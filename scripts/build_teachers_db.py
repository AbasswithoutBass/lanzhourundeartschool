#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照 teacher-liest 原始文件构建完整教师数据库
数据按部门组织：管理部 → 舞蹈部 → 声乐组 → 器乐组
生成 data/teachers.json （完整结构化数据）
"""

import json
import re
from pathlib import Path

def parse_teachers_from_file(filepath):
    """从 teacher-liest 文件解析教师数据"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    teachers = []
    teacher_id_counter = 1
    
    # 使用正则表达式分割部门
    dept_sections = re.split(r'(管理部：|舞蹈部|声乐组|器乐组)', content)
    
    current_dept = None
    current_position = None
    current_name = None
    current_bio = ""
    current_achievements = []
    
    for i, section in enumerate(dept_sections):
        if section in ['管理部：', '舞蹈部', '声乐组', '器乐组']:
            # 保存之前的教师
            if current_name:
                teacher = create_teacher_object(
                    teacher_id_counter, current_name, current_dept, 
                    current_position, current_bio, current_achievements
                )
                teachers.append(teacher)
                teacher_id_counter += 1
                current_name = None
                current_bio = ""
                current_achievements = []
            
            current_dept = section.replace('：', '')
            continue
        
        if not section.strip() or not current_dept:
            continue
        
        # 按换行分割内容
        lines = section.strip().split('\n')
        j = 0
        while j < len(lines):
            line = lines[j].strip()
            if not line:
                j += 1
                continue
            
            # 检查是否是新的教师条目（名字行）
            if j + 1 < len(lines):
                next_line = lines[j + 1].strip()
                # 如果下一行看起来像职位（含"教师"、"校长"、"顾问"等）
                if any(title in next_line for title in ['教师', '校长', '主管', '监', '顾问', '总监', '执行']):
                    # 保存之前的教师
                    if current_name:
                        teacher = create_teacher_object(
                            teacher_id_counter, current_name, current_dept,
                            current_position, current_bio, current_achievements
                        )
                        teachers.append(teacher)
                        teacher_id_counter += 1
                    
                    current_name = line
                    current_position = next_line
                    current_bio = ""
                    current_achievements = []
                    j += 2
                    continue
            
            # 收集简介和成就信息
            if current_name:
                if '获奖' in line or '获得' in line or '荣获' in line:
                    # 开始收集成就
                    if line and '：' in line:
                        achievement_part = line.split('：', 1)[1]
                        if achievement_part:
                            current_achievements.append(achievement_part)
                    else:
                        current_achievements.append(line)
                else:
                    if current_bio:
                        current_bio += "\n" + line
                    else:
                        current_bio = line
            
            j += 1
    
    # 保存最后一个教师
    if current_name:
        teacher = create_teacher_object(
            teacher_id_counter, current_name, current_dept,
            current_position, current_bio, current_achievements
        )
        teachers.append(teacher)
    
    return teachers

def create_teacher_object(idx, name, department, position, bio, achievements):
    """创建标准的教师对象"""
    # 生成 ID（部门缩写 + 序号）
    dept_map = {'管理部': 'admin', '舞蹈部': 'dance', '声乐组': 'vocal', '器乐组': 'instrumental'}
    dept_abbr = dept_map.get(department, 'teacher')
    teacher_id = f"{dept_abbr}_{idx:03d}"
    
    # 从简介中提取短摘要（前100字）
    short_summary = bio[:100].replace('\n', ' ') if bio else position
    
    return {
        "id": teacher_id,
        "name": name,
        "department": department,
        "position": position,
        "shortSummary": short_summary,
        "photo": f"photos/{name}.jpg",
        "bio": bio,
        "achievements": achievements
    }

def save_teachers_json(teachers, output_path):
    """保存教师数据到 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(teachers, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 {output_path}")
    print(f"📊 教师总数: {len(teachers)}")
    
    # 按部门统计
    dept_stats = {}
    for teacher in teachers:
        dept = teacher['department']
        dept_stats[dept] = dept_stats.get(dept, 0) + 1
    
    print("\n按部门分布:")
    for dept, count in sorted(dept_stats.items()):
        print(f"  {dept}: {count}人")

if __name__ == '__main__':
    input_file = Path('/Volumes/唱不上低音的Bass的J.ZAO KP SERIES 2TB SSD Media 1/润德/网页/teacher-liest')
    output_file = Path('/Volumes/唱不上低音的Bass的J.ZAO KP SERIES 2TB SSD Media 1/润德/网页/data/teachers.json')
    
    teachers = parse_teachers_from_file(input_file)
    save_teachers_json(teachers, output_file)
