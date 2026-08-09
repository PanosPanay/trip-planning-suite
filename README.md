# Trip Planning Suite

一套可移植的端到端旅行规划 Skill 套件：从多出发地机票比较、目的地建议、携程酒店检索和对话式行程迭代，一直到详细 Markdown、可点击动态地图、可编辑 HTML 线路图、高清分享图片和 PDF。

## 给 AI 安装

把本仓库链接发给支持本地命令和 Skill 的 AI，并告诉它：

> 克隆这个仓库，阅读 `INSTALL.md`，运行完整安装与验证；不使用降级模式。

也可以手动执行：

```bash
git clone https://github.com/PanosPanay/trip-planning-suite.git
cd trip-planning-suite
python3 scripts/install_suite.py --force
python3 scripts/verify_suite.py --run-external-tests
```

安装器会同时安装：

- `trip-planning-orchestrator`
- `ctrip-flight-prices`
- `ctrip-hotel-search`
- `trip-route-poster`
- `trip-itinerary-pdf`
- `interactive-trip-planner`，通过 [Red Skill](https://redskill.xiaohongshu.net/install.md) 安装并校验版本

缺少任一必要 Skill 或运行时，验证器都会失败，不会静默输出低配版本。

## 完整工作流

1. 查询机票，比较多出发地价格、航班时间和有效游玩时长。
2. 给出目的地候选，结合季节、预算、交通和人流做建议。
3. 通过对话逐步确认路线、景点、节奏、备选方案和风险。
4. 查询携程酒店，复核房型、间数、价格、早餐、到店限制和取消政策。
5. 维护一份规范的详细行程 Markdown。
6. 使用 `interactive-trip-planner` 生成可点击、可分天查看的动态地图。
7. 从真实坐标和道路数据生成 `route-poster.html`，先在浏览器中修改和验收，再导出高清横版与竖版图片。
8. 将 Markdown 与批准后的高清线路图导出为 PDF，并逐页渲染检查。

## 线路图原则

- HTML 是线路图的编辑源，PNG 只是用户批准后的派生文件。
- 默认路线用实线，互斥备选路线用虚线。
- 景点、住宿、编号、里程和车程标注不得遮挡路线或彼此重叠。
- 横版基础画布为 `1920x1350`，竖版为 `1440x2200`；默认以 2 倍像素密度导出。

更多安装说明见 [INSTALL.md](INSTALL.md)。

