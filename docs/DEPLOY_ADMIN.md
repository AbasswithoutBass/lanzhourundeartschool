# 部署后台（控制 Cloudflare 上的静态站点）

当前 Cloudflare 部署的是 `public/` 静态站点；Flask 后台需要单独部署到能跑 Python 的服务上。

推荐做法：把后台部署到 Render/Fly.io/Railway 等，然后让后台用 **GitHub Contents API** 直接读写仓库里的文件：
- JSON：`public/data/*.json`
- 门户图片：`public/assets/portal/...`

这样你在后台点“保存/上传”，就会提交到 GitHub 仓库，Cloudflare 会自动重新构建并上线。

## 1) 必要环境变量

在部署平台配置这些环境变量：

- `ADMIN_PASSWORD`：后台登录密码
- `ADMIN_SECRET_KEY`：随机长字符串（session 用）
- `ADMIN_SITE_MODE=public`：让后台写入 `public/`，从而控制线上站点
- `ADMIN_STORAGE=github`：开启 GitHub 存储模式（不写本地文件，直接写仓库）
- `GITHUB_REPO=AbasswithoutBass/lanzhourundeartschool`：你的仓库
- `GITHUB_BRANCH=main`
- `GITHUB_TOKEN=xxxx`：GitHub Personal Access Token（需要 repo 内容读写权限）

说明：`GITHUB_TOKEN` 建议只授予最小权限（Contents 读写）。

## 2) Render 部署示例

- Build Command：`pip install -r requirements.txt`
- Start Command：`gunicorn "admin_app.app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

部署完成后：
- 后台地址：`https://你的后台域名/admin`

## 3) 线上工作流

- 你在后台修改教师/学生/信息门户并保存
- 后台会把文件写入 GitHub：`public/data/...` 和 `public/assets/portal/...`
- Cloudflare 自动触发部署，前台站点更新

## 4) 安全建议（强烈建议）

- 给后台加一层访问限制：
  - 仅允许特定 IP（办公室/家里）
  - 或部署在内网/VPN 下
- 定期更换 `ADMIN_PASSWORD`

