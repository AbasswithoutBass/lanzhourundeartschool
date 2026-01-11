Excel 模板说明（教师）

请新建一个 .xlsx，第一行是表头（列名必须严格一致）：

必填列：
- id
- name

可选列：
- photo (photos/xxx.jpg 或 teachers/photos/xxx.jpg)
- shortSummary
- bio
- achievements (用 | 分隔)
- department
- position
- order

规则：
- 每行可代表一个岗位；同一 id 多行会合并为同一老师并累计 roles。
- 如果 department/position 只填了一个，会忽略该行岗位并提示 warning。
- Excel 导入不复制图片，只校验路径格式并提示文件是否存在。
