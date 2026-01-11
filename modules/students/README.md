# students 管理工具

用于维护“优秀考生/润德名人堂”数据，统一数据源为 `data/students.json`。

## 常用命令

- 校验数据：
  - `python modules/students/manage.py validate`
- 列表查看：
  - `python modules/students/manage.py list`
- 添加学生：
  - `python modules/students/manage.py add-student --name "张三" --school "中央音乐学院" --major "声乐表演" --year 2026 --photo "path/to/photo.jpg"`
- 添加录取截图：
  - `python modules/students/manage.py add-admission --name "张三" --image "students/admissions/zhangsan_001.jpg" --watermarked`

## 批量水印

- 对目录内截图批量加水印并输出到另一个目录：
  - `python modules/students/manage.py watermark --input students/admissions_raw --output students/admissions --text "兰州润德艺术学校"`

可选：使用命名约定自动写回 JSON（建议格式）：

- `姓名__学校__任意说明.jpg`
- 示例：`张三__中央音乐学院__录取截图.jpg`

然后使用：
- `python modules/students/manage.py watermark --input students/admissions_raw --output students/admissions --add-to-json --create-missing`
