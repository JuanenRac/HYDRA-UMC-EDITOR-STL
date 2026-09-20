<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-EDITOR-STL バナー" width="100%">
</p>

# 🧩 HYDRA-UMC-EDITOR-STL

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | 🇯🇵 <b>日本語</b></p>

### 📦 HYDRA-UMC エコシステム自身の実在する STL モデルライブラリを閲覧・編集する

<p align="center">
  <img src="https://img.shields.io/badge/ライセンス-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/言語-Python%203.10%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/コア-numpy--stl-brightgreen.svg" alt="numpy-stl コア">
  <img src="https://img.shields.io/badge/デスクトップ-PySide6%20%7C%20Qt%20Quick-367BF5.svg" alt="PySide6 Qt Quick デスクトップGUI">
</p>

> **v0.0.4。** 以下で説明する実際のCLI/GUIコアは本当に実装され、テスト
> されています。クリックで選択できる本物の Qt Quick 3D ビューア、
> パーツごとの色、変換、置換、削除、追加、そして編集/追加したモデルを
> HYDRA-UMC-SERVER 自身の実在する `POST /api/models/submit` カタログへ
> 実際に送信する機能（HYDRA-UMC-EDITOR-URDF が URDF モデルに対して
> 使っているのと同じ実在の統合ポイント）を含みます。パーツ自身が
> 保存した色は、今では HYDRA-UMC-STUDIO と HYDRA-UMC-SUITE 自身の実際の
> ライブ 3D ビューアにも届きます（それぞれのリポジトリ自身の実在する
> 変更 - 各自の CHANGELOG を参照）。したがって `part_colors.json` は
> もはや EDITOR-STL 限定のプレビューではありません。

**誠実さの確認 - 今日実際に動くもの：** `model_catalog.py`
（両方のモデルライブラリに対する実在の読み取り専用ディスカバリ）、
`stl_ops.py`（`numpy-stl` による実在の STL 変更 - 変換/置換/削除/追加、
さらに 3D ビューアのカメラ取景用の `model_bounds()`）、`part_colors.py`
（実在のパーツごとの色サイドカーファイル）、`stl_geometry.py`
（実在の Qt Quick 3D ジオメトリ読み込み）、`catalog_push.py`
（実在の組み立て用 URDF 生成に加え、`POST /api/models/submit` 向けの
実在の HTTP クライアント）はすべて、実際に生成した
実在の STL ファイルと、必要に応じて実在のセッションスコープの
`QGuiApplication` に対してテストされており（`pytest tests/`、48 件の
ケースが合格）、本エコシステム自身の実在する
`HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` のチェックアウトに対してエンド
ツーエンドでスモークテスト済みです（`--cli categories`/`models`/
`parts` は実在するツリーに対して実行、`transform`/`remove` は使い捨ての
コピーに対してのみ実行し、実際のチェックアウト自体には触れていません）。
`qt_gui.py` 自身の `EditorBridge` も直接テストされています（色の
slot、色変更後も選択状態が保持されること）。`qml/Main.qml` は QML
エラーなしでロード・描画されます（`QT_QPA_PLATFORM=offscreen` で
ヘッドレス検証済み、実際のモデルのパーツを 3D ビューアに読み込んだ
状態も含む）が、QML シーングラフ自体には自動テストがありません -
実際の Qt イベントループを駆動することはここでは試みていません。
これは HYDRA-UMC-UPDATER 自身の README がすでに自らの Qt Quick 層に
ついて引いているのと同じ誠実さの境界線です。

---

## 1. 🛠️ 技術概要

HYDRA-UMC-EDITOR-STL は、HYDRA-UMC-STUDIO と HYDRA-UMC-SUITE が配布する
すべてのロボット/マシンモデルを構成する実在の STL パーツを編集するための、
小さなデスクトップツールです - デフォルトはウィンドウ GUI、`--cli` で
完全な CLI も使えます。両方のアプリは 2026-09 に自分たち自身のモデル
フォルダを同じ実在のカテゴリ構造（`robots-5-dof`/`robots-6-dof`/
`robots-7-dof`、`machine-pnp`/`machine-cnc`/`machine-laser`、
`heatedbeds`/`racks`/`vacuum-tables`、各モデルは自身の
`ATTRIBUTION.txt` の隣に自身の `metadata.json` を持つ）へと再編成しま
した - 本ツールはまさにその実在の構造を読み取るのであって、別のコピー
や独自のデータベースを持つわけではありません。

本物の Qt Quick 3D ビューアが、選択中のモデルの編集可能な各パーツを
描画します（`stl_geometry.py` — 各パーツ自身の STL ファイルから
三角形を直接読み込む、本物の `QQuick3DGeometry`）——ドラッグで軌道
回転、ホイールでズーム、パーツをクリックして選択（推測ではなく本物の
`View3D.pick()`）。カメラはモデル自身の実在する結合バウンディング
ボックスに自動的にフレーミングされる（`stl_ops.py` の
`model_bounds()`）ので、400mm のロボットベースと 5mm のネジのどちら
も正しくフレーミングされます。

6つの実在する操作、それぞれディスク上の実際のチェックアウトに対する
実在のファイル I/O に裏打ちされています：

- **変換** - パーツの実在する頂点データを（`numpy-stl` — すでに
  HYDRA-UMC-SUITE 自身の `render/mesh.py` が依存しているのと同じ
  ライブラリ経由で）平行移動/回転/拡大縮小し、同じ場所に保存し直す。
- **色の変更** - パーツごとの実在する色注釈（`part_colors.json`、本
  ツール自身が持つサイドカーファイル）が3Dビューに表示されます——
  バイナリ STL はそれ自身の信頼できる色を持たないため、このサイドカー
  ファイルこそが実在する真実の情報源です。HYDRA-UMC-STUDIO 自身の
  `hooks/usePartColors.ts` と HYDRA-UMC-SUITE 自身の
  `render/part_colors.py` はどちらもこの同じファイルを読み返すため、
  ここで保存した色は本ツール自身のプレビューだけでなく、それらの実際の
  3Dビューアにも届きます。
- **置換** - あるパーツを別の実在する STL ファイルで上書きする。
- **削除** - あるパーツをモデルから取り除く。
- **追加** - 新しい実在の STL ファイルをモデルに持ち込む。
- **サーバーに送信** - 選択中のモデルの現在の編集可能パーツを、稼働中の
  HYDRA-UMC-SERVER 自身の実在するモデル提出カタログへ送信する
  （`catalog_push.py`、`POST /api/models/submit` — 管理者ログインが
  必要、HYDRA-UMC-EDITOR-URDF 自身の同等機能と同様）。このエンドポイント
  自身の契約は URDF 向けの形をしているため、パーツをその契約が受け入れる
  最小の実在する URDF に包みます：ルートリンク1つと、パーツごとに
  関節を持たない（`fixed`）子リンク1つ — 各パーツの実際の位置はすでに
  それ自身の STL 頂点に焼き込まれているため、ここで架空のポーズを
  作り出すことはありません。

**何も永久には削除されません。** 削除や置換は、まず実在する元のファイル
をそのモデル自身の `.trash/` サブフォルダへ移動します - これは本
エコシステムの内部作業慣習がすでに従っている「破壊せず、脇に移す」
という規律を、単なる内部的な習慣としてではなく、実在の製品機能として
ここに適用したものです。

## 2. 🧱 アーキテクチャと設計上の決定

- **2つの実在するライブラリ、1つのディスカバリモジュール。**
  `model_catalog.py` 自身の `LIBRARIES` 定数は、本ツールが編集する
  2つの実在するツリー（`HYDRA-UMC-STUDIO/public/models/`、
  `HYDRA-UMC-SUITE/assets/meshes/`）を列挙しています - 後で3つ目の
  ライブラリを追加するということは、そこに1エントリを追加することを
  意味し、2つ目のディスカバリ実装を作ることではありません。
- **`stl_ops.py` だけがファイルを変更する唯一の場所です。**
  `model_catalog.py` は厳密に読み取り専用のままであり、`--cli` と
  Qt Quick ブリッジはどちらも全く同じ `transform_part()`/
  `replace_part()`/`remove_part()`/`add_part()` 関数を呼び出すため、
  GUI が CLI 自体にはできないことを行うことは決してありません。
- **`.stl` で終わるファイル名だけでなく、本物の STL であること。**
  `is_real_stl()` は、候補となる置換/追加ファイルを実際のモデル
  フォルダにコピーする前に、`numpy-stl` で本当に解析します - そして、
  本プロジェクト自身のテストを書く過程で見つかった実在のギャップとして、
  **三角形数が 0** の解析結果も拒否します：`numpy-stl` 自身の ASCII
  フォールバックパスは任意のゴミバイト列に対して例外を送出せず、
  黙って空のメッシュとして解析してしまうため、単純な try/except だけ
  では STL では全くないファイルを通してしまっていたはずです。
- **デフォルトは Qt Quick GUI、ディスプレイのない環境には `--cli`。**
  `main.py` は `--cli` 以外の経路でのみ PySide6 をインポートするため、
  `--cli categories`/`models`/`parts`/`transform`/`replace`/`remove`/
  `add` はディスプレイも Qt ランタイムも一切インストールされていない
  マシン上でも動作します。
- **HYDRA-UMC-UPDATER と全く同じ実在のビジュアル層。** `qml/Main.qml`
  は、プロジェクトオーナー本人の明示的な要望により、その
  プロジェクト自身の `GameButton`/`GameCombo`/`SectionPanel`
  コンポーネントとその暗いシアン/ブルー/アンバー/レッドのテーマを
  そのまま再利用しています - このエコシステムにおける新しい PC
  ツールは、別々にデザインされたものではなく、同じツールのように
  感じられるべきです。
- **固定されたパスではなく、エコシステムのルート。**
  HYDRA-UMC-UPDATER 自身のワークスペースルートと同様に、この
  プロジェクト自身の親ディレクトリがデフォルト値です（`main.py` の
  `default_ecosystem_root()`）。常に上書き可能で（`--cli` の
  `--root`、GUI の「参照」）、GUI の起動をまたいで記憶されます
  （`settings.py`）。

## 📂 ディレクトリ構造

```
HYDRA-UMC-EDITOR-STL/
├── src/hydra_umc_editor_stl/
│   ├── model_catalog.py    # 両方のモデルライブラリに対する実在の読み取り専用ディスカバリ
│   ├── stl_ops.py           # 実在の STL 変更：変換/置換/削除/追加、.trash/ バックアップ
│   ├── catalog_push.py       # 組み立て用 URDF + POST /api/models/submit 向け HTTP クライアント
│   ├── settings.py          # 永続化されたエコシステムのルートと言語設定
│   ├── i18n.py               # 実在の完全な GUI 翻訳（7言語）
│   ├── qt_gui.py             # 実在の model_catalog.py/stl_ops.py コア上の Qt Quick ブリッジ
│   ├── qml/Main.qml          # HYDRA-UMC-UPDATER と共有するテーマ付きデスクトップシェル
│   └── main.py               # ディスパッチ：デフォルトは GUI、--cli は categories/models/parts/transform/replace/remove/add/push 用
├── tests/                    # 実際に生成した実在の STL ファイルに対する実在のテスト
├── docs/
│   └── CLI_REFERENCE.md      # コマンドリファレンス
├── images/                   # メディアとアプリアイコン
├── tools/
│   ├── build_test.py         # バージョンに触れないビルド/コンパイルチェック
│   └── ci_validate.py        # CI が使用するマニフェスト/CHANGELOG/ドキュメント検証
├── build.sh / build.bat      # venv + 編集可能インストール（dev+gui エクストラ）+ コンパイルチェック + テスト
├── run.sh / run.bat          # デフォルトの GUI / CLI エントリポイント
├── run-gui.vbs               # コンソールウィンドウのない Windows 用グラフィカルランチャー
├── bump_version.py           # エコシステム全体の「オドメーター」式バージョン更新（pyproject.toml + __init__.py）
└── bump_manifest_version.py  # hydra-umc.project.json のバージョンをネイティブのものと同期（--sync）
```

## ⚙️ ビルドと実行ガイド

```bash
chmod +x build.sh   # 一度だけ
./build.sh          # .venv を作成、pip install -e ".[dev,gui]"、コンパイルチェックとテスト
./run.sh                                                    # ウィンドウ GUI（デフォルト）
./run.sh --cli categories studio                            # あるライブラリのカテゴリを一覧表示
./run.sh --cli models studio robots-6-dof                   # あるカテゴリのモデルを一覧表示
./run.sh --cli parts studio robots-6-dof ar3                 # あるモデルの実在するパーツファイルを一覧表示
./run.sh --cli transform studio robots-6-dof ar3 base_link.STL --tz 10
./run.sh --cli replace studio robots-6-dof ar3 base_link.STL /path/new.stl
./run.sh --cli remove studio robots-6-dof ar3 base_link.STL
./run.sh --cli add studio robots-6-dof ar3 /path/new.stl
./run.sh --cli push studio robots-6-dof ar3 --host 192.168.1.100 --username admin --password ***
```

Windows では：`build.bat`、続いて `run.bat`（GUI）または
`run.bat --cli ...` / コンソールなしで GUI を起動するには
`run-gui.vbs` をダブルクリックします。

`library` は常に `studio` か `suite` です。`category`/`model` は
`categories`/`models` がちょうど出力した実在のフォルダ名です。
`--root` は任意の `--cli` コマンドについてエコシステムのルートを
上書きします（デフォルト：本ツール自身の親ディレクトリ）。

**トラブルシューティング**

- `categories`/`models`/`parts` が何も出力しない：エコシステムの
  ルートが実際には `HYDRA-UMC-STUDIO`/`HYDRA-UMC-SUITE` を兄弟
  ディレクトリとして含んでいません - `--root` を明示的に渡すか、
  GUI の「参照」を使ってください。
- `transform`/`replace`/`add` が "not a real, parseable STL file" で
  失敗する：ソースファイルが実際に有効な STL ではありません
  （または三角形数が 0 です）- 実際の CAD/メッシュビューアで開いて
  確認してください。
- 削除/置換したパーツが GUI 自身のパーツ一覧から消えなかった：
  ディスク上では実際に `.trash/` へ移動しています - パーツ一覧は
  現在の実在するトップレベルのファイルのみを表示し、`.trash/`
  サブフォルダは意図的にそこから除外されています。

## 🚀 ロードマップ

- パッケージ化されたスタンドアロン GUI 実行ファイル
  （HYDRA-UMC-SUITE 自身の `build_exe.bat`/`.sh` の慣習に従った
  PyInstaller）。
- 手動でのファイル復元ではなく、あるセッション自身の `.trash/`
  履歴に基づく取り消し/やり直し。

## 🔗 関連プロジェクト

このプロジェクトは、同じ著者（JuanenRac / Electro Hobby 3D）による HYDRA-UMC ロボティクスエコシステムの一部です。ある依頼が実際にはこのリポジトリではなく、これらのいずれかに関するものである可能性があるため、知っておく価値があります。

**親プロジェクト**
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — この編集ツールが読み書きする2つの実在するモデルライブラリのうちの1つ（`public/models/`）を所有しています。

**直接関連**
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — この編集ツールが読み書きする2つ目の実在するモデルライブラリ（`assets/meshes/`）を所有しており、STUDIO のものと全く同じカテゴリ構造で維持されています。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 本ツールが編集する生の STL ジオメトリではなく、同じモデルカタログの URDF/運動学側を扱う姉妹デスクトップエディタです。
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — 本エディタが完成した編集内容を送信する実在する `POST /api/models/submit` エンドポイントを所有しています（`catalog_push.py`、GUI の「サーバーに送信...」または `--cli push`）。

**エコシステムの他の一部**

*コアハードウェアとプラットフォーム*
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — ロボットアームのマザーボード本体：CM5 ホスト + デュアルコア STM32H745、CAN-OTA/SPI-OTA 経由で最大8本のツールアームをオーケストレーションします。
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — CM5 向けの再現可能な Raspberry Pi OS 製品層：読み取り専用エージェント、検証済みの設定/プロファイル、WiFi ファーストコンタクトプロビジョニング。
- **[HYDRA-UMC-SDK](https://github.com/JuanenRac/HYDRA-UMC-SDK)** — すべての bridge が自身のコマンドを検証する際に使う、共有の JSON-Schema 契約と安全ゲート境界。
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — 外部マシンコネクタ向けの宣言的なアダプタマニフェストレジストリとそのバリデータ。工業ゲートウェイ系プロジェクトを置き換えることなく、SDK 自身の契約という考え方を外部マシンへ拡張します。

*コアバックエンドとクライアント*
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — 生体認証ログインとペアリングされた Wear OS コンパニオンを備えたネイティブ Android 制御アプリ。
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — リアルタイム WebSocket 同期を備えた iOS/iPadOS 制御アプリ（Flutter）。
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — CM5 本体に組み込まれた 7 インチ DSI タッチスクリーン向けのネイティブタッチ UI。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — GitHub/ローカルソースの読み込みとライブ 3D プレビュー編集を備えたグラフィカルなデスクトップ URDF 作成/編集ツール。
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — 実在する VDA 5050 MQTT パブリッシャー経由の、AGV/AMR フリート向け協調境界。
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — 実在する GRBL ステータス/制御バイトへのアクセスを備えた高レベル CNC セルコーディネータ。
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — 実在する Boston Dynamics Spot コマンド送信機を備えた、脚式/ヒューマノイドドロイド向け協調境界。
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — 3つの実在するキー/筐体/インターロック GPIO 安全装置を読み取るレーザーセル安全コーディネータ。
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — OpenPnP のピックアンドプレース向けの安全な高レベル基板フローコーディネータ。
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — 実在するゲート付きジョブコマンドを備えた、Moonraker/Klipper 3D プリンタ向けの安全な協調境界。
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — 実在する、遅延インポートされる rclpy ROS 2 トランスポートを備えた安全コーディネータ。
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — 実在する MAVLink コマンド送信機を備えた、カメラ搭載 UAV 向け協調境界。

*URTC ツールプラットフォーム*
- **[URTC](https://github.com/JuanenRac/URTC)** — 物理的な Universal Robot Tool Controller PCB 向けファームウェア、CAN バス経由で25以上のツールプロファイルに対応。
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — URTC ボード向けデスクトップ GUI 書き込みツール、CAN-OTA に加えてフルチップ SWD/JTAG に対応。
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — URTC ボード向けデスクトップのライブ CAN バス診断ツール、ツールプロファイルごとに1パネル。
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — ローカルインストール不要な、Web Serial API 経由のブラウザベースの URTC-TESTER 代替。

*ビジョン AI ノード（Hailo-8）*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — 段階ごとの実在するハードウェア準備状況チェックを備えた、Hailo-8 ビジョンパイプラインの統合ハブ。
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — Hailo のアーキテクチャ/チェックサムによる安全なロード検証を備えた、実在するコンパイル済みモデルレジストリ。
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — 実在する HailoRT 統合境界を備えた、実在する GStreamer パイプライン + MediaMTX 設定ジェネレータ。
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — 上流のゾーン状態に対して安全ゲートされた、実在する Position-Based Visual Servoing 補正則。
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — キャリブレーションの新しさを強制する、実在するゾーン侵害チェックと E-STOP 要求。

*認知 AI ノード（Hailo-10）*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — Hailo-10 認知パイプライン（LLM/VLA/音声オーケストレーション）の統合ハブ。
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — Vision-Language-Action モデル向けの、実在するアクショントークンのエンコード/デコードと軌道生成。
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — 制限付きで確認ゲートされた Watch リレーを備えた、実在する音声フロントエンド（VAD + インテントパーサー）。
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — MCU エラーコードに対する、実在するルールベースのタスク分解とセマンティックなエラー復旧。
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — 本エコシステム自身の Markdown ドキュメントに対する、標準ライブラリのみで実装された実在の TF-IDF ドキュメント検索。
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — エコシステム自身のための、ポリシーでゲートされたローカル AI メンテナンス技師 - 観察し、診断し、修正案を提案します。最も高い2つのリスクレベルは意図的にまだ実装されていません。

*オーケストレーションとスウォーム*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — 実在する gRPC/Protobuf ヘルスレポート契約とミッションステートマシンを備えた統合ハブ。
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — 実在する HTTP API 上の、重複排除機能を備えた実在する優先度ベースのジョブキュー。
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — リトライ/バックオフと ID の不一致検出を備えた、実在する gRPC ベースのフリートヘルスウォッチドッグ。
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — 実在する障害物/作業空間の衝突検証を備えた、実在する RRT ベースの 3D パスプランナー。
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — マルチセル収束についてプロパティテストされた、実在する CRDT LWW-Element-Map 状態同期。

*デジタルツインとシミュレーション*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — HYDRA-UMC-EDITOR-URDF が生成する URDF モデルを消費する、実在する物理シミュレーションデジタルツイン。
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — 同じ URDF モデルを消費して自身の物理シミュレーションを駆動します。
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — それら同じモデルからトレーニングデータを生成します。
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — シミュレーションと実際のハードウェアの間でコマンドをルーティングする、実在するハードウェアインザループ安全インターロック。

*データと分析*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — 実在する取り込み/クエリ HTTP API を備えた、sqlite3 を裏付けとする実在する時系列ストア。
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — ドリフト監視を備えた、実在する FFT + 統計ベースラインの異常検知器。
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — 再現可能な CSV エクスポートを備えた、DATALAKE の履歴に対する実在する OEE/可用性計算。
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — シーケンスの重複排除を備えた、DATALAKE への実在する CAN/WebSocket 取り込みパイプライン。

*インダストリアルゲートウェイ*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — 実在するコマンドのアローリスト/バックプレッシャー層を備えた、産業用プロトコルへ中継する統合ハブ。
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — 実在するバイナリプロトコルのクライアントセッションで検証された、実在する OPC-UA アドレス空間。
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — クライアントごとの認証とトピック ACL をオプションで備えた実在する MQTT ブローカー。
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — 劣化モード出力を備えた、実在する MTConnect の `/probe` および `/current` XML エンドポイント。

*補完ツールとエコシステム運用*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — 誠実な統計的フォールバックを備えた、DATALAKE/ANOMALY-DETECTOR 上のスマートサマリーと異常ハイライトのパネル。
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — 実在する安定した終了コード契約を備えた、HYDRA-UMC-SERVER 自身の API の本物のライブクライアントであるフリート CLI。
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — 実在するハプティックアラートとペアリングされたスマートフォンへの音声リレーを備えた WearOS コンパニオンアプリ。
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — 実在するツール ID デコードと Smart Idle 予熱ロジックを備えた、基板搭載ラック向けファームウェア。
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — サーマル/RGB 検査ツールヘッド向けの、ファームウェアと実在する Python ビジョンコンパニオン。
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — 本エコシステムのすべてのリポジトリを発見・クローン・更新する管理用デスクトップツールであり、本プロジェクト自身の Qt Quick ビジュアルシェルの出所です。
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — エコシステムの最新バージョンをプリロードした、フラッシュ可能な CM5 イメージを構築する Windows/Linux デスクトップツール。Raspberry Pi Imager 風の初回起動時 Wi-Fi/ユーザー/SSH 設定を備えています。
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — メンテナンスインシデントのコーディネータ：低権限のエッジロールがサニタイズされたインベントリ/ヘルスのスナップショットを収集し、コントロールプレーンのロールがそれを読み取り専用で表示し、AI プロバイダに診断を提案するよう依頼します - パッチを適用したり何かをデプロイしたりすることは決してありません。
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — エコシステムのソースを保存し、永続的なキューの下で範囲の限定されたビルド/テストタスクを実行する、再現可能な開発ホスト（Raspberry Pi 5 / CM5）。専用の開発ロールであり、明示的に稼働中の CM5 ではありません。

---

## 📚 ドキュメントとコミュニティ

- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - 実在するすべての `--cli` サブコマンドを、引数ごとに解説。
- [`CHANGELOG.md`](CHANGELOG.md) - バージョンごとに実際に何が出荷されたか。
- [`CONTRIBUTING.md`](CONTRIBUTING.md) / [`SECURITY.md`](SECURITY.md) / [`SUPPORT.md`](SUPPORT.md)。

## 👤 作者

**JuanenRac (Electro Hobby 3D)**
メール：`electrohobby3d@gmail.com`
YouTube：[youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 ライセンス

GPL-3.0 - [`LICENSE`](LICENSE) / [`LICENSE.md`](LICENSE.md) を参照してください。
