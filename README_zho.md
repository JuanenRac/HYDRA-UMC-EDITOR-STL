<!-- =============================================================================
HYDRA-UMC-EDITOR-STL - Desktop editor for the STL model libraries of HYDRA-UMC-STUDIO and HYDRA-UMC-SUITE
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL banner" width="100%">
</p>

# 📦 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | 🇨🇳 <b>简体中文</b> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 📦 浏览并编辑 HYDRA-UMC 生态系统真实的 STL 模型库

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg" alt="Language">
  <img src="https://img.shields.io/badge/Core-numpy--stl-brightgreen.svg" alt="Core">
  <img src="https://img.shields.io/badge/Desktop-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="Desktop">
  <img src="https://img.shields.io/badge/Tests-267%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.1.9-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-scaffolding-FFB020.svg" alt="Maturity">
</p>

---

**诚实检查——今天到底能真正运行什么：** `model_catalog.py`（对两个模型库
进行真实的、只读的发现）、`stl_ops.py`（通过 `numpy-stl` 进行真实的 STL
变更——变换/替换/移除/添加，外加为 3D 查看器摄像机取景服务的
`model_bounds()`）、`part_colors.py`（真实的按部件颜色附属文件）、
`stl_geometry.py`（真实的 Qt Quick 3D 几何体加载）和 `catalog_push.py`
（真实生成装配用 URDF，外加一个真实的 `POST /api/models/submit` HTTP
客户端）全部都针对真实生成的
STL 文件、以及在需要时一个真实的、会话范围的 `QGuiApplication` 进行了
测试（`pytest tests/`，267 个用例通过），并已针对本生态系统真实的
`HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` 检出进行了端到端的冒烟测试
（`--cli categories`/`models`/`parts` 针对真实的目录树；`transform`/`remove`
针对一份可丢弃的副本，绝不是真实的检出本身）。`qt_gui.py` 自己的
`EditorBridge` 也被直接测试（颜色 slot、颜色更改后选中状态被保留）。
`qml/Main.qml` 能够加载并渲染而不出现任何 QML 错误（已用
`QT_QPA_PLATFORM=offscreen` 无界面验证，包括把一个真实模型的部件加载到
3D 查看器中的情况），但 QML 场景图本身没有自己的自动化测试——驱动
一个真实的 Qt 事件循环在这里并未尝试，这与 HYDRA-UMC-UPDATER 自己的
README 已经为其自身 Qt Quick 层划出的诚实界限相同。

---

> **安全与安防现状:**本生态系统不是经认证的安全系统。目前尚无硬件 E-STOP 通路,没有由固件强制执行的限位或联锁,也没有经过验证的运动指令;固件映像使用 CRC-32 和 Ed25519 签名校验,发布构建会拒绝已公开的开发密钥(中继之后的工具头和扩展板仍运行 URTC 的引导程序,它们使用共享密钥的 HMAC-SHA256 而不是签名);TLS 与双向 TLS 均为可选项,默认关闭;自制电路板尚未组装或测试。在依赖此处任何说法来保障人身安全之前,请先阅读[安全基线](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)和[威胁模型](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)。

---

## 📋 速览

| | |
|---|---|
| 版本 | `0.1.9` |
| 成熟度 | 雏形 |
| 测试 | 267 (`python -m pytest tests -q`) |
| 技术栈 | Python / PySide6 / Qt Quick / numpy-stl |
| 目标 | 使用者的电脑 |
| 真实硬件 | 不适用：这里的内容不在硬件上运行 |

**跳转：** [概述](#-概述) · [架构](#-架构) · [安全与防护](#-安全与防护) · [接口](#-接口) · [配置](#-配置) · [快速开始](#-快速开始) · [测试](#-测试) · [故障排除](#-故障排除) · [仓库结构](#-仓库结构) · [相关项目](#-相关项目)

## 🚦 项目状态

每一行是本仓库的一个部分，灯号表示它今天做到了哪一步。内容依据仓库能够展示的证据（测试、构建、运行），而不是计划。

🟢 已完成并验证 · 🟡 可用，有已知限制 · 🟠 部分完成或尚未验证 · 🔴 未完成或不可用

| 领域 | 状态 | 在这里的含义 |
|---|---|---|
| 软件 | 🟠 | 目前只有结构和最初的部分，大部分工作尚未完成 |
| 测试 | 🟡 | 267 项自动测试，每次变更都会运行 |
| 真实硬件 | 🟡 | 不适用：这里的内容不在硬件上运行 |
| 文档 | 🟡 | 八种语言的 README，每次变更都会与清单核对 |

## 🎯 概述

HYDRA-UMC-EDITOR-STL 是一个小型桌面工具——默认是窗口化 GUI，也可用
`--cli` 使用完整的命令行——用于编辑构成 HYDRA-UMC-STUDIO 和
HYDRA-UMC-SUITE 所提供的每个机器人/机器模型的真实 STL 部件。这两个应用都
把各自的模型文件夹重新整理成了同一套真实的分类结构
（`robots-5-dof`/`robots-6-dof`/`robots-7-dof`、
`machine-pnp`/`machine-cnc`/`machine-laser`、
`heatedbeds`/`racks`/`vacuum-tables`，每个模型都有自己的
`metadata.json`，与其 `ATTRIBUTION.txt` 放在一起）——本工具读取的正是这套
真实结构，而不是另一份副本或自己的数据库。

真实的 Qt Quick 3D 视图会渲染所选模型的每一个可编辑部件
(`stl_geometry.py`，一个真实的 `QQuick3DGeometry`，直接从每个部件自己
的 STL 文件加载其三角形) —— 拖动可环绕旋转，滚轮可缩放，点击一个部件
即可选中它 (真实的 `View3D.pick()`，不是猜测)。摄像机会根据模型自己
真实的组合包围盒自动取景 (`stl_ops.py` 的 `model_bounds()`)，所以
400mm 的机器人底座和 5mm 的螺丝都能正确取景。

六个真实操作，每一个都由针对磁盘上真实检出的真实文件 I/O 支撑：

- **变换** —— 通过 `numpy-stl`（HYDRA-UMC-SUITE 自己的
  `render/mesh.py` 已经依赖的同一个库）平移/旋转/缩放一个部件的真实
  顶点数据，并原地保存回去。
- **更改颜色** —— 一个真实的、按部件保存的颜色标注
  (`part_colors.json`，本工具自己的一个附属文件)，会显示在 3D 视图
  中 —— 二进制 STL 本身并不可靠地携带颜色，所以这个附属文件才是真正的
  真相来源。HYDRA-UMC-STUDIO 自己的 `hooks/usePartColors.ts` 和
  HYDRA-UMC-SUITE 自己的 `render/part_colors.py` 都会读回这同一个文件，
  所以在这里保存的颜色也会到达它们真正的 3D 查看器中，而不仅仅是本工具
  自己的预览。
- **替换** —— 用另一份真实的 STL 文件覆盖一个部件。
- **移除** —— 把一个部件从模型中取出。
- **添加** —— 把一份新的真实 STL 文件带入一个模型。
- **推送到服务器** —— 把所选模型当前可编辑的部件提交到一个正在运行的
  HYDRA-UMC-SERVER 真实的模型提交目录（`catalog_push.py`，
  `POST /api/models/submit` —— 需要管理员登录，与 HYDRA-UMC-EDITOR-URDF
  自己等效的功能相同）。由于该端点自身的契约是为 URDF 设计的，这里会把
  部件包装进它能接受的最小真实 URDF 中：一个根链接，外加每个部件一个
  未加关节的（`fixed`）子链接，因为每个部件的真实位置已经烘焙在它自己的
  STL 顶点中 —— 绝不是凭空捏造的姿态。
- **悬浮视图工具栏** —— 选择、移动（真实可拖动的三轴 gizmo）、编辑（旋转/缩放）、颜色、添加、删除、固定（永久保存移动/旋转/缩放）、复制、粘贴和剪切，直接位于 3D 视图内。热床、真空台和机架是相互独立的尺寸变体，因此视图只显示所选的那一个，而不是全部叠在一起。
- **装配视图** —— 机器人、CNC、PnP 和激光模型会以原位姿态直接装配好打开（读取此检出旁 HYDRA-UMC-SUITE 自己的运动学，仅用于显示）；工具栏按钮可切换到原始部件进行编辑。

**推送与变换的限制：** 只会上传 `.stl` 零件（其余的会被报告），整个上传必须不超过服务器 50 MB 的请求上限，并且模型只保存在服务器的目录中（HYDRA-UMC-STUDIO 目前不会读取）。单位姿态适用于相互独立的零件（热床、机架、真空台）；机器人或机器的零件保存在各自的连杆坐标系中，因此到达时会堆叠在原点且没有关节。建议使用 `https://` 主机（用 `HYDRA_UMC_PASSWORD` 或密码提示代替 `--password`）。变换先缩放，再绕 X、Y、Z 旋转，最后平移；旋转绕文件原点进行，而不是绕零件中心。

**任何东西都不会被永久删除。** 移除或替换会先把真实的原始文件移动到该
模型自己的 `.trash/` 子文件夹中——这与本生态系统内部工作惯例早已遵循的
"绝不销毁，先移到一边"纪律相同，只是在这里作为一项真实的产品功能实现，
而不仅仅是一个内部习惯。

## 🧩 在 HYDRA-UMC 中的角色

**HYDRA-UMC-EDITOR-STL** 是桌面工具，用来编辑 HYDRA-UMC-STUDIO 和 HYDRA-UMC-SUITE 所带的每个机器人和机器模型的真实 STL 零件。它按原样读取这两个模型文件夹，在 Qt Quick 3D 查看器中显示模型，并在磁盘上变换、改色、替换、移除或添加零件，原文件被移到一旁而不是删除。完成的模型可以推送到 HYDRA-UMC-SERVER 的模型目录。

## 🏛️ 架构

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-EDITOR-STL architecture" width="100%">
</p>

### 架构与设计决策

- **两个真实库，一个发现模块。** `model_catalog.py` 自己的
  `LIBRARIES` 常量列出了本工具编辑的两棵真实目录树
  （`HYDRA-UMC-STUDIO/public/models/`、
  `HYDRA-UMC-SUITE/assets/meshes/`）——以后再加入第三个库，意味着在
  那里加一条记录，而不是再实现第二套发现逻辑。
- **`stl_ops.py` 是唯一会修改文件的地方。** `model_catalog.py`
  严格保持只读；`--cli` 和 Qt Quick 桥接层调用的是完全相同的
  `transform_part()`/`replace_part()`/`remove_part()`/`add_part()`
  函数，因此 GUI 永远不能做任何命令行本身做不到的事。
- **是真正的 STL，而不仅仅是以 `.stl` 结尾的文件名。**
  `is_real_stl()` 在把候选的替换/新增文件复制进真实模型文件夹之前，
  会真的用 `numpy-stl` 去解析它——而且，在编写本项目自己的测试时发现
  的一个真实漏洞是，它还会拒绝**0 三角形**的解析结果：`numpy-stl`
  自己的 ASCII 回退路径对任意垃圾字节并不会抛出异常，而是悄悄把它们
  解析成一个空网格，所以仅靠一个简单的 try/except 本会放行一个根本
  不是 STL 的文件。
- **默认 Qt Quick GUI，`--cli` 供无显示器环境使用。** `main.py`
  只在非 `--cli` 路径上导入 PySide6，因此
  `--cli categories`/`models`/`parts`/`transform`/`replace`/
  `remove`/`add` 可以在完全没有显示器或 Qt 运行时的机器上运行。
- **与 HYDRA-UMC-UPDATER 完全相同的真实视觉外壳。** `qml/Main.qml`
  按项目所有者本人的明确要求，原样复用了该项目自己的
  `GameButton`/`GameCombo`/`SectionPanel` 组件及其深色青/蓝/琥珀/红
  主题——本生态系统中的新 PC 工具应当给人以"同一个工具"的感觉，而不是
  另行设计的一个。
- **生态系统根目录，而非写死的路径。** 就像 HYDRA-UMC-UPDATER 自己的
  工作区根目录一样，本项目自身的父目录就是默认值（`main.py` 的
  `default_ecosystem_root()`），始终可被覆盖（`--cli` 上的 `--root`，
  GUI 中的"浏览"），并且会在多次 GUI 启动之间被记住（`settings.py`）。

## 🔒 安全与防护

| 威胁 | 防御 | 位置 |
|---|---|---|
| 替换或移除零件时丢失零件 | 原文件会先被移到模型的 `.trash/` 文件夹，绝不会被删除；可以恢复，清空回收站需要明确确认 | `stl_ops.py` |
| 不是 STL 的文件，或跳出模型文件夹的零件名 | 替换或新增的文件会先被解析，没有三角形或被截断时会被拒绝；零件名必须是模型文件夹内简单的 `.stl` 文件名；会产生非有限顶点的变换不会改变任何内容 | `stl_ops.py`, `mesh_check.py` |
| 服务器密码出现在 shell 历史或进程列表中 | 不建议使用 `--password`；不用它时，密码会从 `HYDRA_UMC_PASSWORD` 读取或在无回显的情况下询问；使用 `https://` 主机可避免明文发送 | `main.py`, `catalog_push.py` |
| 过大或卡住的上传 | 整个上传必须不超过 49 MiB（服务器限制为 50 MB），每个请求有 20 秒的时限；只发送 `.stl` 零件，其余的会被报告 | `catalog_push.py` |
| 增长或包含数据的日志 | 主目录中一个 256 KiB、保留两份副本的滚动日志 | `diagnostics.py` |

**它绝不做的事：** 编辑你所指定的模型文件夹之外的任何内容，或永久删除零件。向服务器的推送是按其文档化的契约编写的，尚未在真实服务器上试过。

默认情况下，把机器人或机器模型发送到目录会被拒绝，因为其零件会堆叠在原点；只有独立零件的类别（床、机架）可以通过。拒绝时会说明原因，非 `.stl` 的零件会被报告。

## 🔌 接口

| 主题或路由 | 内容 |
|---|---|
| `--cli categories \| models \| parts <library> [...]` | 列出现有内容：类别、某类别下的模型、模型的零件文件（供机器读取用 `--json`）；库为 `studio` 或 `suite` |
| `--cli transform <library> <category> <model> <part> [--tx --ty --tz --rx --ry --rz --scale]` | 就地平移、旋转和缩放一个零件：先缩放，再绕 X、Y、Z 旋转，最后平移，旋转以文件原点为中心 |
| `--cli replace \| remove \| add` | 用另一个 STL 替换零件、把某个零件移到 `.trash/`，或引入新的 STL（`--dest-filename` 可重命名） |
| `--cli push <library> <category> <model> --host --username` | 把模型的可编辑零件发送到服务器的 `POST /api/models/submit`（需管理员登录；`--port` 默认 3000，`--server-category`，`--overwrite`） |
| `--root <folder>` | 并排包含 `HYDRA-UMC-STUDIO` 和 `HYDRA-UMC-SUITE` 的生态系统根目录；默认是本工具的上级文件夹 |

`--cli push` 的 `--allow-stacked-push` 以及推送窗口中的 **强制** 复选框（默认关闭，支持八种语言），可让机器人或机器模型即使零件会堆叠在原点也能发送到目录。

## ⚙️ 配置

没有服务器，也没有需要手工编辑的配置文件：窗口把选择记在一个文件里，每个模型把颜色保存在一个附属文件中。

| 变量 | 默认值 | 设置内容 |
|---|---|---|
| `~/.hydra_umc_editor_stl_settings.json` | 无 | 窗口中选择的生态系统根目录和语言，跨启动记住 |
| `part_colors.json` (in each model folder) | `#9fb4c9` | 每个零件的颜色；二进制 STL 不带颜色，STUDIO 和 SUITE 读取同一个文件 |
| `HYDRA_UMC_PASSWORD` | 未设置 | `--cli push` 使用的服务器密码，避免出现在命令行中 |
| `~/.hydra_umc_editor_stl.log` | 256 KiB x 3 | 窗口和命令行的滚动日志 |

## 🚀 快速开始

需要 Python 3.10 或更高版本。第一行会创建带 GUI 附加项的虚拟环境并运行检查和测试；Windows 上有 `build.bat` 和 `run.bat`。

```bash
./build.sh                                    # creates .venv, installs the package with the GUI extra, checks and tests
./run.sh                                      # the windowed editor
./run.sh --cli categories studio              # lists the categories of the STUDIO library (use suite for the SUITE one)
./run.sh --cli parts studio robots-6-dof ar3  # lists the part files of one model
```

## 🧪 测试

运行 `python -m pytest tests -q` 会执行 267 个自动测试。 不需要硬件，也不需要这台机器以外的任何东西。

CI 运行 `HYDRA_UMC_CI=1 python tools/ci_validate.py`，检查清单、文档、八个 README 和图片。

## 🏗️ 构建与发布

```bash
chmod +x build.sh   # 一次性
./build.sh          # 创建 .venv，pip install -e ".[dev,gui]"，编译检查并测试
./run.sh                                                    # 窗口化 GUI（默认）
./run.sh --cli categories studio                            # 列出某个库中的分类
./run.sh --cli models studio robots-6-dof                   # 列出某个分类中的模型
./run.sh --cli parts studio robots-6-dof ar3                 # 列出某个模型的真实部件文件
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /路径/new.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /路径/new.stl
./run.sh --cli lite studio robots-6-dof ar3 --ratio 0.2          # 在 .lite/ 中生成轻量副本(原件不动)
./run.sh --cli diff studio robots-6-dof ar3 base_link.STL --svg diff.svg   # 与 .trash/ 中保留的版本比较
./run.sh --cli sync-libraries --master studio --target suite   # 仅显示计划;加 --apply 才写入,不删除任何内容
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin
```

在 Windows 上：先 `build.bat`，然后 `run.bat`（GUI）或
`run.bat --cli ...`；双击 `run-gui.vbs` 可无控制台启动 GUI。

`library` 始终是 `studio` 或 `suite`；`category`/`model` 是
`categories`/`models` 刚刚打印出来的真实文件夹名。`--root` 会为任意
`--cli` 命令覆盖生态系统根目录（默认：本工具自身的父目录）。

## 🩺 故障排除

- `categories`/`models`/`parts` 什么都不打印：生态系统根目录实际上并未
  将 `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` 作为同级目录包含在内——请显式
  传入 `--root`，或在 GUI 中使用"浏览"。
- `transform`/`replace`/`add` 报错 "not a real, parseable STL file"：
  源文件实际上不是有效的 STL（或者是一个 0 三角形的 STL）——请在真实的
  CAD/网格查看器中打开它以确认。
- 一个被移除/替换的部件没有从 GUI 自己的部件列表中消失：它确实已经在
  磁盘上被移动到了 `.trash/`——部件列表只显示当前真实的顶层文件，
  `.trash/` 子文件夹被有意排除在外。

| 你看到 | 原因 | 处理 |
|---|---|---|
| “推送成功但服务器没有返回 slug”，或登录错误 | 服务器拒绝了该账户（推送需要管理员）、它不是 HYDRA-UMC-SERVER，或返回的不是 JSON 对象 | 使用真实 HYDRA-UMC-SERVER 的管理员账户及其地址和端口 |
| “该变换会产生非有限顶点（是否过大？）——未作任何更改” | 缩放或平移过大，数值已无法放入 32 位浮点数 | 使用较小的值 |
| “清空回收站需要明确确认” | 未经你确认，不会永久删除任何内容 | 从 `.trash/` 恢复该项，或在窗口中确认清空 |

## 📂 仓库结构

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-EDITOR-STL" width="100%">
</p>

<details>
<summary>目录树的文本版本</summary>

```text
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/   源代码
│   ├── __init__.py             包版本
│   ├── model_catalog.py        对两个模型库的真实、只读发现
│   ├── stl_ops.py              真实的 STL 变更：变换/替换/移除/添加，.trash/ 备份
│   ├── catalog_push.py         装配用 URDF + POST /api/models/submit 的 HTTP 客户端
│   ├── settings.py             持久化的生态系统根目录和语言偏好
│   ├── i18n.py                 真实、完整的 GUI 翻译（8 种语言）
│   ├── diagnostics.py          主目录中的轮转日志与窗口槽函数的保护
│   ├── qt_gui.py               建立在真实 model_catalog.py/stl_ops.py 核心之上的 Qt Quick 桥接层
│   ├── qml/Main.qml            主题化的桌面外壳，与 HYDRA-UMC-UPDATER 共享
│   ├── main.py                 分发：默认 GUI，--cli 用于 categories/models/parts/transform/replace/remove/add/push
│   ├── assembly.py             由 STL 零件组装出的机器视图 (原位姿态)
│   ├── mesh_check.py           推送到目录前的网格检查
│   ├── decimate.py             零件的轻量副本
│   ├── mesh_diff.py            零件修改前后的数值与图像对比
│   ├── library_sync.py         使一个模型库与另一个保持一致
│   ├── part_colors.py          按零件的颜色标注 (二进制 STL 本身不带颜色)
│   └── stl_geometry.py         把 STL 文件的真实三角形作为 Qt Quick 3D 几何体
├── tests/                      针对真实生成的 STL 文件的真实测试
├── docs/                       项目文档
├── images/                     媒体和应用图标
├── tools/                      项目工具和 CI 检查
├── .github/                    CI 工作流和 Issue 模板
├── build.sh / build.bat        venv + 可编辑安装（dev+gui 附加项）+ 编译检查 + 测试
├── run.sh / run.bat            默认 GUI / CLI 入口点
├── run-gui.vbs                 无控制台窗口的 Windows 图形启动器
├── bump_version.py             显式提升版本
├── bump_manifest_version.py    将 hydra-umc.project.json 的版本与原生版本同步（--sync）
├── CHANGELOG.md                每个版本的变更
├── build-test.sh               不修改内容的构建检查
├── hydra-umc.project.json      清单：版本、成熟度、系列
├── pyproject.toml              包的元数据
└── test.sh                     不修改内容的构建检查
```

</details>

## 🗺️ 路线图与已知限制

**当前已知限制**

- 一个打包好的独立 GUI 可执行文件（PyInstaller，遵循与
  HYDRA-UMC-SUITE 相同的 `build_exe.bat`/`.sh` 约定）。
- 基于某次会话自己的 `.trash/` 历史记录的撤销/重做，而不是手动恢复文件。

## 🌍 语言

本 README 和仓库文档提供八种语言：英语、西班牙语、德语、法语、意大利语、日语、中文和葡萄牙语（葡萄牙）。它们同时编写，并由 CI 检查八个文件拥有相同的章节和相同的链接。

## 🔗 相关项目

本项目是同一作者（JuanenRac / Electro Hobby 3D）的 HYDRA-UMC 机器人生态系统的一部分。值得了解，因为某个请求实际上可能是关于这些项目之一，而不是这个仓库本身。

**父项目**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — 拥有本编辑器读写的两个真实模型库之一（`public/models/`）。

**直接相关**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — 拥有本编辑器读写的第二个真实模型库（`assets/meshes/`），与 STUDIO 保持完全相同的分类结构。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 同一模型目录的姐妹桌面编辑器，负责 URDF/运动学一侧，而非本工具编辑的原始 STL 几何体。
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — 拥有真实的 `POST /api/models/submit` 端点，本编辑器会把完成的编辑推送到该端点（`catalog_push.py`，GUI 中的“推送到服务器...”或 `--cli push`）。

**同样属于本生态系统**

*核心硬件与平台*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — 机器人手臂主板设计——CM5 主机 + 双核 STM32H745,目标是通过 CAN-OTA/SPI-OTA 协调最多 8 条工具臂(固件处于早期阶段,尚无已组装的电路板)。
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — 面向 CM5 的可复现 Raspberry Pi OS 产品层：只读代理、经过校验的配置/配置文件、WiFi 首次接触配网。
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — 每个桥接都据此校验自身指令的共享 JSON-Schema 契约与软件作业门限边界(并非经认证的安全功能)。
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — 面向外部机器连接器的声明式适配器清单注册表及其校验器；在不取代工业网关项目的前提下，把 SDK 自身的契约理念扩展到外部机器。

*核心后端与客户端*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — 原生 Android 控制应用，具备生物识别登录和一个配对的 Wear OS 伴侣应用。
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS 控制应用（Flutter），具备实时 WebSocket 同步。
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — 面向 CM5 本机内置 7 英寸 DSI 触摸屏的原生触控 UI。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 图形化桌面 URDF 创建/编辑器，具备 GitHub/本地源加载和实时 3D 预览编辑。
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — 通过 VDA 5050 MQTT 发布者为 AGV/AMR 车队提供的协调边界(仅针对仿真车队测试)。
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — 具备 GRBL 状态/控制字节访问能力的高层 CNC 单元协调器(仅针对模拟器测试)。
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — 面向足式/人形机器人的协调边界,带有 Boston Dynamics Spot 指令发送器(仅针对模拟器测试)。
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — 读取 3 路钥匙/外壳/联锁 GPIO 信号的激光单元协调器(仅针对模拟芯片测试;无法使激光器上膛或发射)。
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — 面向 OpenPnP 贴片的安全高层板级流程协调器。
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — 面向 Moonraker/Klipper 3D 打印机的安全协调边界，具备真实的受控任务命令。
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — 带有惰性导入 rclpy ROS 2 传输层的协调器(尚未在 ROS 2 环境中运行)。
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — 面向搭载摄像头的无人机的协调边界,带有 MAVLink 指令发送器(仅针对模拟器测试)。

*URTC 工具平台*
- **[URTC](https://github.com/JuanenRac/URTC)** — 面向 Universal Robot Tool Controller 实体 PCB 的固件，通过 CAN 总线支持 25 种以上的工具配置。
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — 面向 URTC 板卡的桌面 GUI 刷写工具，支持 CAN-OTA 及完整芯片级 SWD/JTAG。
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — 面向 URTC 板卡的桌面实时 CAN 总线诊断工具，每个工具配置一个面板。
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — 通过 Web Serial API 实现的、无需本地安装的浏览器版 URTC-TESTER 替代方案。
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — URTC CAN 总线前的网关：允许的标识符列表、速率限制和会话密钥；软件已在计算机上测试，尚未在真实总线上测试。

*视觉 AI 节点（Hailo-8）*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — Hailo-8 视觉流水线的集成中枢，具备逐阶段的真实硬件就绪检查。
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — 具备 Hailo 架构/校验和安全加载验证的真实已编译模型注册表。
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — 具备真实 HailoRT 集成边界的真实 GStreamer 流水线 + MediaMTX 配置生成器。
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — 以区域状态为授权条件的 Position-Based Visual Servoing 修正律;尚无摄像头位姿估计。
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — 从文件读取物体位置的 v0 区域入侵、校准新鲜度与 E-STOP 请求逻辑;没有检测器为其供数,也尚未连接任何物理 E-STOP。

*认知 AI 节点（Hailo-10）*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — Hailo-10 认知流水线（LLM/VLA/语音编排）的集成中枢。
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — 面向 Vision-Language-Action 模型的真实动作令牌编解码与轨迹生成。
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — 具备受限、需确认的 Watch 中继的真实语音前端（VAD + 意图解析器）。
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — 基于规则的真实任务分解与针对 MCU 错误码的语义化错误恢复。
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — 仅依赖标准库、针对本生态系统自身 Markdown 文档的真实 TF-IDF 文档检索。
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — 面向生态系统自身、受策略门控的本地 AI 维护技师——观察、诊断并提出修复建议；最高的两个风险等级被有意保留为尚未实现。

*编排与集群*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — 具备真实 gRPC/Protobuf 健康报告契约与任务状态机的集成中枢。
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — 基于真实 HTTP API 的、具备去重能力的真实优先级任务队列。
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — 具备重试/退避与身份不匹配检测的真实基于 gRPC 的车队健康看门狗。
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — 具备真实障碍物/工作空间碰撞校验的真实基于 RRT 的 3D 路径规划器。
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — 真实的 CRDT LWW-Element-Map 状态同步，针对多单元收敛性进行了基于属性的测试。

*数字孪生与仿真*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — 真实的物理仿真数字孪生，消费 HYDRA-UMC-EDITOR-URDF 生成的 URDF 模型。
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — 消费同一批 URDF 模型来驱动自己的物理仿真。
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — 基于这些同样的模型生成训练数据。
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — 在仿真与真实硬件之间带有软件碰撞联锁的硬件在环路由器(未在真实硬件上测试)。

*数据与分析*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — 基于 sqlite3 的真实时间序列存储，具备真实的写入/查询 HTTP API。
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — 具备漂移监测的真实 FFT + 统计基线异常检测器。
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — 基于 DATALAKE 历史数据的真实 OEE/可用性计算，具备可复现的 CSV 导出。
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — 面向 DATALAKE 的真实 CAN/WebSocket 摄取流水线，具备序列去重。

*工业网关*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — 中继到工业协议的集成中枢，具备真实的命令白名单/背压层。
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — 真实的 OPC-UA 地址空间，已通过真实的二进制协议客户端会话验证。
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — 具备可选的按客户端认证和主题 ACL 的真实 MQTT 代理。
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — 具备降级模式输出的真实 MTConnect `/probe` 和 `/current` XML 端点。

*配套工具与生态系统运维*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — 建立在 DATALAKE/ANOMALY-DETECTOR 之上的智能摘要与异常高亮面板，具备诚实的统计学回退方案。
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — 具备真实、稳定退出码契约的车队 CLI，是 HYDRA-UMC-SERVER 自身 API 的真正实时客户端。
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — 带有触觉提醒模式与配对手机语音中继的 WearOS 伴侣应用(尚未在实体手表上运行)。
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — 面向板卡安装机架的固件，具备真实的工具 ID 解码和 Smart Idle 预热逻辑。
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — 固件加上一个真实的 Python 视觉配套程序，用于热成像/RGB 检测工具头。
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — 发现、克隆并更新本生态系统中每个仓库的管理型桌面工具，也是本项目自身 Qt Quick 视觉外壳的来源。
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux 桌面工具，构建预装了生态系统最新版本、可直接刷写的 CM5 镜像，具备 Raspberry Pi Imager 风格的首次启动 Wi-Fi/用户/SSH 配置。
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — 维护事件协调器：一个低权限边缘角色收集经过脱敏的库存/健康快照，一个控制平面角色以只读方式展示它并请求 AI 提供商给出诊断建议——绝不应用补丁，也不部署任何东西。
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — 可复现的开发主机（Raspberry Pi 5 / CM5），存储生态系统的源代码，并在一个持久化队列下执行受限的构建/测试任务；这是一个专用的开发角色，明确不是一台运行中的 CM5。

## 📚 文档

更多阅读：

* [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - 每一个真实的 `--cli` 子命令，逐参数说明。
* [生态系统的安全基线](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [生态系统的威胁模型](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [本仓库的更新日志](CHANGELOG.md)
* [本仓库的许可证](LICENSE.md)

## 🤝 参与贡献与社区

* 提交 pull request 之前，请运行 `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py`（或 `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`）：它必须输出 `CI_VALIDATION=PASS`。此检查不要运行 `build.sh` 或 `build.bat`；构建不是检查。
* 八个 README 由 HYDRA-UMC-DOCS 中的同一个源生成；请勿手工编辑。修改源文件，再用 `tools/make_readmes.py` 重新生成。
* 不要在 README 中声称尚未运行过的内容：属实时请写“仅模拟”或“尚未在硬件上试过”。
* 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md)、[SECURITY.md](SECURITY.md) 和 [SUPPORT.md](SUPPORT.md)。

## 👤 作者

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 许可证

GPL-3.0-or-later - [LICENSE](LICENSE).
