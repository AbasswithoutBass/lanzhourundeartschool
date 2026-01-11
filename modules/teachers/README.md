**教师数据管理模块**

目的：提供简单的脚本以增删查验 `data/teachers.json`，并在每次修改写入 `todo.txt` 记录。

位置：modules/teachers/manage.py

基本命令：
- 列表：`python manage.py list`
- 校验：`python manage.py validate`
- 从 teacher-liest 同步：`python manage.py sync-from-liest --write`
- 添加教师（人）：`python manage.py add-person --name "张三" --photo "photos/placeholder.jpg"`
- 添加岗位（可多次执行以支持跨部门/身兼数职）：`python manage.py add-role --name "张三" --department "声乐组" --position "声乐教师" --order 999`
- 编辑教师信息（头像/简介/姓名等）：`python manage.py edit-person --name "张三" --photo "photos/zhang.jpg" --short "一句话简介" --bio "详细简介"`
- 编辑岗位（改部门/岗位名/排序）：`python manage.py edit-role --name "张三" --role-index 1 --position "声乐名师" --order 120`
- 删除某条岗位：`python manage.py remove-role --name "张三" --role-index 2`
- 删除教师（整个人）：`python manage.py remove --id xxx`

注意：脚本会在写入前自动备份 `data/teachers.json` 到同目录并带时间戳的 .bak 文件。

如需在本地预览页面，请在仓库根目录运行简单 HTTP 服务：
`python -m http.server 8000` 然后浏览器访问 http://localhost:8000
