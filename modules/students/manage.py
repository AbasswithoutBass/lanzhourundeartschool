#!/usr/bin/env python3
"""data/students.json 管理工具（优秀考生/录取喜报）

数据格式（v1）：
    [
      {
        "id": "s_001",
        "name": "张同学",
        "school": "中央音乐学院",
        "major": "声乐表演（美声）",
        "year": 2026,
        "photo": "path/to/photo.jpg",
        "admissions": [
          {"image": "path/to/admission.jpg", "watermarked": true, "note": "..."}
        ]
      }
    ]

常用命令：
    python modules/students/manage.py list
    python modules/students/manage.py validate
    python modules/students/manage.py add-student --name "张三" --school "中央音乐学院" --major "声乐表演" --year 2026
    python modules/students/manage.py add-admission --name "张三" --image "students/admissions/xxx.jpg" --watermarked
    python modules/students/manage.py watermark --input students/admissions_raw --output students/admissions --text "兰州润德艺术学校" --add-to-json

依赖：Pillow（用于水印）
"""

import argparse
import datetime
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / 'data' / 'students.json'
TODO_PATH = ROOT / 'todo.txt'


def norm_line(s: str) -> str:
    s = (s or '').replace('\u3000', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def write_todo(line: str):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    TODO_PATH.write_text(TODO_PATH.read_text(encoding='utf-8') + f"{ts} — {line} — by students/manage.py\n", encoding='utf-8') if TODO_PATH.exists() else TODO_PATH.write_text(f"{ts} — {line} — by students/manage.py\n", encoding='utf-8')


def load_data(path: Path = DATA_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8'))


def backup_file(path: Path):
    if not path.exists():
        return
    bak = path.with_suffix(path.suffix + '.bak.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    shutil.copy2(path, bak)


def write_data(data: list[dict], path: Path = DATA_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_file(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def canonical_id(name: str, school: str | None = None, year: int | None = None) -> str:
    base = f"{name}_{school or ''}_{year or ''}".strip('_')
    base = base.replace(' ', '_')
    base = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff-]", '', base)
    return base.lower() or 'student'


def find_student(data: list[dict], *, sid: str | None = None, name: str | None = None) -> dict | None:
    for s in data:
        if sid and s.get('id') == sid:
            return s
        if name and s.get('name') == name:
            return s
    return None


def relpath_to_root(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return p.as_posix()


def validate_data(data: list[dict]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(data, list):
        return False, ['顶层必须是数组(list)']

    ids: set[str] = set()
    for i, s in enumerate(data):
        if not isinstance(s, dict):
            errors.append(f'项 {i} 不是对象')
            continue

        sid = s.get('id')
        if not sid:
            errors.append(f'项 {i} 缺少 id')
        elif sid in ids:
            errors.append(f'重复 id: {sid}')
        else:
            ids.add(sid)

        for k in ('name', 'school', 'major'):
            if not norm_line(str(s.get(k, ''))):
                errors.append(f"项 {i} ({s.get('id','?')}) 缺少 {k}")

        year = s.get('year')
        if year is not None:
            try:
                int(year)
            except Exception:
                errors.append(f"项 {i} ({s.get('name')}) year 不是整数")

        admissions = s.get('admissions', [])
        if admissions is None:
            admissions = []
        if not isinstance(admissions, list):
            errors.append(f"项 {i} ({s.get('name')}) admissions 必须是数组")
        else:
            for ai, a in enumerate(admissions):
                if not isinstance(a, dict):
                    errors.append(f"项 {i} ({s.get('name')}) admissions[{ai}] 不是对象")
                    continue
                if not norm_line(str(a.get('image', ''))):
                    errors.append(f"项 {i} ({s.get('name')}) admissions[{ai}] 缺少 image")

    return (len(errors) == 0, errors)


def cmd_list(args) -> int:
    data = load_data()
    for s in data:
        adm = s.get('admissions') or []
        print(f"{s.get('id','?')}  {s.get('name','?')}  {s.get('school','?')}  {s.get('major','?')}  year={s.get('year','?')}  admissions={len(adm)}")
    return 0


def cmd_validate(args) -> int:
    data = load_data()
    ok, errs = validate_data(data)
    if ok:
        print('OK: data/students.json 校验通过')
        return 0
    print('校验发现问题：')
    for e in errs:
        print(' -', e)
    return 1


def cmd_add_student(args) -> int:
    data = load_data()
    name = norm_line(args.name)
    school = norm_line(args.school)
    major = norm_line(args.major)
    year = int(args.year) if args.year is not None else None

    if find_student(data, name=name):
        print('已存在同名学生:', name)
        return 1

    sid = args.id or canonical_id(name, school, year)
    existing = {s.get('id') for s in data}
    base = sid
    n = 1
    while sid in existing:
        sid = f"{base}_{n}"
        n += 1

    entry = {
        'id': sid,
        'name': name,
        'school': school,
        'major': major,
        'year': year,
        'photo': norm_line(args.photo) if args.photo else '',
        'admissions': [],
    }
    data.append(entry)
    write_data(data)
    write_todo(f"添加优秀考生: {name} / {school} / {major} year={year}")
    print('已添加:', sid)
    return 0


def cmd_add_admission(args) -> int:
    data = load_data()
    student = find_student(data, sid=args.id, name=args.name)
    if not student:
        print('未找到学生(请用 --id 或 --name):', args.id or args.name)
        return 1

    image = norm_line(args.image)
    if not image:
        print('ERROR: --image 不能为空')
        return 2

    admission = {
        'image': image,
        'watermarked': bool(args.watermarked),
        'note': norm_line(args.note) if args.note else '',
    }
    student.setdefault('admissions', [])
    student['admissions'].append(admission)
    write_data(data)
    write_todo(f"添加录取截图: {student.get('name')} image={image}")
    print('已添加录取截图:', student.get('id'))
    return 0


def guess_font(size: int) -> ImageFont.ImageFont:
    # macOS 常见字体路径兜底；找不到就用默认字体
    candidates = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return ImageFont.truetype(p, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def apply_text_watermark(img: Image.Image, text: str, *, opacity: float = 0.28, position: str = 'br') -> Image.Image:
    base = img.convert('RGBA')
    overlay = Image.new('RGBA', base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 字号按短边比例
    short_edge = min(base.size)
    font_size = max(18, int(short_edge * 0.045))
    font = guess_font(font_size)

    text = norm_line(text)
    if not text:
        return img

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = max(10, int(short_edge * 0.03))

    if position == 'bl':
        x, y = margin, base.size[1] - th - margin
    elif position == 'tl':
        x, y = margin, margin
    elif position == 'tr':
        x, y = base.size[0] - tw - margin, margin
    else:  # br
        x, y = base.size[0] - tw - margin, base.size[1] - th - margin

    a = int(255 * max(0.0, min(1.0, opacity)))
    fill = (255, 255, 255, a)
    stroke_fill = (0, 0, 0, int(a * 0.65))
    draw.text((x, y), text, font=font, fill=fill, stroke_width=2, stroke_fill=stroke_fill)

    out = Image.alpha_composite(base, overlay).convert('RGB')
    return out


@dataclass
class NameHint:
    name: str
    school: str | None


def parse_name_hint_from_filename(filename: str) -> NameHint | None:
    # 约定：姓名__学校__xxx.jpg
    stem = Path(filename).stem
    parts = stem.split('__')
    if len(parts) >= 2:
        name = norm_line(parts[0]).replace(' ', '')
        school = norm_line(parts[1])
        if name:
            return NameHint(name=name, school=school or None)
    return None


def cmd_watermark(args) -> int:
    input_path = (ROOT / args.input).resolve() if not os.path.isabs(args.input) else Path(args.input).resolve()
    output_path = (ROOT / args.output).resolve() if not os.path.isabs(args.output) else Path(args.output).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    text = args.text or '兰州润德艺术学校'
    opacity = float(args.opacity)
    position = args.position

    if input_path.is_dir():
        in_files = [p for p in input_path.rglob('*') if p.is_file() and p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')]
    else:
        in_files = [input_path]

    if not in_files:
        print('未找到可处理图片:', input_path)
        return 1

    data = load_data() if args.add_to_json else None
    updated = 0
    processed = 0

    for p in in_files:
        try:
            img = Image.open(p)
            out = apply_text_watermark(img, text, opacity=opacity, position=position)
            out_name = p.name
            out_file = output_path / out_name
            out.save(out_file, quality=95)
            processed += 1

            if args.add_to_json and data is not None:
                hint = parse_name_hint_from_filename(p.name)
                if not hint:
                    continue
                student = find_student(data, name=hint.name)
                if not student and args.create_missing:
                    # 缺少则创建（major 先留空，后续再补）
                    sid = canonical_id(hint.name, hint.school, args.year)
                    student = {
                        'id': sid,
                        'name': hint.name,
                        'school': hint.school or '',
                        'major': '',
                        'year': int(args.year) if args.year else None,
                        'photo': '',
                        'admissions': [],
                    }
                    data.append(student)

                if student:
                    student.setdefault('admissions', [])
                    student['admissions'].append({
                        'image': relpath_to_root(out_file),
                        'watermarked': True,
                        'note': norm_line(args.note) if args.note else '',
                    })
                    updated += 1
        except Exception as e:
            print('处理失败:', p, str(e))

    if args.add_to_json and data is not None:
        write_data(data)
        write_todo(f"批量水印并写回 students.json: processed={processed} updated={updated}")

    print(f'已处理图片: {processed}')
    if args.add_to_json:
        print(f'写回 admissions 条目: {updated}')
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description='管理 data/students.json（优秀考生/录取喜报）')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('list')
    sub.add_parser('validate')

    ps = sub.add_parser('add-student', help='新增优秀考生')
    ps.add_argument('--id')
    ps.add_argument('--name', required=True)
    ps.add_argument('--school', required=True)
    ps.add_argument('--major', required=True)
    ps.add_argument('--year', type=int)
    ps.add_argument('--photo')

    pa = sub.add_parser('add-admission', help='给学生添加录取截图')
    pa.add_argument('--id', help='学生 id（可选，与 --name 二选一）')
    pa.add_argument('--name', help='学生姓名（可选，与 --id 二选一）')
    pa.add_argument('--image', required=True)
    pa.add_argument('--watermarked', action='store_true')
    pa.add_argument('--note')

    pw = sub.add_parser('watermark', help='对录取截图批量加水印')
    pw.add_argument('--input', required=True, help='输入文件或目录')
    pw.add_argument('--output', required=True, help='输出目录')
    pw.add_argument('--text', default='兰州润德艺术学校')
    pw.add_argument('--opacity', default='0.28')
    pw.add_argument('--position', choices=['br', 'bl', 'tr', 'tl'], default='br')
    pw.add_argument('--add-to-json', action='store_true', help='按文件名约定解析并写回 students.json 的 admissions')
    pw.add_argument('--create-missing', action='store_true', help='add-to-json 时，若学生不存在则创建')
    pw.add_argument('--year', type=int, help='create-missing 时写入 year')
    pw.add_argument('--note', help='写回 admissions.note')

    args = p.parse_args()

    if args.cmd == 'list':
        return cmd_list(args)
    if args.cmd == 'validate':
        return cmd_validate(args)
    if args.cmd == 'add-student':
        return cmd_add_student(args)
    if args.cmd == 'add-admission':
        return cmd_add_admission(args)
    if args.cmd == 'watermark':
        return cmd_watermark(args)

    p.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
