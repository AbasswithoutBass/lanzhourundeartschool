# ⚡ 快速参考指南

## 🚀 快速开始

### 1️⃣ 本地测试
```bash
cd "/Volumes/.../润德/网页"
python3 -m http.server 8000
# 浏览器访问：http://localhost:8000
```

如果你不想敲命令，也可以双击脚本：

- `scripts/site_start.command`（默认 8000 并自动打开浏览器）
- `scripts/site_stop.command`

> 注意：不要用 `file://` 直接打开 `index.html`。浏览器会拦截读取本地 JSON（CORS），导致“名师团队 / 名人堂 / 信息门户”无法加载数据。

### 2️⃣ 查看教师数据
```bash
# 显示教师人数/岗位条目统计（v2：roles 多岗/跨部门）
python3 -c "
import json
with open('data/teachers.json', 'r', encoding='utf-8') as f:
    teachers = json.load(f)
people = len(teachers)
roles = sum(len(t.get('roles') or []) for t in teachers)
print(f'教师人数(去重): {people}')
print(f'岗位条目(含跨部门): {roles}')
"
```

### 3️⃣ 添加新教师
```bash
# 先新增“人”
python3 modules/teachers/manage.py add-person --name "教师名字" --photo "photos/placeholder.jpg"

# 再给该教师添加岗位（可重复执行以支持跨部门/身兼数职）
python3 modules/teachers/manage.py add-role --name "教师名字" --department "声乐组" --position "声乐教师" --order 999
```

### 4️⃣ 验证数据
```bash
python3 modules/teachers/manage.py validate
python3 modules/teachers/manage.py list
```

### 5️⃣ 优秀考生（名人堂）维护

```bash
python3 modules/students/manage.py validate
python3 modules/students/manage.py list

# 添加优秀考生
python3 modules/students/manage.py add-student \
  --name "张三" --school "中央音乐学院" --major "声乐表演" --year 2026 --photo "润德1.png"

# 添加录取截图（可多张）
python3 modules/students/manage.py add-admission --name "张三" --image "润德1.png" --watermarked --note "示例"

# 批量给截图加水印并写回 students.json（按文件名约定：姓名__学校__xxx.jpg）
python3 modules/students/manage.py watermark \
  --input students/admissions_raw \
  --output students/admissions \
  --text "兰州润德艺术学校" \
  --add-to-json --create-missing --year 2026
```

### 6️⃣ 管理后台（仅管理员可见）

```bash
# 强烈建议：只监听本机（默认就是 127.0.0.1）
export ADMIN_PASSWORD='请改成强密码'
export ADMIN_SECRET_KEY='请改成随机长字符串'

# 可选：如果你确实需要内网访问
# export ADMIN_HOST='0.0.0.0'
# export ADMIN_PORT='5050'

# 推荐使用项目自带虚拟环境（避免系统 Python 缺依赖）：
./.venv/bin/python admin_app/app.py
# 浏览器访问：http://127.0.0.1:5050
```

信息门户管理入口：

- `http://127.0.0.1:5050/admin/portal`

---

## 📋 文件对照表

| 文件/目录 | 说明 | 状态 |
|----------|------|------|
| `data/teachers.json` | ⭐ 主数据库 | ✅ 有效 |
| `data/students.json` | ⭐ 优秀考生数据库 | ✅ 有效 |
| `data/portal_posts.json` | ⭐ 信息门户文章库（招生简章/通知/政策） | ✅ 有效 |
| `scripts/` | 数据处理脚本 | ✅ 整理好 |
| `assets/portal/` | 信息门户图片（后台上传会写入这里） | ✅ 有效 |
| `photos/` | 教师头像 | ⚠️ 待补充 |
| `modules/teachers/` | 数据管理工具 | ✅ 可用 |
| `modules/students/` | 名人堂管理工具 + 水印 | ✅ 可用 |
| `index.html` | 官网主页 | ✅ 就绪 |
| `docs/teachers.md` | 教师文字版 | ⚠️ 待同步 |

---

## 🎯 当前状态

✅ 教师数据库已同步（79位教师，支持跨部门多岗）  
✅ 名人堂数据库已接入（data/students.json）  
✅ 文件结构已优化  
✅ 冗余脚本已清理  
❌ 头像文件缺失  
❌ 前端尚未测试  

---

## 📞 常见问题

**Q：教师头像放在哪？**  
A：`photos/` 目录，命名格式 `photos/{name}.jpg`

**Q：怎么添加新教师？**  
A：用 `modules/teachers/manage.py add-person` + `add-role`（推荐），或直接编辑 `data/teachers.json`

**Q：数据有多少位教师？**  
A：目前 79 位（以 `teacher-liest` 为准），并支持跨部门多岗。

**Q：前端怎么渲染教师？**  
A：`index.html` 引入 `snippets/teachers_fragment.html` 的卡片模板

---

## ✨ ID 规范

- 教师与学生的 `id` 由管理工具自动生成并保证唯一（推荐不要手工硬编码规则）。

---

**最后更新**：2026-01-11  
**维护者**：GitHub Copilot
