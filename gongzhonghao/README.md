# 七宗罪 × 七美德 · 人格光影测试（公众号项目）

一套**完全免费**的**微信公众号**内容项目：
在线人格测试页（46 题 → 14 维雷达报告）+ 公众号「每天一个测试」每日推文自动发布。

**模式：测试免费 + 报告免费，纯内容涨粉**

## 项目结构

```
gongzhonghao/
├── index.html                  # 测试页（GitHub Pages 站点入口，46 题）
├── quiz/index.html             # 测试页源码（与根目录一致）
├── questions/                  # 测试题库（JSON，每日轮换）
├── notes/                      # 公众号推文素材
│   ├── 笔记文案.md             # 每天一个测试推文模板/标题/正文/发布注意事项
│   ├── img/公众号头像.png       # 公众号头像（1200×1200，已生成）
│   ├── img/                     # 配图（可复用为推文配图）
│   └── shoot*.js               # 截图脚本（本地工具，可选）
├── scripts/
│   ├── daily_pipeline.py       # 每日自动：选题→生成推文→发布草稿箱
│   ├── md2wechat.py            # Markdown → 微信 HTML（金色美化 + 按钮）
│   └── publish_wechat.py       # 公众号 API 发布（token→封面→草稿）
├── output/                     # 生成的推文（md + html）
└── product/
    ├── 商品上架资料.md          # 公众号昵称/简介/上线清单
    └── 公众号运营方案.md        # 内容日历/增长裂变/转化漏斗/KPI
```

## 部署测试页到 GitHub Pages

1. 仓库 `TonDeng/xhs`，GitHub Pages 已启用（Source: main / root）
2. 测试页地址：`https://tondeng.github.io/xhs/`
3. 本地改完 push 即可自动部署

## 每日自动发布推文

Windows 定时任务 `GZH_Daily_Quiz_Publish` 每天 08:00 自动执行：

```bash
python scripts/daily_pipeline.py
```

流程：按日期轮换题库 → 生成推文 Markdown（无收费字眼、含测试链接按钮）→ 转微信 HTML → 发布到公众号草稿箱 → 记日志。

手动运行：
```bash
python scripts/daily_pipeline.py --dry-run   # 只生成不发布
python scripts/daily_pipeline.py --question qizongzui-v2  # 指定题库
```

配置（不入库）：`scripts/config.local.json` → `{"appid": "...", "secret": "...", "gzh": "每天一个测试"}`

## 公众号上线流程

1. 注册公众号（个人订阅号，免费）→ 设置昵称/简介/头像（见 `product/商品上架资料.md`）
2. 部署测试页（见上）
3. 公众号后台配置：自动回复 + 自定义菜单「免费测试」
4. 每天 08:00 自动生成推文到草稿箱 → 后台点「群发」
5. 运营节奏按 `product/公众号运营方案.md`

## 注意事项

- 测试结果仅供自我探索与娱乐参考（页面已注明）
- 测试与报告完全免费，无任何付费环节
- 页面无任何外部依赖，可离线运行；部署后记得测一遍完整答题流程
