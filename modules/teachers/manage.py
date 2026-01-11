#!/usr/bin/env python3
"""teachers.json 管理工具（支持“一人多岗/跨部门” + teacher-liest 顺序同步）

数据格式（v2，推荐）：
    [
        {
            "id": "chen_tao",
            "name": "陈涛",
            "photo": "photos/chen_tao.jpg",
            "shortSummary": "...可选...",
            "bio": "...",
            "achievements": [],
            "roles": [
                {"department": "管理部", "position": "创始人", "order": 1},
                {"department": "声乐组", "position": "声乐教师", "order": 20}
            ]
        }
    ]

兼容旧格式（v1）：顶层数组元素包含 department/position 字段。工具会在内存中自动升级为 v2。

常用命令：
    python modules/teachers/manage.py list
    python modules/teachers/manage.py validate
    python modules/teachers/manage.py sync-from-liest --write
    python modules/teachers/manage.py add-person --name "张三" --photo "photos/placeholder.jpg"
    python modules/teachers/manage.py add-role --name "张三" --department "声乐组" --position "声乐教师" --order 999
"""
import argparse
import json
import os
import shutil
import datetime
import re


DEPT_CANON = {
    '管理部': '管理部',
    '舞蹈部': '舞蹈部',
    '声乐组': '声乐组',
    '器乐组': '器乐组',
    '理论组教师': '理论组',
    '理论组': '理论组',
}

# 管理部显示顺序（强制覆盖 roles[].order）
MGMT_ORDER = [
    '陈涛', '苏海鹏', '王玉', '韩刚', '李甜', '秦淼娜', '祁军霞', '景想东', '苏海震'
]

# 姓名修正/别名映射（teacher-liest 或历史数据里出现的误写）
NAME_ALIASES = {
    '陈璞东': '陈璞',
}

ROLE_HINTS = (
    '教师', '校长', '总监', '主管', '顾问', '名师', '创始人', '团长', '执行校长',
    '主任', '副主任', '副教授', '教授', '讲师', '外聘', '特聘',
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(ROOT, 'data', 'teachers.json')
TODO_PATH = os.path.join(ROOT, 'todo.txt')


def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return normalize_data(data)


def normalize_data(data):
    """将 v1 数据（department/position 在顶层）升级为 v2（roles 数组）。"""
    if not isinstance(data, list):
        return data
    if not data:
        return data

    # v2: roles 字段存在
    if isinstance(data[0], dict) and 'roles' in data[0]:
        for t in data:
            # 确保 roles 的字段齐全
            t.setdefault('roles', [])
            t.setdefault('achievements', [])
            t.setdefault('bio', '')
            t.setdefault('photo', 'photos/placeholder.jpg')
            # shortSummary 可选
        return data

    # v1: 扁平 department/position
    upgraded = []
    for idx, t in enumerate(data):
        if not isinstance(t, dict):
            continue
        upgraded.append({
            'id': t.get('id') or f'legacy_{idx+1:03d}',
            'name': t.get('name') or '',
            'photo': t.get('photo') or 'photos/placeholder.jpg',
            'shortSummary': t.get('shortSummary', ''),
            'bio': t.get('bio') or '',
            'achievements': t.get('achievements') or [],
            'roles': [
                {
                    'department': t.get('department') or '',
                    'position': t.get('position') or '',
                    'order': idx + 1,
                }
            ],
        })
    return upgraded


def write_data(data, path=DATA_PATH):
    # backup
    if os.path.exists(path):
        bak = path + '.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        shutil.copy2(path, bak)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_todo(line):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f"{ts} — {line} — by manage.py\n"
    with open(TODO_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)


def canonical_id(name):
    # 生成基于拼音/拼写的简易 id（保守处理：字母与下划线）
    # 这里只做 ASCII 转换的简单替换：空格->下划线，非字母数字删除
    s = name.replace(' ', '_')
    s = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff-]", '', s)
    s = s.lower()
    return s


def norm_line(s: str) -> str:
    s = (s or '').replace('\u3000', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def clean_dept(s: str) -> str:
    s = norm_line(s).strip('：:')
    return DEPT_CANON.get(s, s)


def normalize_dept_by_position(dept: str | None, position: str | None) -> str | None:
    """把“理论组”从器乐组里拎出来：按岗位文本做归类修正。"""
    if not dept:
        return dept
    d = clean_dept(dept)
    p = norm_line(position or '')
    if not p:
        return d

    theory_markers = ('乐理', '视唱', '练耳', '视唱练耳', '音乐理论')
    if any(m in p for m in theory_markers):
        return '理论组'
    return d


def is_dept_line(s: str) -> bool:
    s = clean_dept(s)
    return s in DEPT_CANON.values()


def clean_name(s: str) -> str:
    s = norm_line(s).strip('：:')
    return s.replace(' ', '')


def normalize_name(s: str) -> str:
    n = clean_name(s)
    return NAME_ALIASES.get(n, n)


def normalize_position(position: str | None) -> str | None:
    if position is None:
        return None
    p = norm_line(position)
    if not p:
        return None

    # 去掉来源文本里的冗余前缀
    for prefix in ('兰州润德艺考', '兰州润德艺术学校', '兰州润德艺校'):
        if p.startswith(prefix):
            p = p[len(prefix):].strip()

    # 注意：不在这里强制把“名师”改成“教师”。
    # 去重时会将“名师/教师”视作同一专业并优先保留“名师”。
    # 进一步把“X声乐教师”之类保持原样；不做过度标准化
    return p


def position_dedupe_key(position: str | None) -> str:
    p = normalize_position(position) or ''
    if p.endswith('名师'):
        return p[:-2] + '教师'
    return p


def looks_like_name(s: str) -> bool:
    s = clean_name(s)
    if not s:
        return False
    if any(k in s for k in ROLE_HINTS):
        return False
    if len(s) < 2 or len(s) > 5:
        return False
    return re.fullmatch(r'[\u4e00-\u9fff·]{2,5}', s) is not None


def stitch_lines(lines):
    """修复极少数情况：姓名被拆成两行（例如：陈璞 / 东）。"""
    stitched = []
    i = 0
    while i < len(lines):
        cur = norm_line(lines[i])
        if cur and re.fullmatch(r'[\u4e00-\u9fff]', cur) and stitched:
            prev = stitched[-1]
            if re.fullmatch(r'[\u4e00-\u9fff]{2,4}', prev.replace(' ', '')):
                stitched[-1] = prev.replace(' ', '') + cur
                i += 1
                continue
        stitched.append(cur)
        i += 1
    return stitched


def split_embedded_name_suffixes(lines):
    """修复格式问题：姓名被粘在上一段末尾（例如：'...。肖雪'）。"""
    out = []
    for raw in lines:
        line = norm_line(raw)
        if not line:
            out.append('')
            continue
        m = re.match(r'^(.*?)([。.!?；;，,、])([\u4e00-\u9fff·]{2,4})\s*$', line)
        if m:
            prefix, punct, name = m.group(1), m.group(2), m.group(3)
            if len(prefix) >= 12 and looks_like_name(name):
                out.append(norm_line(prefix + punct))
                out.append(name)
                continue
        out.append(line)
    return out


def split_name_dept_inline(line: str):
    """处理少数行里把“姓名 + 部门”写在一行的情况，例如：'管民 器乐组'。"""
    s = norm_line(line)
    if not s:
        return None, None
    for dept in DEPT_CANON.values():
        if dept in s and s.strip('：:') != dept:
            left = s.split(dept, 1)[0]
            name = clean_name(left)
            if looks_like_name(name):
                return name, dept
    return None, None


def parse_teacher_liest(text: str):
    """解析 teacher-liest，输出按出现顺序的 role 列表：
    [{'name','department','position','order'}]
    """
    lines = split_embedded_name_suffixes(text.splitlines())
    lines = stitch_lines(lines)

    dept = None
    order = 0
    roles = []
    for idx, line in enumerate(lines):
        if is_dept_line(line):
            dept = clean_dept(line)
            continue
        if not line:
            continue

        inline_name, inline_dept = split_name_dept_inline(line)
        if inline_name and inline_dept:
            dept = inline_dept
            order += 1
            roles.append({'name': inline_name, 'department': dept, 'position': None, 'order': order})
            continue

        if not looks_like_name(line):
            continue

        # position: next non-empty line if short-ish and not a dept header
        j = idx + 1
        while j < len(lines) and not lines[j]:
            j += 1
        nxt = lines[j] if j < len(lines) else ''
        nxtn = norm_line(nxt)

        # 某些条目在姓名后会重复写一遍部门（例如：童倩影 -> 声乐组 -> 兰州润德艺考声乐教师）
        if nxtn and is_dept_line(nxtn):
            dept = clean_dept(nxtn)
            j += 1
            while j < len(lines) and not lines[j]:
                j += 1
            nxt = lines[j] if j < len(lines) else ''
            nxtn = norm_line(nxt)

        position = None
        if nxtn and (not is_dept_line(nxtn)) and len(nxtn) <= 20:
            # 只有“像职位”的行才认为是有效条目，避免把“中央/获奖情况”等误判为姓名
            if any(k in nxtn for k in ROLE_HINTS):
                position = nxtn
            else:
                # 没有岗位特征就跳过该姓名候选
                continue

        # 没有明确的岗位行（例如长段落续行）一律跳过，避免误判
        if not position:
            continue

        if not dept:
            continue

        position = normalize_position(position)
        dept = normalize_dept_by_position(dept, position)

        order += 1
        roles.append({'name': normalize_name(line), 'department': dept, 'position': position, 'order': order})

    return roles


def find_teacher(data, *, tid=None, name=None):
    for t in data:
        if tid and t.get('id') == tid:
            return t
        if name and t.get('name') == name:
            return t
    return None


def ensure_role(teacher, role):
    teacher.setdefault('roles', [])
    for r in teacher['roles']:
        if r.get('department') == role.get('department') and r.get('position') == role.get('position'):
            # keep earliest order
            if isinstance(role.get('order'), int):
                r['order'] = min(int(r.get('order') or role['order']), role['order'])
            return
    teacher['roles'].append(role)


def normalize_teacher_roles(teacher: dict):
    """规范化 roles（部门/岗位）并去重合并。"""
    raw_roles = teacher.get('roles') or []
    if not isinstance(raw_roles, list):
        teacher['roles'] = []
        return

    # key: (dept, position_dedupe_key)
    merged_map: dict[tuple[str, str], dict] = {}
    for r in raw_roles:
        if not isinstance(r, dict):
            continue
        pos = normalize_position(r.get('position'))
        if not pos:
            continue
        dept = normalize_dept_by_position(r.get('department'), pos)
        if not dept:
            continue
        key = (dept, position_dedupe_key(pos))
        try:
            order = int(r.get('order') or 10**9)
        except Exception:
            order = 10**9

        cur = merged_map.get(key)
        if not cur:
            merged_map[key] = {'department': dept, 'position': pos, 'order': order}
            continue

        # order 取最早出现
        cur['order'] = min(int(cur.get('order') or order), order)

        # 同一专业：优先保留“名师”作为展示头衔
        cur_pos = norm_line(cur.get('position') or '')
        new_pos = norm_line(pos)
        if (not cur_pos.endswith('名师')) and new_pos.endswith('名师'):
            cur['position'] = new_pos

    teacher['roles'] = list(merged_map.values())


def merge_teachers_by_name(data: list[dict]) -> list[dict]:
    """按 normalize_name 合并重复教师条目（保留更完整的信息，合并 roles）。"""
    merged: dict[str, dict] = {}
    for t in data:
        if not isinstance(t, dict):
            continue
        name = normalize_name(t.get('name') or '')
        if not name:
            continue
        t['name'] = name

        # 先把自身 roles 规范化，避免把“未规范化的 role”带进最终结果
        normalize_teacher_roles(t)

        if name not in merged:
            merged[name] = t
            continue

        base = merged[name]

        # photo/bio/summary 取更“像有效值”的那个
        if (not base.get('photo') or 'placeholder' in str(base.get('photo'))) and t.get('photo'):
            base['photo'] = t.get('photo')
        if (not base.get('bio')) and t.get('bio'):
            base['bio'] = t.get('bio')
        if (not base.get('shortSummary')) and t.get('shortSummary'):
            base['shortSummary'] = t.get('shortSummary')
        if (not base.get('achievements')) and t.get('achievements'):
            base['achievements'] = t.get('achievements')

        # roles 合并
        for r in (t.get('roles') or []):
            if not isinstance(r, dict):
                continue
            dept = r.get('department')
            pos = normalize_position(r.get('position'))
            if not pos:
                continue
            dept = normalize_dept_by_position(dept, pos)
            ensure_role(base, {'department': dept, 'position': pos, 'order': int(r.get('order') or 10**9)})

    return list(merged.values())


def cmd_list(args):
    data = load_data()
    for t in data:
        roles = t.get('roles') or []
        if not roles:
            print(f"{t.get('id','?')}  {t.get('name','?')}  (无岗位)")
            continue
        for r in sorted(roles, key=lambda x: int(x.get('order') or 10**9)):
            print(
                f"{t.get('id','?')}  {t.get('name','?')}  [{r.get('department','')}] {r.get('position','')}  order={r.get('order','?')}"
            )


def cmd_validate(args):
    try:
        data = load_data()
    except Exception as e:
        print('ERROR: 读取或解析 data/teachers.json 失败:', str(e))
        return 2
    if not isinstance(data, list):
        print('ERROR: data/teachers.json 顶层应为数组')
        return 2
    required = {'id', 'name', 'photo', 'bio', 'achievements', 'roles'}
    ok = True
    ids = set()
    for i, t in enumerate(data):
        if not isinstance(t, dict):
            print(f'项 {i} 不是对象')
            ok = False
            continue
        missing = required - set(t.keys())
        if missing:
            print(f"项 {i} ({t.get('name')}) 缺少字段: {', '.join(missing)}")
            ok = False
        tid = t.get('id')
        if not tid:
            print(f"项 {i} ({t.get('name')}) 缺少 id")
            ok = False
        else:
            if tid in ids:
                print(f"重复 id: {tid}")
                ok = False
            ids.add(tid)

        roles = t.get('roles')
        if not isinstance(roles, list) or not roles:
            print(f"项 {i} ({t.get('name')}) roles 为空或不是数组")
            ok = False
            continue
        for ri, r in enumerate(roles):
            if not isinstance(r, dict):
                print(f"项 {i} ({t.get('name')}) roles[{ri}] 不是对象")
                ok = False
                continue
            if not r.get('department'):
                print(f"项 {i} ({t.get('name')}) roles[{ri}] 缺少 department")
                ok = False
            if not r.get('position'):
                print(f"项 {i} ({t.get('name')}) roles[{ri}] 缺少 position")
                ok = False
            if r.get('order') is None:
                print(f"项 {i} ({t.get('name')}) roles[{ri}] 缺少 order")
                ok = False
    if ok:
        print('OK: data/teachers.json 校验通过')
        return 0
    else:
        print('校验发现问题')
        return 1


def cmd_add_person(args):
    data = load_data()
    name = args.name
    if find_teacher(data, name=name):
        print('已存在同名教师:', name)
        return 1

    tid = args.id or canonical_id(name)
    existing_ids = {t.get('id') for t in data}
    base = tid
    n = 1
    while tid in existing_ids:
        tid = f"{base}_{n}"
        n += 1

    entry = {
        'id': tid,
        'name': name,
        'photo': args.photo or 'photos/placeholder.jpg',
        'shortSummary': args.short or '',
        'bio': args.bio or '',
        'achievements': args.achievement or [],
        'roles': [],
    }
    data.append(entry)
    write_data(data)
    append_todo(f"添加教师(人): {entry['name']} id={entry['id']}")
    print('已添加:', entry['id'])
    return 0


def cmd_add_role(args):
    data = load_data()
    teacher = find_teacher(data, tid=args.id, name=args.name)
    if not teacher:
        print('未找到教师(请用 --id 或 --name):', args.id or args.name)
        return 1
    dept = clean_dept(args.department or '')
    pos = norm_line(args.position or '')
    if not dept or not pos:
        print('ERROR: --department 与 --position 不能为空')
        return 2
    role = {'department': dept, 'position': pos, 'order': int(args.order)}
    ensure_role(teacher, role)
    normalize_teacher_roles(teacher)
    write_data(data)
    append_todo(f"添加岗位: {teacher.get('name')} [{dept}] {pos} order={args.order}")
    print('已添加岗位:', teacher.get('id'))
    return 0


def cmd_remove_role(args):
    data = load_data()
    teacher = find_teacher(data, tid=args.id, name=args.name)
    if not teacher:
        print('未找到教师(请用 --id 或 --name):', args.id or args.name)
        return 1
    roles = teacher.get('roles') or []
    if not isinstance(roles, list) or not roles:
        print('该教师没有 roles')
        return 1

    idx = args.role_index - 1
    if idx < 0 or idx >= len(roles):
        print(f'ERROR: --role-index 超出范围 (1..{len(roles)})')
        return 2
    removed = roles.pop(idx)
    teacher['roles'] = roles
    normalize_teacher_roles(teacher)
    write_data(data)
    append_todo(f"删除岗位: {teacher.get('name')} [{removed.get('department')}] {removed.get('position')} idx={args.role_index}")
    print('已删除岗位:', teacher.get('id'))
    return 0


def cmd_edit_person(args):
    data = load_data()
    teacher = find_teacher(data, tid=args.id, name=args.name)
    if not teacher:
        print('未找到教师(请用 --id 或 --name):', args.id or args.name)
        return 1

    changes = []
    if args.new_name:
        old = teacher.get('name')
        teacher['name'] = normalize_name(args.new_name)
        changes.append(f"name:{old}->{teacher['name']}")
    if args.photo is not None:
        teacher['photo'] = args.photo
        changes.append('photo')
    if args.short is not None:
        teacher['shortSummary'] = args.short
        changes.append('shortSummary')
    if args.bio is not None:
        teacher['bio'] = args.bio
        changes.append('bio')
    if args.clear_achievements:
        teacher['achievements'] = []
        changes.append('achievements:clear')
    if args.achievement:
        teacher.setdefault('achievements', [])
        teacher['achievements'].extend(args.achievement)
        changes.append(f"achievements:+{len(args.achievement)}")

    normalize_teacher_roles(teacher)
    write_data(data)
    append_todo(f"编辑教师信息: {teacher.get('name')} changes={','.join(changes) if changes else 'none'}")
    print('已更新:', teacher.get('id'))
    return 0


def cmd_edit_role(args):
    data = load_data()
    teacher = find_teacher(data, tid=args.id, name=args.name)
    if not teacher:
        print('未找到教师(请用 --id 或 --name):', args.id or args.name)
        return 1
    roles = teacher.get('roles') or []
    if not isinstance(roles, list) or not roles:
        print('该教师没有 roles')
        return 1

    idx = args.role_index - 1
    if idx < 0 or idx >= len(roles):
        print(f'ERROR: --role-index 超出范围 (1..{len(roles)})')
        return 2

    r = roles[idx]
    before = (r.get('department'), r.get('position'), r.get('order'))

    if args.department is not None:
        r['department'] = clean_dept(args.department)
    if args.position is not None:
        r['position'] = norm_line(args.position)
    if args.order is not None:
        r['order'] = int(args.order)

    teacher['roles'] = roles
    normalize_teacher_roles(teacher)
    # normalize_teacher_roles 可能改变顺序，按 order 排一下便于 list 查看
    teacher['roles'] = sorted(teacher.get('roles') or [], key=lambda x: int(x.get('order') or 10**9))

    write_data(data)
    after_roles = teacher.get('roles') or []
    append_todo(f"编辑岗位: {teacher.get('name')} idx={args.role_index} before={before} after_count={len(after_roles)}")
    print('已更新岗位:', teacher.get('id'))
    return 0


def cmd_sync_from_liest(args):
    data = load_data()
    data = merge_teachers_by_name(data)

    # 合并后再次全量清洗一遍 roles，确保没有遗留脏岗位
    for t in data:
        normalize_teacher_roles(t)

    # build fallback map (name -> dept -> position)
    fallback = {}
    for t in data:
        name = normalize_name(t.get('name') or '')
        if not name:
            continue
        fallback.setdefault(name, {})
        for r in (t.get('roles') or []):
            d = r.get('department')
            p = normalize_position(r.get('position'))
            if d and p:
                fallback[name][clean_dept(d)] = p

    raw_path = os.path.join(ROOT, 'teacher-liest')
    if not os.path.exists(raw_path):
        print('ERROR: 未找到 teacher-liest 文件')
        return 2
    with open(raw_path, 'r', encoding='utf-8') as f:
        roles = parse_teacher_liest(f.read())

    # index teachers by name for stable merges
    by_name = {normalize_name(t.get('name') or ''): t for t in data if t.get('name')}

    for rr in roles:
        name = normalize_name(rr['name'])
        dept = rr['department']
        pos = normalize_position(rr.get('position'))
        if not pos:
            pos = fallback.get(name, {}).get(clean_dept(dept))
        if not pos:
            # 保底，避免前端显示空职位
            pos = '教师'

        pos = normalize_position(pos) or pos

        dept = normalize_dept_by_position(dept, pos)

        teacher = by_name.get(name)
        if not teacher:
            tid = canonical_id(name)
            existing_ids = {t.get('id') for t in data}
            base = tid
            n = 1
            while tid in existing_ids:
                tid = f"{base}_{n}"
                n += 1
            teacher = {
                'id': tid,
                'name': name,
                'photo': 'photos/placeholder.jpg',
                'shortSummary': '',
                'bio': '',
                'achievements': [],
                'roles': [],
            }
            data.append(teacher)
            by_name[name] = teacher

        ensure_role(teacher, {'department': dept, 'position': pos, 'order': int(rr['order'])})

    # sort roles within each teacher
    for t in data:
        t['roles'] = sorted(t.get('roles') or [], key=lambda x: int(x.get('order') or 10**9))

    # 管理部强制排序（只影响管理部角色的 order）
    mgmt_rank = {n: i + 1 for i, n in enumerate(MGMT_ORDER)}
    for t in data:
        nm = normalize_name(t.get('name') or '')
        rank = mgmt_rank.get(nm)
        if not rank:
            continue
        for r in (t.get('roles') or []):
            if clean_dept(r.get('department') or '') == '管理部':
                r['order'] = rank

    # re-sort roles after overrides
    for t in data:
        t['roles'] = sorted(t.get('roles') or [], key=lambda x: int(x.get('order') or 10**9))

    # sort teachers by earliest role order
    def teacher_key(t):
        orders = [int(r.get('order') or 10**9) for r in (t.get('roles') or [])]
        return (min(orders) if orders else 10**9, t.get('name') or '')

    data.sort(key=teacher_key)

    if args.write:
        write_data(data)
        append_todo('从 teacher-liest 同步岗位与排序（写入 teachers.json）')
        print('已写入 data/teachers.json (已自动备份)')
    else:
        print('DRY RUN: 解析到 roles 条目:', len(roles))
        print('DRY RUN: 合并后教师人数:', len(data))
        print('DRY RUN: 使用 --write 写入 data/teachers.json')
    return 0


def cmd_remove(args):
    data = load_data()
    before = len(data)
    data = [t for t in data if t.get('id') != args.id]
    after = len(data)
    if before == after:
        print('未找到 id:', args.id)
        return 1
    write_data(data)
    append_todo(f"删除教师 id={args.id}")
    print('已删除 id=', args.id)
    return 0


def main():
    p = argparse.ArgumentParser(description='管理 data/teachers.json')
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('list')
    sub.add_parser('validate')

    ps = sub.add_parser('sync-from-liest', help='从 teacher-liest 同步岗位与排序（支持跨部门/多岗位）')
    ps.add_argument('--write', action='store_true', help='写入 data/teachers.json（会自动备份）')

    pp = sub.add_parser('add-person', help='新增教师（人）')
    pp.add_argument('--id', help='可选 id，默认基于 name 生成')
    pp.add_argument('--name', required=True)
    pp.add_argument('--photo')
    pp.add_argument('--short')
    pp.add_argument('--bio')
    pp.add_argument('--achievement', action='append', help='可重复指定以添加多个成就/奖项')

    prl = sub.add_parser('add-role', help='给教师添加岗位（跨部门/身兼数职）')
    prl.add_argument('--id', help='教师 id（可选，与 --name 二选一）')
    prl.add_argument('--name', help='教师姓名（可选，与 --id 二选一）')
    prl.add_argument('--department', required=True)
    prl.add_argument('--position', required=True)
    prl.add_argument('--order', type=int, required=True)

    pe = sub.add_parser('edit-person', help='编辑教师信息（头像/简介/姓名等）')
    pe.add_argument('--id', help='教师 id（可选，与 --name 二选一）')
    pe.add_argument('--name', help='教师姓名（可选，与 --id 二选一）')
    pe.add_argument('--new-name', dest='new_name')
    pe.add_argument('--photo', help='覆盖 photo 字段（传空字符串可清空）')
    pe.add_argument('--short', help='覆盖 shortSummary 字段（传空字符串可清空）')
    pe.add_argument('--bio', help='覆盖 bio 字段（传空字符串可清空）')
    pe.add_argument('--achievement', action='append', help='追加成就/奖项（可重复）')
    pe.add_argument('--clear-achievements', action='store_true', help='清空 achievements')

    per = sub.add_parser('edit-role', help='编辑某一条岗位（部门/岗位名称/order）')
    per.add_argument('--id', help='教师 id（可选，与 --name 二选一）')
    per.add_argument('--name', help='教师姓名（可选，与 --id 二选一）')
    per.add_argument('--role-index', type=int, required=True, help='岗位序号（从 1 开始；可用 list 查看顺序）')
    per.add_argument('--department', help='新 department')
    per.add_argument('--position', help='新 position（岗位名称）')
    per.add_argument('--order', type=int, help='新 order（排序用）')

    prrm = sub.add_parser('remove-role', help='删除某一条岗位')
    prrm.add_argument('--id', help='教师 id（可选，与 --name 二选一）')
    prrm.add_argument('--name', help='教师姓名（可选，与 --id 二选一）')
    prrm.add_argument('--role-index', type=int, required=True, help='岗位序号（从 1 开始；可用 list 查看顺序）')

    pr = sub.add_parser('remove')
    pr.add_argument('--id', required=True)

    args = p.parse_args()
    if args.cmd == 'list':
        cmd_list(args)
    elif args.cmd == 'validate':
        return cmd_validate(args)
    elif args.cmd == 'sync-from-liest':
        return cmd_sync_from_liest(args)
    elif args.cmd == 'add-person':
        return cmd_add_person(args)
    elif args.cmd == 'add-role':
        return cmd_add_role(args)
    elif args.cmd == 'edit-person':
        return cmd_edit_person(args)
    elif args.cmd == 'edit-role':
        return cmd_edit_role(args)
    elif args.cmd == 'remove-role':
        return cmd_remove_role(args)
    elif args.cmd == 'remove':
        return cmd_remove(args)
    else:
        p.print_help()


if __name__ == '__main__':
    raise SystemExit(main())
