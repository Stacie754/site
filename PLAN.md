# 猫咪寄养业务网站建设计划（部署到 GitHub Pages）

## 1. 目标与范围

### 业务目标
- 建立一个可信、好看的独立网站，服务猫咪寄养业务。
- 用网站承接来自 Rover / 小红书 / 朋友转介绍的流量。
- 提升咨询转化率（让访客更快发起联系或预约）。

### 技术目标
- 全站静态化，可部署到 GitHub Pages。
- 维护成本低（内容可按 Markdown 更新，不依赖后端）。
- 页面加载快，移动端体验好，支持 SEO。
- 支持本地 SEO + GEO（LLM Search），让温哥华用户更容易搜到网站。

### 非目标（首版不做）
- 不做自建支付系统。
- 不做复杂会员系统/登录系统。
- 不做复杂后台管理系统（首版以手工维护内容为主）。

---

## 2. 目标用户与价值主张

### 目标用户
- 在本地寻找可靠猫咪寄养/上门照看服务的猫主人。
- 对“安全、更新及时、懂猫行为和医疗护理”敏感的人群。

### 核心价值主张（首页必须体现）
- 专注猫咪照护，熟悉猫咪行为和情绪管理。
- 有真实评价和案例（可基于 `reference/rover-stacie-comments.md`）。
- 有清晰的流程、服务边界、收费与紧急处理机制。

---

## 3. 信息架构（网站页面）

### 必要页面（MVP）
1. 首页（Home）
2. 服务与价格（Services & Pricing）
3. 寄养环境与日常（Environment）
4. 评价与案例（Reviews）
5. FAQ（常见问题）
6. 预约流程与联系（Book / Contact）

### 页面关键内容
- 首页：一句话价值主张 + 核心服务卡片 + 真实评价摘录 + CTA（立即咨询/预约）。
- 服务与价格：服务类型、时长、收费区间、附加服务、取消政策。
- 环境页：空间照片、每日作息、隔离/消毒流程、安全措施。
- 评价页：精选评论、按时间展示、可附 Rover 链接增强可信度。
- FAQ：接送、试住、饮食、药物、应急、照片更新频率等。
- 联系页：微信/邮箱/表单 + 服务区域 + 可预约时间。

---

## 4. 内容准备清单

### 必备素材
- 品牌名、slogan、头像/主视觉图。
- 服务说明文案（每项服务 80-150 字）。
- 价格与政策（含退款/改期规则）。
- 真实环境照片（至少 15-20 张）。
- 评价数据（已抓取的 74 条评论可做素材池）。
- 联系方式与营业时段。

### 内容结构建议
- 评论数据做成结构化 JSON/Markdown，便于筛选“精选 6-10 条”。
- 图片统一命名与压缩（webp 优先，保留 jpg 兼容）。
- FAQ 先做 12-15 条，后续按客户真实问题迭代。
- 增加温哥华本地关键词文案池（中英文），用于页面标题、FAQ、服务说明。

---

## 5. 技术方案（GitHub Pages 友好）

### 推荐栈
- 框架：Astro（静态站点、SEO 友好、部署简单）。
- 样式：Tailwind CSS（快速搭建 + 统一设计 token）。
- 内容：Markdown + JSON（评论、FAQ、服务配置）。
- 表单：Formspree / Basin / Getform（三选一，避免自建后端）。
- 统计：Plausible 或 GA4。

### 仓库结构建议
- `src/pages/`：页面路由
- `src/components/`：通用组件（Hero、PricingCard、ReviewCard）
- `src/content/`：服务、FAQ、评价精选
- `public/images/`：图片资源
- `reference/`：原始资料（保留）

---

## 6. 设计与体验规范

### 品牌感
- 风格关键词：温暖、专业、安心、干净。
- 颜色：中性底色 + 1 个强调色（避免花哨，强调信任感）。
- 字体：中文可用思源黑体/Noto Sans SC，英文搭配 Inter。

### 交互重点
- 每屏都要有明确 CTA（咨询、预约、查看价格）。
- 首屏加载 < 2.5s（图片优化是关键）。
- 移动端优先（大部分流量来自手机）。

---

## 7. SEO / GEO 与转化

### SEO 基础
- 每页唯一标题（Title）与描述（Meta Description）。
- 结构化数据：`LocalBusiness` + `FAQPage`（JSON-LD）。
- Open Graph 与 Twitter 卡片配置。
- `sitemap.xml` 与 `robots.txt`。

### 本地 SEO（温哥华）
- 所有核心页面加入本地实体词：`Vancouver`、`温哥华`、`cat boarding`、`cat sitter`、`猫咪寄养`。
- 首页和服务页明确 `Service Area`（例如：Downtown Vancouver / Burnaby / Richmond，按真实服务范围填写）。
- 联系页保持 NAP 一致性（Name/Area/Contact），与 Rover 主页和社媒信息一致。
- 增加“温哥华猫咪寄养指南/FAQ”内容块，覆盖高意图长尾问题。
- 接入 Google Search Console 与 Bing Webmaster，提交 sitemap 并跟踪索引状态。

### GEO（LLM Search，可被 AI 更好理解和引用）
- 关键业务信息使用“可抽取”的结构：清晰标题 + 简短段落 + 列表/表格（价格、流程、政策、服务范围）。
- 保证首屏和核心信息直接在 HTML 中可读（避免仅靠 JS 运行后才出现关键文本）。
- 增加 `llms.txt`（站点摘要、核心页面、更新时间、联系方式）与 `llms-full.txt`（可选）。
- 扩展 JSON-LD：`LocalBusiness`、`Service`、`FAQPage`、`Review`、`AggregateRating`、`areaServed`。
- 为评论与服务信息保留来源说明（如 Rover 评价汇总来源），提高可引用性与可信度。
- 关键页面支持中英双语并配置 `hreflang`，覆盖 Vancouver 本地英文检索与中文检索。

### 转化优化
- 首页首屏放“3 个信任信号”：评分、评论数、更新频率。
- 预约流程可视化（3 步完成咨询）。
- 联系方式固定悬浮按钮（移动端）。

---

## 8. 实施里程碑（建议 10 天）

### Milestone 1（Day 1-2）：规划与素材整理
- 确定站点结构、页面文案框架、品牌基调。
- 整理图片和评论素材，完成内容清单。
- 产出温哥华关键词地图（中英）和本地 FAQ 题库。
- 产出：最终站点 sitemap + 内容表。

### Milestone 2（Day 3-5）：MVP 开发
- 初始化 Astro 项目并搭建基础布局。
- 完成 6 个核心页面与路由。
- 接入评论精选模块与联系方式模块。
- 产出：本地可用版本。

### Milestone 3（Day 6-7）：优化与完善
- 响应式适配、性能优化、SEO 元信息完善。
- 完成 GEO 基础：`llms.txt`、扩展 JSON-LD、双语页与 `hreflang`。
- 表单联调、错误页与空状态处理。
- 产出：预发布版本。

### Milestone 4（Day 8-9）：部署上线
- 配置 GitHub Actions 自动构建部署到 GitHub Pages。
- 验证自定义域名（可选）与 HTTPS。
- 产出：线上可访问地址。

### Milestone 5（Day 10）：验收与运营准备
- 用真实用户路径做一次完整测试（咨询/跳转/表单）。
- 配置统计看板和迭代 backlog。
- 建立本地搜索与 LLM 搜索观测清单（关键词、收录、引用）。
- 产出：v1 正式版 + v1.1 迭代列表。

---

## 9. GitHub Pages 部署方案

### 分支与流程
- 主分支：`main`
- 部署方式：GitHub Actions 构建后发布到 `gh-pages`
- 策略：每次 merge 到 `main` 自动部署

### 关键事项
- 若仓库是 project page，需设置正确 `base` 路径。
- 若是 custom domain，添加 `CNAME` 并配置 DNS。
- 开启 Pages 的 HTTPS 强制。
- 建议使用自定义域名（比 `*.github.io` 更利于品牌与搜索信任）。

---

## 10. 验收标准（Definition of Done）

- 6 个核心页面全部上线可访问。
- 移动端和桌面端主要分辨率无明显布局问题。
- Lighthouse（移动端）Performance/SEO 均 >= 85。
- 联系/预约路径可用（表单可收到信息）。
- 首页包含真实评价、服务说明、价格区间、CTA。
- GitHub Pages 自动部署稳定可复现。
- 核心页面具备温哥华本地关键词（中英）和 `Service Area` 信息。
- `sitemap.xml`、`robots.txt`、`llms.txt`、JSON-LD 均可访问且语法正确。
- Search Console / Bing Webmaster 完成站点验证并提交 sitemap。

---

## 11. 下一步（马上可执行）

1. 确认品牌文案（站点名称 + 首页一句话价值主张）。
2. 从 `reference/rover-stacie-comments.md` 选出 8-12 条精选评价。
3. 确认服务与价格表（首版先定 3-5 个核心服务）。
4. 我开始搭建 Astro 项目骨架和页面模板（按本计划落地）。
