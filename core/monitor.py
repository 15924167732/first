"""
FF14战斗分析器 - 实时监控类
"""

import os
import time
import threading
from datetime import datetime
from collections import defaultdict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analyzer import ACTLogAnalyzer
from utils.constants import JOB_NAMES, LOG_TYPE_ADD_ENTITY, LOG_TYPE_ABILITY, LOG_TYPE_DEATH, LOG_TYPE_COMBAT_STATUS, LOG_TYPE_ZONE_CHANGE


class RealtimeMonitor:
    """实时监控类"""
    
    def __init__(self, log_file_path: str, callback):
        self.log_file_path = log_file_path
        self.callback = callback
        self.analyzer = ACTLogAnalyzer()
        self.is_running = False
        self.file_position = 0
        self.monitor_thread = None
        
        # 当前战斗状态
        self.current_zone = "未知区域"
        self.in_combat = False
        self.fight_number = 0
        self.combat_start_time = None
        self.player_damage = defaultdict(int)
        self.player_healing = defaultdict(int)
        self.death_events = []
        self.player_info = {}
    
    def start(self):
        """启动监控"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 初始化文件位置
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(0, 2)
                self.file_position = f.tell()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.in_combat:
            self._end_current_fight()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                if not os.path.exists(self.log_file_path):
                    time.sleep(1)
                    continue
                
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    f.seek(self.file_position)
                    new_lines = f.readlines()
                    self.file_position = f.tell()
                
                if new_lines:
                    for line in new_lines:
                        self._process_line(line)
                
                time.sleep(0.5)
            
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(1)
    
    def _process_line(self, line: str):
        """处理单行日志"""
        line = line.strip()
        if not line:
            return
        
        parts = line.split('|')
        if len(parts) < 3:
            return
        
        log_type = parts[0]
        timestamp_str = parts[1]
        
        try:
            timestamp = self.analyzer.parse_timestamp(timestamp_str)
        except:
            return
        
        # 265行: 副本区域
        if log_type == LOG_TYPE_ZONE_CHANGE and len(parts) >= 5 and parts[4] == 'True':
            if len(parts) >= 4:
                new_zone = parts[3]
                if new_zone != self.current_zone:
                    self.current_zone = new_zone
        
        # 03行: 添加实体
        elif log_type == LOG_TYPE_ADD_ENTITY:
            if len(parts) >= 5:
                entity_id = parts[2]
                job_id_str = parts[4]
                
                if entity_id.startswith('10'):
                    try:
                        job_id = int(job_id_str, 16)
                        if job_id in JOB_NAMES:
                            self.analyzer.player_jobs[entity_id] = JOB_NAMES[job_id]
                    except ValueError:
                        pass
        
        # 260行: 进战状态
        elif log_type == LOG_TYPE_COMBAT_STATUS:
            if len(parts) >= 6:
                id2=parts[2]
                in_game_combat = parts[3]
                id4=parts[4]
                is_game_changed = parts[5]
                
                # 进战
                if in_game_combat == '1' and is_game_changed == '1':
                    if not self.in_combat:
                        self._start_new_fight(timestamp)
                
                # 脱战
                elif in_game_combat == '0' and is_game_changed == '0' and id2 == '0' and id4 == '1':
                    if self.in_combat:
                        self._end_current_fight()
        
        # 处理技能和死亡
        elif log_type in LOG_TYPE_ABILITY:
            if self.in_combat and len(parts) >= 11:
                self._process_ability(parts)
        
        elif log_type == LOG_TYPE_DEATH:
            if self.in_combat and len(parts) >= 5:
                self._process_death(parts, timestamp)
    
    def _start_new_fight(self, timestamp):
        """开始新战斗"""
        self.in_combat = True
        self.fight_number += 1
        self.combat_start_time = timestamp
        self.player_damage = defaultdict(int)
        self.player_healing = defaultdict(int)
        self.death_events = []
        self.player_info = {}
        self.analyzer.last_death_ability = {}
    
    def _end_current_fight(self):
        """结束当前战斗"""
        if not self.combat_start_time:
            return
        
        self.in_combat = False
        end_time = datetime.now()
        
        # 获取最终的战斗数据快照
        final_fight_data = self._get_final_fight_data(end_time)
        
        # 保存到analyzer
        self.analyzer._save_fight(
            self.current_zone,
            self.combat_start_time,
            end_time,
            self.player_damage,
            self.player_healing,
            self.death_events,
            self.player_info,
            end_time.isoformat() + '+08:00'
        )
        
        # 通知UI更新
        if self.callback:
            self.callback('fight_end', final_fight_data)
    
    def _update_current_fight(self):
        """更新当前战斗数据（事件驱动）"""
        if self.callback:
            self.callback('fight_update', self._get_current_fight_data())
    
    def _get_current_fight_data(self):
        """获取当前战斗数据（实时更新）"""
        if not self.combat_start_time:
            return None
        
        end_time = datetime.now()
        return self._get_final_fight_data(end_time)
    
    def _get_final_fight_data(self, end_time):
        """获取最终战斗数据（指定结束时间）"""
        if not self.combat_start_time:
            return None
        
        duration_seconds = (end_time - self.combat_start_time).total_seconds()
        
        if duration_seconds <= 0:
            duration_seconds = 1
        
        # 构建临时战斗数据
        damage_done = []
        total_damage = sum(self.player_damage.values())
        
        for player_id, damage in self.player_damage.items():
            player_name = self.player_info.get(player_id, f"Unknown_{player_id}")
            player_job = self.analyzer.player_jobs.get(player_id, "Unknown")
            dps = round(damage / duration_seconds, 2)
            percent = round((damage / total_damage * 100), 2) if total_damage > 0 else 0
            
            damage_done.append({
                "name": player_name,
                "type": player_job,
                "total": damage,
                "dps": dps,
                "percent": percent
            })
        
        damage_done.sort(key=lambda x: x['total'], reverse=True)
        
        # 类似处理治疗数据
        healing_done = []
        total_healing = sum(self.player_healing.values())
        
        for player_id, healing in self.player_healing.items():
            player_name = self.player_info.get(player_id, f"Unknown_{player_id}")
            player_job = self.analyzer.player_jobs.get(player_id, "Unknown")
            hps = round(healing / duration_seconds, 2)
            percent = round((healing / total_healing * 100), 2) if total_healing > 0 else 0
            
            healing_done.append({
                "name": player_name,
                "type": player_job,
                "total": healing,
                "hps": hps,
                "percent": percent
            })
        
        healing_done.sort(key=lambda x: x['total'], reverse=True)
        
        # 统计每个玩家的死亡次数
        player_deaths = defaultdict(int)
        for death_event in self.death_events:
            player_id = death_event.get('id')
            if player_id:
                player_deaths[player_id] += 1
        
        return {
            'zone': self.current_zone,
            'fight_id': self.fight_number,
            'duration': int(duration_seconds),
            'damage_done': damage_done,
            'healing_done': healing_done,
            'death_events': self.death_events.copy(),
            'player_damage': dict(self.player_damage),
            'player_healing': dict(self.player_healing),
            'player_deaths': dict(player_deaths),
            'player_info': dict(self.player_info),
            'player_jobs': dict(self.analyzer.player_jobs)
        }
    
    def _process_ability(self, parts):
        """处理技能日志"""
        source_id = parts[2]
        source_name = parts[3]
        ability_id = parts[4]
        ability_name = parts[5]
        target_id = parts[6]
        target_name = parts[7]
        
        if source_id.startswith('10') and source_id not in self.player_info:
            self.player_info[source_id] = source_name
        if target_id.startswith('10') and target_id not in self.player_info:
            self.player_info[target_id] = target_name
        
        # 标记是否有数据变化
        has_damage_or_healing = False
        
        for i in range(8):
            flags_idx = 8 + i * 2
            damage_idx = 9 + i * 2
            
            if len(parts) <= damage_idx:
                break
            
            flags = parts[flags_idx]
            damage_hex = parts[damage_idx]
            
            if not flags or flags == '0':
                continue
            
            try:
                if flags[-1] == '3':
                    if source_id.startswith('10'):
                        damage = self.analyzer.parse_damage(damage_hex, flags)
                        if damage > 0:
                            self.player_damage[source_id] += damage
                            has_damage_or_healing = True  # 检测到伤害
                    
                    if target_id.startswith('10'):
                        self.analyzer.last_death_ability[target_id] = {
                            'ability_id': ability_id,
                            'ability_name': ability_name
                        }
                
                elif flags[-1] == '4':
                    if source_id.startswith('10') and target_id.startswith('10'):
                        healing = self.analyzer.parse_damage(damage_hex, flags)
                        if healing > 0:
                            self.player_healing[source_id] += healing
                            has_damage_or_healing = True  # 检测到治疗
            except:
                pass
        
        # 如果检测到伤害或治疗，立即刷新界面
        if has_damage_or_healing and self.in_combat:
            self._update_current_fight()
    
    def _process_death(self, parts, timestamp):
        """处理死亡日志"""
        target_id = parts[2]
        target_name = parts[3]
        if target_id.startswith('10'):
            death_time_ms = int((timestamp - self.combat_start_time).total_seconds() * 1000)
            
            death_event = {
                "name": target_name,
                "id": target_id,
                "deathTime": death_time_ms
            }
            
            if target_id in self.analyzer.last_death_ability:
                ability_info = self.analyzer.last_death_ability[target_id]
                death_event["ability"] = {
                    "name": ACTLogAnalyzer.clean_ability_name(ability_info['ability_name'], ability_info['ability_id']),
                    "guid": ability_info['ability_id']
                }
            
            self.death_events.append(death_event)
            
            # 检测到死亡事件，立即刷新界面
            if self.in_combat:
                self._update_current_fight()
