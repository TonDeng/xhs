# 七宗罪 × 七美德 · 人格光影测试（小红书商品项目）

一套可商用的小红书虚拟商品全套素材：
在线人格测试页（21 题 → 14 维雷达报告）+ 图文笔记配图 + 商品上架资料。

## 项目结构

```
xhs/
├── index.html                  # 测试页（GitHub Pages 站点入口）
├── quiz/index.html             # 测试页源码（与根目录一致）
├── notes/                      # 小红书图文笔记素材
│   ├── 笔记文案.md             # 标题/正文/话题标签/发布注意事项
│   ├── notes.html              # 配图设计稿（9 张卡片的 HTML 源）
│   ├── img/                    # 9 张 1080×1440 PNG 配图（已渲染）
│   └── shoot*.js               # 截图脚本（本地工具，可选）
└── product/
    └── 商品上架资料.md          # 千帆商品标题/类目/卖点/详情文案/检查清单
```

## 部署测试页到 GitHub Pages

1. 在 GitHub 新建仓库，名字建议 `xhs`（私有即可，Pages 需要公开，或付费私有 Pages）
2. 本地推送：
   ```bash
   cd D:\projects\xhs
   git remote add origin git@github.com:<你的用户名>/xhs.git
   git branch -M main
   git push -u origin main
   ```
3. GitHub 仓库 → Settings → Pages → Source 选 `Deploy from a branch` → `main` / `/ (root)` → Save
4. 等待 1-2 分钟，站点地址为：`https://<你的用户名>.github.io/xhs/`
   （直接打开即测试页，客户做完题出报告）

## 配置商品链接（测试页内「获取完整报告」按钮）

两种方式任选其一：

- **方式 A（URL 参数，无需改文件）**：把商品链接拼到测试页网址后面：
  `https://<你的用户名>.github.io/xhs/?product=https://qianfan.xiaohongshu.com/...商品链接`
  然后将这个完整网址作为商品详情页里的「测试入口」链接。
- **方式 B（改文件）**：编辑 `index.html` 顶部 `PRODUCT_URL = ''`，填入千帆商品链接后重新 push。

## 上架流程（千帆）

1. 登录小红书商家后台（千帆）：https://ark.xiaohongshu.com
2. 按 `product/商品上架资料.md` 创建虚拟商品（标题/类目/详情文案/定价）
3. 上传商品主图（可用 `notes/img/08-商品卡.png` 或 `01-封面.png`）
4. 配置自动发货或兑换码，获取商品链接
5. 把商品链接填入测试页（见上），或直接放在笔记中
6. 发布笔记：按 `notes/笔记文案.md` 的标题/正文/标签，配图用 `notes/img/` 的 9 张图，发布时关联商品

## 注意事项

- 测试结果仅供自我探索与娱乐参考（页面已注明）
- 虚拟商品需在详情页说明「虚拟商品 · 付款后自动开通」，避免售后投诉
- 页面无任何外部依赖，可离线运行；部署后记得测一遍完整答题流程
