"""
FF14战斗分析器 - ACT日志分析核心类
"""

from datetime import datetime
from collections import defaultdict
from typing import Dict, List
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import JOB_NAMES, LOG_TYPE_ADD_ENTITY, LOG_TYPE_ABILITY, LOG_TYPE_DEATH, LOG_TYPE_COMBAT_STATUS, LOG_TYPE_ZONE_CHANGE


class ACTLogAnalyzer:
    """ACT日志分析核心类"""
    
    @staticmethod
    def clean_ability_name(name: str, id: str) -> str:
        """清理技能名称"""
        if id == "844B":
            return "坠机"
        if name.startswith("_rsv_"):
            return "aoe"
        if name.startswith("unk"):
            return "攻击"
        return name
    
    def __init__(self):
        self.reports = {}
        self.player_jobs = {}
        self.last_death_ability = {}
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析时间戳"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('+08:00', ''))
        except:
            return datetime.now()
    
    def get_or_create_report(self, zone_name: str) -> Dict:
        """获取或创建指定副本的report"""
        if zone_name not in self.reports:
            self.reports[zone_name] = {
                'fights': [],
                'start_time': None,
                'end_time': None,
                'first_timestamp': None,
                'fight_count': 0
            }
        return self.reports[zone_name]
    
    def parse_damage(self, damage_hex: str, flags: str) -> int:
        """解析伤害值"""
        if not damage_hex or damage_hex == '0':
            return 0
        
        try:
            damage_hex = damage_hex.upper().zfill(8)
            
            if len(damage_hex) >= 6:
                byte_c = damage_hex[4:6]
                if byte_c == '40':
                    byte_a = damage_hex[0:2]
                    byte_b = damage_hex[2:4]
                    byte_d = damage_hex[6:8]
                    actual_damage_hex = byte_d + byte_a + byte_b
                    return int(actual_damage_hex, 16)
            
            damage = int(damage_hex[0:4], 16)
            return damage
        except ValueError:
            return 0
    
    def analyze_log_file(self, log_file_path: str, progress_callback=None) -> List[Dict]:
        """分析整个日志文件（离线分析）
        
        Args:
            log_file_path: 日志文件路径
            progress_callback: 进度回调函数，接收两个参数：current, total
        
        Returns:
            分析结果列表
        """
        self.reports = {}
        self.player_jobs = {}
        self.last_death_ability = {}
        
        current_zone = "未知区域"
        in_combat = False
        combat_start_time = None
        player_damage = defaultdict(int)
        player_healing = defaultdict(int)
        death_events = []
        player_info = {}
        
        # 计算文件总行数
        total_lines = 0
        if progress_callback:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for _ in f)
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            current_line = 0
            for line in f:
                current_line += 1
                
                # 每处理100行更新一次进度
                if progress_callback and total_lines > 0 and current_line % 100 == 0:
                    progress_callback(current_line, total_lines)
                
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) < 3:
                    continue
                
                log_type = parts[0]
                timestamp_str = parts[1]
                
                try:
                    timestamp = self.parse_timestamp(timestamp_str)
                except:
                    continue
                
                # 265行: 副本区域
                if log_type == LOG_TYPE_ZONE_CHANGE and len(parts) >= 5 and parts[4] == 'True':
                    if len(parts) >= 4:
                        new_zone = parts[3]
                        if new_zone != current_zone:
                            current_zone = new_zone
                
                # 03行: 添加实体
                elif log_type == LOG_TYPE_ADD_ENTITY:
                    if len(parts) >= 5:
                        entity_id = parts[2]
                        job_id_str = parts[4]
                        
                        if entity_id.startswith('10'):
                            try:
                                job_id = int(job_id_str, 16)
                                if job_id in JOB_NAMES:
                                    self.player_jobs[entity_id] = JOB_NAMES[job_id]
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
                            if not in_combat:
                                in_combat = True
                                combat_start_time = timestamp
                                player_damage = defaultdict(int)
                                player_healing = defaultdict(int)
                                death_events = []
                                player_info = {}
                                self.last_death_ability = {}
                                
                                current_report = self.get_or_create_report(current_zone)
                                
                                if current_report['first_timestamp'] is None:
                                    current_report['first_timestamp'] = timestamp
                                    current_report['start_time'] = timestamp.isoformat() + '+08:00'
                        
                        # 脱战
                        elif in_game_combat == '0' and is_game_changed == '0' and id2 == '0' and id4 == '1':
                            if in_combat:
                                in_combat = False
                                if combat_start_time:
                                    self._save_fight(current_zone, combat_start_time,
                                                   timestamp, player_damage, player_healing,
                                                   death_events, player_info, timestamp_str)
                
                # 21/22行: 技能
                elif log_type in LOG_TYPE_ABILITY:
                    if in_combat and len(parts) >= 11:
                        source_id = parts[2]
                        source_name = parts[3]
                        ability_id = parts[4]
                        ability_name = parts[5]
                        target_id = parts[6]
                        target_name = parts[7]
                        
                        if source_id.startswith('10') and source_id not in player_info:
                            player_info[source_id] = source_name
                        if target_id.startswith('10') and target_id not in player_info:
                            player_info[target_id] = target_name
                        
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
                                        damage = self.parse_damage(damage_hex, flags)
                                        if damage > 0:
                                            player_damage[source_id] += damage
                                    
                                    if target_id.startswith('10'):
                                        self.last_death_ability[target_id] = {
                                            'ability_id': ability_id,
                                            'ability_name': ability_name
                                        }
                                
                                elif flags[-1] == '4':
                                    if source_id.startswith('10') and target_id.startswith('10'):
                                        healing = self.parse_damage(damage_hex, flags)
                                        if healing > 0:
                                            player_healing[source_id] += healing
                            except:
                                pass
                
                # 25行: 死亡
                elif log_type == LOG_TYPE_DEATH:
                    if in_combat and len(parts) >= 5:
                        target_id = parts[2]
                        target_name = parts[3]
                        if target_id.startswith('10'):
                            death_time_ms = int((timestamp - combat_start_time).total_seconds() * 1000)
                            
                            death_event = {
                                "name": target_name,
                                "id": target_id,
                                "deathTime": death_time_ms
                            }
                            
                            if target_id in self.last_death_ability:
                                ability_info = self.last_death_ability[target_id]
                                death_event["ability"] = {
                                    "name": self.clean_ability_name(ability_info['ability_name'], ability_info['ability_id']),
                                    "guid": ability_info['ability_id']
                                }
                            
                            death_events.append(death_event)
        
        # 处理最后一场战斗
        if in_combat and combat_start_time:
            self._save_fight(current_zone, combat_start_time,
                           datetime.now(), player_damage, player_healing,
                           death_events, player_info, datetime.now().isoformat() + '+08:00')
        
        return self._generate_reports()
    
    def _build_player_stats(self, player_data: Dict, player_info: Dict, 
                            duration_seconds: float, stat_type: str = 'damage') -> List[Dict]:
        """构建玩家统计数据（伤害或治疗）"""
        stats_list = []
        total = sum(player_data.values())
        rate_key = 'dps' if stat_type == 'damage' else 'hps'
        
        for player_id, value in player_data.items():
            player_name = player_info.get(player_id, f"Unknown_{player_id}")
            player_job = self.player_jobs.get(player_id, "Unknown")
            rate = round(value / duration_seconds, 2)
            percent = round((value / total * 100), 2) if total > 0 else 0
            
            stats_list.append({
                "name": player_name,
                "id": player_id,
                "type": player_job,
                "icon": player_job,
                "total": value,
                rate_key: rate,
                "percent": percent
            })
        
        stats_list.sort(key=lambda x: x['total'], reverse=True)
        return stats_list
    
    def _save_fight(self, zone_name: str, start_time: datetime, 
                    end_time: datetime, player_damage: Dict, player_healing: Dict,
                    death_events: List, player_info: Dict, end_time_str: str):
        """保存战斗数据"""
        current_report = self.get_or_create_report(zone_name)
        
        current_report['fight_count'] += 1
        fight_id = current_report['fight_count']
        
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        duration_seconds = max((end_time - start_time).total_seconds(), 1)
        
        if current_report['first_timestamp'] is None:
            current_report['first_timestamp'] = start_time
            current_report['start_time'] = start_time.isoformat() + '+08:00'
        
        first_timestamp = current_report['first_timestamp']
        start_time_relative = int((start_time - first_timestamp).total_seconds() * 1000)
        end_time_relative = int((end_time - first_timestamp).total_seconds() * 1000)
        
        damage_done = self._build_player_stats(player_damage, player_info, duration_seconds, 'damage')
        healing_done = self._build_player_stats(player_healing, player_info, duration_seconds, 'healing')
        
        for death_event in death_events:
            player_id = death_event['id']
            player_job = self.player_jobs.get(player_id, "Unknown")
            death_event['type'] = player_job
            death_event['icon'] = player_job
        
        death_events.sort(key=lambda x: x['deathTime'])
        
        fight_data = {
            "id": fight_id,
            "name": f"战斗 {fight_id}",
            "startTime": start_time_relative,
            "endTime": end_time_relative,
            "duration": duration_ms,
            "damageDone": damage_done,
            "healingDone": healing_done,
            "deathEvents": death_events
        }
        
        current_report['fights'].append(fight_data)
        current_report['end_time'] = end_time_str
    
    def _generate_reports(self) -> List[Dict]:
        """生成所有副本的报告"""
        reports = []
        
        for zone_name, report_data in self.reports.items():
            report = {
                "data": {
                    "reportData": {
                        "report": {
                            "title": zone_name,
                            "startTime": report_data['start_time'] if report_data['start_time'] else "",
                            "endTime": report_data['end_time'] if report_data['end_time'] else "",
                            "fights": report_data['fights']
                        }
                    }
                }
            }
            reports.append(report)
        
        return reports
