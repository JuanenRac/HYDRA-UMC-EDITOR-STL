<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL 横幅" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | 🇨🇳 <b>简体中文</b> | <a href="README_jpn.md">🇯🇵 日本語</a></p>

### 📦 浏览并编辑 HYDRA-UMC 生态系统真实的 STL 模型库

<p align="center">
  <img src="https://img.shields.io/badge/许可证-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/语言-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/核心-numpy--stl-brightgreen.svg" alt="numpy-stl 核心">
  <img src="https://img.shields.io/badge/桌面-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="PySide6 Qt Quick 桌面 GUI">
</p>

> **v0.0.4。** 下面描述的真实 CLI/GUI 核心是真正实现并经过测试的，包括一个
> 真实的 Qt Quick 3D 查看器，支持点击选中、按部件着色、变换、替换、移除、
> 添加，以及把一个编辑好/新增的模型真正推送回 HYDRA-UMC-SERVER 自己真实的
> `POST /api/models/submit` 目录（与 HYDRA-UMC-EDITOR-URDF 对 URDF 模型
> 所用的同一个真实集成点）。它还不会把部件保存的颜色传播到 STUDIO/SUITE
> 自己真实的 3D 查看器中 —— 这是真实、有明确范围的未来工作（见路线图），
> 并未被悄悄假定为已完成。

**诚实检查——今天到底能真正运行什么：** `model_catalog.py`（对两个模型库
进行真实的、只读的发现）、`stl_ops.py`（通过 `numpy-stl` 进行真实的 STL
变更——变换/替换/移除/添加，外加为 3D 查看器摄像机取景服务的
`model_bounds()`）、`part_colors.py`（真实的按部件颜色附属文件）、
`stl_geometry.py`（真实的 Qt Quick 3D 几何体加载）和 `catalog_push.py`
（真实生成装配用 URDF，外加一个真实的 `POST /api/models/submit` HTTP
客户端）全部都针对真实生成的
STL 文件、以及在需要时一个真实的、会话范围的 `QGuiApplication` 进行了
测试（`pytest tests/`，48 个用例通过），并已针对本生态系统真实的
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

## 1. 🛠️ 技术概览

HYDRA-UMC-EDITOR-STL 是一个小型桌面工具——默认是窗口化 GUI，也可用
`--cli` 使用完整的命令行——用于编辑构成 HYDRA-UMC-STUDIO 和
HYDRA-UMC-SUITE 所提供的每个机器人/机器模型的真实 STL 部件。这两个应用都
在 2026-09 把各自的模型文件夹重新整理成了同一套真实的分类结构
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
  中 —— 二进制 STL 本身并不可靠地携带颜色，而且本生态系统自己的
  STUDIO/SUITE 查看器也不会解析那种约定，所以这目前是一个诚实的、
  仅限 EDITOR-STL 的预览，尚未传播到它们真正的 3D 查看器中。
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

**任何东西都不会被永久删除。** 移除或替换会先把真实的原始文件移动到该
模型自己的 `.trash/` 子文件夹中——这与本生态系统内部工作惯例早已遵循的
"绝不销毁，先移到一边"纪律相同，只是在这里作为一项真实的产品功能实现，
而不仅仅是一个内部习惯。

## 2. 🧱 架构与设计决策

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

## 📂 目录结构

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # 对两个模型库的真实、只读发现
│   ├── stl_ops.py           # 真实的 STL 变更：变换/替换/移除/添加，.trash/ 备份
│   ├── catalog_push.py       # 装配用 URDF + POST /api/models/submit 的 HTTP 客户端
│   ├── settings.py          # 持久化的生态系统根目录和语言偏好
│   ├── i18n.py               # 真实、完整的 GUI 翻译（7 种语言）
│   ├── qt_gui.py             # 建立在真实 model_catalog.py/stl_ops.py 核心之上的 Qt Quick 桥接层
│   ├── qml/Main.qml          # 主题化的桌面外壳，与 HYDRA-UMC-UPDATER 共享
│   └── main.py               # 分发：默认 GUI，--cli 用于 categories/models/parts/transform/replace/remove/add/push
├── tests/                    # 针对真实生成的 STL 文件的真实测试
├── docs/
│   └── CLI_REFERENCE.md      # 命令参考
├── images/                   # 媒体和应用图标
├── tools/
│   ├── build_test.py         # 不涉及版本变更的编译检查
│   └── ci_validate.py        # CI 使用的清单/更新日志/文档验证
├── build.sh / build.bat      # venv + 可编辑安装（dev+gui 附加项）+ 编译检查 + 测试
├── run.sh / run.bat          # 默认 GUI / CLI 入口点
├── run-gui.vbs               # 无控制台窗口的 Windows 图形启动器
├── bump_version.py           # 生态系统范围的"里程表"式版本递增（pyproject.toml + __init__.py）
└── bump_manifest_version.py  # 将 hydra-umc.project.json 的版本与原生版本同步（--sync）
```

## ⚙️ 构建与运行指南

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
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin --password ***
```

在 Windows 上：先 `build.bat`，然后 `run.bat`（GUI）或
`run.bat --cli ...`；双击 `run-gui.vbs` 可无控制台启动 GUI。

`library` 始终是 `studio` 或 `suite`；`category`/`model` 是
`categories`/`models` 刚刚打印出来的真实文件夹名。`--root` 会为任意
`--cli` 命令覆盖生态系统根目录（默认：本工具自身的父目录）。

**故障排查**

- `categories`/`models`/`parts` 什么都不打印：生态系统根目录实际上并未
  将 `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` 作为同级目录包含在内——请显式
  传入 `--root`，或在 GUI 中使用"浏览"。
- `transform`/`replace`/`add` 报错 "not a real, parseable STL file"：
  源文件实际上不是有效的 STL（或者是一个 0 三角形的 STL）——请在真实的
  CAD/网格查看器中打开它以确认。
- 一个被移除/替换的部件没有从 GUI 自己的部件列表中消失：它确实已经在
  磁盘上被移动到了 `.trash/`——部件列表只显示当前真实的顶层文件，
  `.trash/` 子文件夹被有意排除在外。

## 🚀 路线图

- 把一个部件保存的颜色（`part_colors.json`，见上文）传播到
  HYDRA-UMC-STUDIO/HYDRA-UMC-SUITE 自己真实的实时 3D 查看器中——这是
  真实的、独立的跨仓库工作。
- 一个打包好的独立 GUI 可执行文件（PyInstaller，遵循与
  HYDRA-UMC-SUITE 相同的 `build_exe.bat`/`.sh` 约定）。
- 基于某次会话自己的 `.trash/` 历史记录的撤销/重做，而不是手动恢复文件。

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
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — 机械臂主板本体：CM5 主机 + 双核 STM32H745，通过 CAN-OTA/SPI-OTA 编排最多 8 条工具臂。
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — 面向 CM5 的可复现 Raspberry Pi OS 产品层：只读代理、经过校验的配置/配置文件、WiFi 首次接触配网。
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — 每个 bridge 都据以校验自身命令的共享 JSON-Schema 契约与安全门边界。
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — 面向外部机器连接器的声明式适配器清单注册表及其校验器；在不取代工业网关项目的前提下，把 SDK 自身的契约理念扩展到外部机器。

*核心后端与客户端*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — 原生 Android 控制应用，具备生物识别登录和一个配对的 Wear OS 伴侣应用。
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS 控制应用（Flutter），具备实时 WebSocket 同步。
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — 面向 CM5 本机内置 7 英寸 DSI 触摸屏的原生触控 UI。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 图形化桌面 URDF 创建/编辑器，具备 GitHub/本地源加载和实时 3D 预览编辑。
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — 通过真实的 VDA 5050 MQTT 发布者实现的 AGV/AMR 车队协调边界。
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — 具备真实 GRBL 状态/控制字节访问的高层 CNC 单元协调器。
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — 面向足式/人形机器人的协调边界，具备真实的 Boston Dynamics Spot 命令发送器。
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — 读取 3 个真实的钥匙/围栏/联锁 GPIO 安全防护的激光单元安全协调器。
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — 面向 OpenPnP 贴片的安全高层板级流程协调器。
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — 面向 Moonraker/Klipper 3D 打印机的安全协调边界，具备真实的受控任务命令。
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — 具备真实、惰性导入的 rclpy ROS 2 传输层的安全协调器。
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — 面向带摄像头无人机的协调边界，具备真实的 MAVLink 命令发送器。

*URTC 工具平台*
- **[URTC](https://github.com/JuanenRac/URTC)** — 面向 Universal Robot Tool Controller 实体 PCB 的固件，通过 CAN 总线支持 25 种以上的工具配置。
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — 面向 URTC 板卡的桌面 GUI 刷写工具，支持 CAN-OTA 及完整芯片级 SWD/JTAG。
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — 面向 URTC 板卡的桌面实时 CAN 总线诊断工具，每个工具配置一个面板。
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — 通过 Web Serial API 实现的、无需本地安装的浏览器版 URTC-TESTER 替代方案。

*视觉 AI 节点（Hailo-8）*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — Hailo-8 视觉流水线的集成中枢，具备逐阶段的真实硬件就绪检查。
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — 具备 Hailo 架构/校验和安全加载验证的真实已编译模型注册表。
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — 具备真实 HailoRT 集成边界的真实 GStreamer 流水线 + MediaMTX 配置生成器。
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — 根据上游区域状态设置安全门的真实基于位置的视觉伺服校正律。
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — 具备校准新鲜度强制要求的真实区域越界检查与 E-STOP 请求。

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
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — 在仿真与真实硬件之间路由命令的真实硬件在环安全联锁。

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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — 具备真实触觉提醒和配对手机语音中继的 WearOS 伴侣应用。
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — 面向板卡安装机架的固件，具备真实的工具 ID 解码和 Smart Idle 预热逻辑。
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — 固件加上一个真实的 Python 视觉配套程序，用于热成像/RGB 检测工具头。
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — 发现、克隆并更新本生态系统中每个仓库的管理型桌面工具，也是本项目自身 Qt Quick 视觉外壳的来源。
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux 桌面工具，构建预装了生态系统最新版本、可直接刷写的 CM5 镜像，具备 Raspberry Pi Imager 风格的首次启动 Wi-Fi/用户/SSH 配置。
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — 维护事件协调器：一个低权限边缘角色收集经过脱敏的库存/健康快照，一个控制平面角色以只读方式展示它并请求 AI 提供商给出诊断建议——绝不应用补丁，也不部署任何东西。
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — 可复现的开发主机（Raspberry Pi 5 / CM5），存储生态系统的源代码，并在一个持久化队列下执行受限的构建/测试任务；这是一个专用的开发角色，明确不是一台运行中的 CM5。

---

## 📚 文档与社区

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - 每一个真实的 `--cli` 子命令，逐参数说明。
- [`CHANGELOG.md`](CHANGELOG.md) - 每个版本真正交付了什么。
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md)。

## 👤 作者

**JuanenRac (Electro Hobby 3D)**
邮箱：`electrohobby3d@gmail.com`
YouTube：[youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 许可证

GPL-3.0 - 见 [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md)。
