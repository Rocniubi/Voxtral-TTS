# Voxtral TTS Static Site

这是从 `MSA` 多站点架构里拆出来的独立静态项目。

当前目标很明确：

- 只保留一个首页
- 首页主功能区就是 Hugging Face iframe
- 文案走 `locales/en.json`
- 部署目标是 Cloudflare Pages
- 不接登录、支付、数据库、Workers AI、D1、R2、Workflow

## 目录结构

```text
voxtraltts.online/
- index.html
- 404.html
- styles.css
- locales/en.json
- assets/
- _headers
- robots.txt
- sitemap.xml
- wrangler.toml
```

## 本地预览

不需要安装任何框架。

```bash
cd /Users/chenweipeng/Downloads/代码/voxtraltts.online
pnpm dev
```

默认地址：

```text
http://localhost:4173
```

## Cloudflare Pages 部署

这套站点是纯静态站，推荐两种发法。

### 方式 1：Cloudflare Pages 面板连 Git

项目设置这样填：

- Framework preset: `None`
- Build command: 留空，或者填 `exit 0`
- Build output directory: `.`
- Root directory: 当前项目目录

这套站点没有 Functions，不需要任何环境变量。

### 方式 2：Wrangler 直接上传

```bash
cd /Users/chenweipeng/Downloads/代码/voxtraltts.online
npx wrangler login
npx wrangler pages deploy . --project-name=voxtraltts-online
```

如果你已经提前在 Cloudflare 创建了 Pages 项目，也可以直接用：

```bash
pnpm deploy
```

## 迁移后和 MSA 的关系

迁移完成后，这个目录已经是独立项目，和 `MSA/sites/voxtraltts` 没有运行时依赖。

也就是说：

- 不再依赖多站点注册
- 不再依赖 Next.js
- 不再依赖 Auth
- 不再依赖 Stripe
- 不再依赖 D1
- 不再依赖 Workflow

## 后续如果要扩 SEO

现在这版最适合先验证首页流量。

如果后面要扩内容，建议按这个方式加：

- 新增独立静态页面，比如 `compare/`, `faq/`, `guides/`
- 每个页面单独写静态 HTML
- 每个页面都补自己的 title、description、canonical、OG
- 如果需要多语言 SEO，再按语言拆目录，比如 `zh/`, `ja/`

现在先保持单页，会更轻，也更稳。
