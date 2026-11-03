# PR 报告：v4.4.1 灵动岛默认关闭与 macOS 跨 DPI 拖拽修正（2026-11-03）

> **基线**：`34d810b`（v4.4.0 `update.json`）
> **分支**：`main`　**日期**：2026-11-03
> **范围**：灵动岛默认值 + 托盘/Dock 开关 + 跨窗映射平面分岐

## 一、修改文件说明

| 文件 | 增删 | 改了什么 + 为什么 |
|---|---|---|
| `pet/config.py` | +7/−2 | `_default_dynamic_island_data()["enabled"]` True → False；新装不再悬浮胶囊 |
| `pet/app.py` | +49/−13 | `set_dynamic_island_enabled` / `_island_enabled_from_config`；Dock「显示灵动岛」；缺省读法 False |
| `pet/overlay_shell.py` | +66/−21 | overlay 托盘灵动岛开关；`_window_mapping_scale`：macOS/Linux=1、Windows=DPR |
| `pet/features.py` | +2/−2 | 注释：enabled 缺省已对齐 False |
| `docs/SETTINGS-CHANGE-GATES.md` | +11 | 2026-11-03 已有键默认值变更 |
| `tests/test_dynamic_island_revamp.py` | +9 | `test_default_dynamic_island_is_hidden` |
| `tests/test_tray_settings_deferred_dispatch.py` | +21 | overlay 托盘灵动岛开关等菜单关闭 |
| `tests/test_requested_regressions.py` | +32 | Dock 菜单能关灵动岛 |
| `tests/test_overlay_hosts_multiscreen.py` | +5 | Windows 物理域测试强制 `_IS_WINDOWS=True` |
| `tests/test_overlay_cross_dpi_macos.py` | +新 | macOS 逻辑平面映射 / 负原点布局 / 松手交接 |
| `tests/test_settings_ia_first_cut.py` | +4 | 岛相关行测试事先开岛 |
| `tests/test_settings_stale_form_exit.py` | +3 | 同上 |
| `pet/__init__.py` | 4.4.0 → 4.4.1 | 发版版本号 |

**未改**：`update.json` 仍指 v4.4.0 附件；CI 出包后另交 size/sha256。`assets/icon.ico` 为本机打包旁路重生成，不进本版。

## 二、性能分析

- **稳态**：灵动岛默认不建窗，新装少一个胶囊窗 + 采样槽。已开启用户路径不变。
- **拖拽映射**：每次跨窗多一次 `if not _IS_WINDOWS`，无新线程/磁盘/网络。
- **触发**：托盘/Dock 点一次写盘 + `_sync_dynamic_island`；拖拽每拍走既有映射函数。

## 三、实机运行记录

- **macOS arm64**：`/Applications/dsh-pet-standalone-webm-chat.app` 本地打包安装。灵动岛默认不出现；托盘「灵动岛」可开关。
- **跨屏**：小屏 1450×825 @DPR2 + 大屏 1900×1030 @DPR1（负原点）。修正前乘 DPR 跟不上鼠标；修正后逻辑平面测试绿。
- **门**：`ruff` 清洁；跨屏族 + 灵动岛托盘/Dock 用例本机过。Windows 真机拖拽由 tag 触发的 CI 包验证。
