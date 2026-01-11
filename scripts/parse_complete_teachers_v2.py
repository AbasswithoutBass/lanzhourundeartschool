#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整解析 teacher-liest 文件，生成 teachers.json
使用改进的两阶段解析方法
"""

import json
import re
from pathlib import Path

def fix_typos(text):
    """修正文本中的错别字和格式问题"""
    corrections = {
        "口盖碗": "喝口盖碗",
        "巴邮鼓": "巴郎鼓",
        "聼暮": "参加",
        "三州": "兰州",
        "业于": "毕业于",
        "那从育年中音纪秀杰": "师从青年男中音纪秀杰",
        "表年里中音": "青年男中音",
        "表年里中亲": "青年男中音",
        "表年亲乐家": "青年音乐家",
        "竞乐家": "音乐家",
        "唢级债承人": "唢呐传承人",
        "州产乐": "音乐厅",
        "字院": "学院",
        "交喻乐团": "交响乐团",
        "十剧院": "大剧院",
        "李老师": "李红老师",
        "青年择果克产": "青年男高音",
        "中国传统立化年歌限安学卡": "中国传统文化促进会青年歌唱家学术委员会",
        "审团特将": "评审团特别奖",
        "新第十二届国南乐": "新加坡第十二届中新国际音乐比赛",
        "中联决": "大型",
        "编创井参演": "编创并参演",
        "念": "舞蹈",
        "文华迁动会国总网演志主业则发采局支": "文化和旅游部人才中心全国总展演最佳展演者",
        "鸡家学术委员会业务老核中": "中国青年歌唱家学术委员会业务考核",
        "硕士业奖学金": "硕士研究生学业奖学金",
        "吴极巧": "吴吉巧",
        "中Sin": "中新",
        "中公": "中共",
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    return text

def extract_achievements(bio):
    """从简介中提取获奖情况"""
    achievements = []
    bio_without_achievements = bio
    
    # 查找"获奖情况"、"获奖作品"、"获奖："等标记
    patterns = [
        r'获奖情况[：:]\s*(.+?)(?=\n[A-Za-z\u4e00-\u9fa5]{2,4}\n|\Z)',
        r'获奖作品[：:]\s*(.+?)(?=\n[A-Za-z\u4e00-\u9fa5]{2,4}\n|\Z)',
        r'获奖[：:]\s*(.+?)(?=\n[A-Za-z\u4e00-\u9fa5]{2,4}\n|\Z)',
        r'曾获奖项[：:]\s*(.+?)(?=\n[A-Za-z\u4e00-\u9fa5]{2,4}\n|\Z)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, bio, re.DOTALL)
        if match:
            achievement_text = match.group(1).strip()
            # 分割成多个奖项（按句号或换行）
            achievement_lines = [line.strip() for line in re.split(r'[。\n]', achievement_text) if line.strip()]
            achievements.extend(achievement_lines)
            # 从bio中移除获奖部分
            bio_without_achievements = bio[:match.start()] + bio[match.end():]
            break
    
    return achievements, bio_without_achievements.strip()

def parse_teachers_file(filepath):
    """解析教师列表文件 - 改进版本"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正错字
    content = fix_typos(content)
    
    # 第一步：分割成部门块
    # 使用正则表达式找出所有部门标识的位置
    dept_pattern = r'(管理部：|声乐组|器乐组|理论组教师|舞蹈部)'
    dept_positions = []
    
    for match in re.finditer(dept_pattern, content):
        dept_name = match.group(1).replace('：', '').replace('教师', '')
        dept_positions.append((match.start(), match.end(), dept_name))
    
    # 按部门分割内容
    department_blocks = []
    for i, (start, end, dept_name) in enumerate(dept_positions):
        # 找到下一个部门的开始位置
        next_start = dept_positions[i + 1][0] if i + 1 < len(dept_positions) else len(content)
        
        # 提取该部门的内容（从部门标识结束到下一个部门开始）
        block_content = content[end:next_start].strip()
        department_blocks.append((dept_name, block_content))
    
    # 第二步：解析每个部门的教师信息
    teachers = []
    teacher_id = 1
    seen_teachers = set()  # 用于去重（同一个人可能在多个部门）
    
    for dept_name, block_content in department_blocks:
        lines = block_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            # 跳过说明性文字
            if line.startswith('我觉得') or line.startswith('按这个顺序'):
                i += 1
                continue
            
            # 检查是否是"姓名 部门标识"的组合（如"管民 器乐组"）
            name_dept_match = re.match(r'^([A-Za-z\u4e00-\u9fa5]{2,10})\s+(器乐组|声乐组|理论组)$', line)
            if name_dept_match:
                name = name_dept_match.group(1)
                # 这种情况下部门标识在姓名后，跳过处理，因为已经在当前块中
                i += 1
            # 判断是否是教师姓名（2-10个字符，纯中文或字母，不包含职位关键词）
            elif (len(line) >= 2 and len(line) <= 10 and 
                  re.match(r'^[A-Za-z\u4e00-\u9fa5：]+$', line) and
                  not any(keyword in line for keyword in ['教师', '顾问', '创始人', '组', '部'])):
                
                name = line.strip()
                # 移除姓名后的冒号（如"苏海鹏："）
                name = name.rstrip('：')
                
                # 特殊处理：陈璞东（可能分两行）
                if name == '陈璞' and i + 1 < len(lines) and lines[i + 1].strip() == '东':
                    name = '陈璞东'
                    i += 1
                
                # 读取职位（下一行）
                i += 1
                if i >= len(lines):
                    break
                
                position = lines[i].strip()
                
                # 检查职位是否合理（不能太长，应该包含职位关键词）
                position_keywords = ['教师', '顾问', '创始人', '校长', '主管', '总监', '名师']
                has_position_keyword = any(kw in position for kw in position_keywords)
                
                # 如果职位看起来不像职位，可能这不是教师条目
                if len(position) > 100 or not has_position_keyword:
                    # 可能是误判，回退
                    i -= 1
                    i += 1
                    continue
                
                # 读取简介（多行，直到遇到下一个教师名）
                i += 1
                bio_lines = []
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    if not next_line:
                        i += 1
                        continue
                    
                    # 检查是否是新教师（短行 + 后面跟职位）
                    if (len(next_line) >= 2 and len(next_line) <= 10 and 
                        i + 1 < len(lines)):
                        potential_position = lines[i + 1].strip()
                        if any(keyword in potential_position for keyword in ['教师', '顾问', '创始人', '校长', '主管', '总监', '名师']):
                            # 这是新教师，停止收集bio
                            break
                    
                    bio_lines.append(next_line)
                    i += 1
                
                # 合并简介
                bio = '\n'.join(bio_lines).strip()
                
                # 如果bio为空或太短，跳过
                if not bio or len(bio) < 20:
                    continue
                
                # 提取获奖情况
                achievements, bio_clean = extract_achievements(bio)
                
                # 生成简短摘要
                short_summary = bio_clean[:100] + '...' if len(bio_clean) > 100 else bio_clean
                
                # 确定照片路径
                photo = f"assets/images/teachers/{name}.jpg"
                
                # 创建唯一标识（姓名+部门）
                teacher_key = f"{name}_{dept_name}"
                
                # 检查是否已存在（避免重复）
                if teacher_key in seen_teachers:
                    continue
                
                seen_teachers.add(teacher_key)
                
                # 创建教师对象
                teacher = {
                    "id": teacher_id,
                    "name": name,
                    "department": dept_name,
                    "position": position,
                    "shortSummary": short_summary,
                    "photo": photo,
                    "bio": bio_clean if bio_clean else bio,
                    "achievements": achievements
                }
                
                teachers.append(teacher)
                teacher_id += 1
                continue
            
            i += 1
    
    return teachers

def main():
    """主函数"""
    # 文件路径
    input_file = Path("/Volumes/唱不上低音的Bass的J.ZAO KP SERIES 2TB SSD Media 1/下载/润德公众号/teacher-liest")
    output_file = Path("/Volumes/唱不上低音的Bass的J.ZAO KP SERIES 2TB SSD Media 1/下载/润德公众号/data/teachers.json")
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 解析教师信息
    print("开始解析教师列表...")
    teachers = parse_teachers_file(input_file)
    
    # 统计各部门人数
    dept_stats = {}
    for teacher in teachers:
        dept = teacher['department']
        dept_stats[dept] = dept_stats.get(dept, 0) + 1
    
    # 保存到JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(teachers, f, ensure_ascii=False, indent=2)
    
    # 输出统计信息
    print(f"\n✅ 成功创建 {len(teachers)} 位教师的数据库")
    print("\n各部门分布：")
    for dept in ['管理部', '声乐组', '器乐组', '理论组', '舞蹈部']:
        count = dept_stats.get(dept, 0)
        print(f"  {dept}: {count}人")
    
    # 显示前5位和后5位教师
    print("\n前5位教师：")
    for i, teacher in enumerate(teachers[:5], 1):
        print(f"{i}. {teacher['name']} - {teacher['department']} - {teacher['position']}")
    
    print("\n后5位教师：")
    for i, teacher in enumerate(teachers[-5:], len(teachers)-4):
        print(f"{i}. {teacher['name']} - {teacher['department']} - {teacher['position']}")
    
    # 显示每个部门的前几位教师
    print("\n各部门教师示例：")
    for dept in ['管理部', '声乐组', '器乐组', '理论组', '舞蹈部']:
        dept_teachers = [t for t in teachers if t['department'] == dept]
        if dept_teachers:
            print(f"\n{dept} ({len(dept_teachers)}人):")
            for teacher in dept_teachers[:3]:
                print(f"  - {teacher['name']} ({teacher['position']})")
    
    print(f"\n数据已保存到: {output_file}")

if __name__ == "__main__":
    main()
