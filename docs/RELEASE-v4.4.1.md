# v4.4.1 — 灵动岛默认关闭与 macOS 跨屏拖拽修正

> **状态**：待发布。tag `v4.4.1`；三端构建由 tag 触发，产物 size/sha256 对账进 `update.json` 由另一次提交完成。
> 上一版 v4.4.0 是试验先行版。本版是它的用户反馈补丁：灵动岛不再默认悬浮，macOS 混合 DPI 跨屏拖拽不再跟不上鼠标。

## 为什么有这个版本

两条实机反馈：

1. **灵动岛一直悬浮**，只能缩小不能关。新装 / 出厂默认改成不展示；状态栏托盘与 macOS Dock 右键可开关。
2. **从小屏拖到大屏时鼠标偏移**（macOS 混合 DPI）。跨窗换算不再乘小屏 DPR。

无新增配置键、无数据迁移。已显式开过灵动岛的老配置原样保留。

## 下载哪个

| 你是 | 下这个 |
|---|---|
| Windows 大多数人 | `…-webm-chat-setup.exe`（安装版，推荐） |
| Windows 不想安装 | `…-webm-chat-portable.zip`（解压即用） |
| macOS（Apple 芯片） | `…-webm-chat-macos-arm64.zip` |
| Linux | `…-webm-chat-linux-x86_64.zip` |

名字里带 `webm-chat` = 带 AI 对话；不带 `-chat` 的 `webm` 版是纯桌宠。

## 改了什么

- **灵动岛默认关**。`dynamic_island.enabled` 出厂 `false`，与设置页缺省读法对齐。overlay 托盘与 Dock 补「灵动岛」勾选。
- **macOS/Linux 跨屏映射走逻辑点**。Windows 仍走物理像素。小屏 DPR 2 → 大屏 DPR 1 时宠跟着光标。
- 详细证据见 [`PR-REPORT-V4.4.1-ISLAND-CROSSDPI-2026-11-03.md`](PR-REPORT-V4.4.1-ISLAND-CROSSDPI-2026-11-03.md)。

## 升级说明

直接覆盖安装或换绿色包。配置目录不变。从 v4.4.0 升级无额外操作。
