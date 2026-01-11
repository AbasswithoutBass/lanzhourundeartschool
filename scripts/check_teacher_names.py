#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import importlib.util
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / 'teacher-liest'
DB_PATH = ROOT / 'data' / 'teachers.json'
MANAGE_PATH = ROOT / 'modules' / 'teachers' / 'manage.py'


def load_teachers_json() -> list[dict]:
    return json.loads(DB_PATH.read_text(encoding='utf-8'))


def load_manage_module():
    spec = importlib.util.spec_from_file_location('teachers_manage', str(MANAGE_PATH))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    manage = load_manage_module()
    if not RAW_PATH.exists():
        print('ERROR: 未找到 teacher-liest 文件:', RAW_PATH)
        return 2
    if not DB_PATH.exists():
        print('ERROR: 未找到 data/teachers.json 文件:', DB_PATH)
        return 2

    raw_text = RAW_PATH.read_text(encoding='utf-8')
    raw_roles = manage.parse_teacher_liest(raw_text)
    raw_names = [r['name'] for r in raw_roles]

    db = load_teachers_json()
    db_names = [str(t.get('name', '')).strip() for t in db]

    raw_unique = sorted(set(raw_names))
    db_unique = sorted(set(db_names))

    raw_dup = sorted([n for n, c in Counter(raw_names).items() if c > 1])
    db_dup = sorted([n for n, c in Counter(db_names).items() if c > 1])

    missing_in_db = sorted(set(raw_names) - set(db_names))
    extra_in_db = sorted(set(db_names) - set(raw_names))

    print('=== teacher-liest (解析 roles) ===')
    print('role 条目数(含跨部门):', len(raw_names))
    print('按姓名去重人数:', len(raw_unique))
    if raw_dup:
        print('同名出现多次(多岗位/跨部门):', '、'.join(raw_dup))

    print('\n=== data/teachers.json (v2) ===')
    print('教师人数:', len(db_names))
    print('按姓名去重人数:', len(db_unique))
    if db_dup:
        print('重复姓名(DB 内):', '、'.join(db_dup))

    print('\n=== 对比 (按姓名去重) ===')
    print('teacher-liest 有但 DB 没有:', len(missing_in_db))
    if missing_in_db:
        print('  ' + '、'.join(missing_in_db))
    print('DB 有但 teacher-liest 没有:', len(extra_in_db))
    if extra_in_db:
        print('  ' + '、'.join(extra_in_db))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
