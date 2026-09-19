// =============================================================================
// HYDRA-UMC-EDITOR-STL - Qt Quick visual desktop shell: Main.qml
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0 - see LICENSE
// =============================================================================
// Same real visual language HYDRA-UMC-UPDATER's own Main.qml established
// for this ecosystem's PC tools (dark canvas, cyan/blue/amber/red accents,
// Bahnschrift type, GameButton/GameCombo/SectionPanel components) - reused
// here verbatim, not restyled, per the project owner's own request that
// this app "use the same UI base as UPDATER". Every list/status value
// below comes straight from qt_gui.py's real EditorBridge - no row here
// is invented in QML.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.VectorImage
import QtQuick3D
import HydraUmcEditorStl

ApplicationWindow {
    id: window
    width: 1500
    height: 900
    minimumWidth: 1100
    minimumHeight: 680
    visible: true
    visibility: Window.Maximized
    title: backend.text("window_title")
    color: "#07111e"

    property string languageTick: backend.language
    property color canvasColor: "#07111e"
    property color panel: "#101d30"
    property color panelAlt: "#14253b"
    property color border: "#294965"
    property color textPrimary: "#edf7ff"
    property color textMuted: "#91a8bd"
    property color cyan: "#38d4e6"
    property color blue: "#397dff"
    property color green: "#43db9b"
    property color amber: "#f3ba55"
    property color red: "#ee6b80"

    function ui(key) {
        var ignored = languageTick
        return backend.text(key)
    }

    component LabelText: Text {
        color: window.textPrimary
        font.family: "Bahnschrift"
        font.pixelSize: 12
        renderType: Text.QtRendering
    }

    component SectionPanel: Rectangle {
        color: window.panel
        radius: 16
        border.width: 1
        border.color: window.border
    }

    component GameButton: Button {
        id: gameButton
        property color accent: window.blue
        implicitHeight: 40
        hoverEnabled: true
        font.family: "Bahnschrift"
        font.pixelSize: 12
        font.bold: true
        contentItem: Text {
            text: gameButton.text
            color: gameButton.enabled ? "#f5fbff" : "#6d8294"
            font: gameButton.font
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle {
            radius: 10
            border.width: 1
            border.color: gameButton.enabled ? Qt.lighter(gameButton.accent, gameButton.hovered ? 1.28 : 1.08) : "#25384b"
            color: !gameButton.enabled ? "#122031" : (gameButton.down ? Qt.darker(gameButton.accent, 1.38) : (gameButton.hovered ? Qt.lighter(gameButton.accent, 1.14) : gameButton.accent))
            Behavior on color { ColorAnimation { duration: 130 } }
            Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; height: 1; radius: 1; color: gameButton.enabled ? "#9eeeff" : "#34495c"; opacity: 0.55 }
        }
    }

    component GameCombo: ComboBox {
        id: gameCombo
        implicitHeight: 40
        font.family: "Bahnschrift"
        font.pixelSize: 12
        contentItem: Text {
            leftPadding: 13
            rightPadding: 34
            text: gameCombo.displayText
            color: "#edf7ff"
            font: gameCombo.font
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        indicator: Text {
            x: gameCombo.width - width - 13
            y: (gameCombo.height - height) / 2 - 1
            text: "⌄"
            color: window.cyan
            font.family: "Bahnschrift"
            font.pixelSize: 20
        }
        background: Rectangle {
            radius: 10
            color: gameCombo.pressed ? "#1a3954" : (gameCombo.hovered ? "#19334d" : "#12263a")
            border.width: 1
            border.color: gameCombo.hovered ? "#3dcce0" : "#315773"
            Behavior on color { ColorAnimation { duration: 120 } }
        }
        delegate: ItemDelegate {
            width: gameCombo.width
            height: 39
            contentItem: Text {
                text: modelData.label || modelData
                color: "#edf7ff"
                font.family: "Bahnschrift"
                font.pixelSize: 12
                verticalAlignment: Text.AlignVCenter
                leftPadding: 13
            }
            background: Rectangle { color: highlighted ? "#23516e" : "#10243a" }
        }
        popup: Popup {
            y: gameCombo.height + 5
            width: gameCombo.width
            implicitHeight: contentItem.implicitHeight
            padding: 1
            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: gameCombo.popup.visible ? gameCombo.delegateModel : null
                currentIndex: gameCombo.highlightedIndex
            }
            background: Rectangle { radius: 10; color: "#10243a"; border.width: 1; border.color: "#3dcce0" }
        }
    }

    component GameField: TextField {
        id: gameField
        implicitHeight: 38
        font.family: "Bahnschrift"
        font.pixelSize: 12
        color: window.textPrimary
        selectByMouse: true
        background: Rectangle {
            radius: 8
            color: "#0c1b2b"
            border.width: 1
            border.color: gameField.activeFocus ? window.cyan : window.border
        }
    }

    component ListLabel: LabelText {
        color: window.textMuted
        font.pixelSize: 10
        font.bold: true
        font.letterSpacing: 1
        text: text.toUpperCase()
    }

    component AboutInfoRow: Rectangle {
        property string label: ""
        property string value: ""
        property color valueColor: window.textPrimary
        Layout.fillWidth: true
        implicitHeight: 34
        radius: 8
        color: "#07111e"
        border.width: 1
        border.color: window.border
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            LabelText { text: label.toUpperCase(); color: window.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
            Item { Layout.fillWidth: true }
            LabelText { text: value; color: valueColor; font.pixelSize: 11 }
        }
    }

    FolderDialog {
        id: rootDialog
        title: ui("browse_button")
        onAccepted: backend.setEcosystemRoot(selectedFolder.toString())
    }

    FileDialog {
        id: replaceDialog
        title: ui("btn_choose_replacement")
        nameFilters: ["STL files (*.stl *.STL)"]
        onAccepted: backend.replaceSelectedPart(selectedFile.toString())
    }

    FileDialog {
        id: addDialog
        title: ui("btn_choose_new_part")
        nameFilters: ["STL files (*.stl *.STL)"]
        onAccepted: {
            addFileField.text = selectedFile.toString()
        }
    }

    Dialog {
        id: aboutDialog
        modal: true
        anchors.centerIn: parent
        width: 440
        padding: 24
        background: Rectangle { color: window.panel; radius: 16; border.color: window.border; border.width: 1 }
        contentItem: ColumnLayout {
            spacing: 8

            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Rectangle {
                    Layout.preferredWidth: 88; Layout.preferredHeight: 88; radius: 20
                    color: "#0e3045"; border.width: 1; border.color: "#2d7695"
                    VectorImage {
                        anchors.fill: parent; anchors.margins: 10
                        source: "../../../images/HYDRA_UMC_ICON.svg"
                        preferredRendererType: VectorImage.CurveRenderer
                        animations.loops: Animation.Infinite
                        animations.paused: false
                    }
                }
                Item { Layout.fillWidth: true }
            }

            LabelText {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: "HYDRA<font color=\"" + window.green + "\">-UM</font><font color=\"" + window.red + "\">C</font> <font color=\"" + window.cyan + "\">EDITOR STL</font>"
                textFormat: Text.RichText
                font.pixelSize: 20
                font.bold: true
                font.letterSpacing: 1
            }
            LabelText {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: ui("about_tagline")
                color: window.cyan
                font.pixelSize: 12
                font.bold: true
            }
            LabelText {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: ui("about_description")
                color: window.textMuted
                font.pixelSize: 11
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.topMargin: 6
                spacing: 4
                AboutInfoRow { label: ui("about_version_label"); value: backend.appVersion }
                AboutInfoRow { label: ui("about_author_label"); value: "JuanenRac (Electro Hobby 3D)" }
                AboutInfoRow {
                    label: ui("about_email_label")
                    valueColor: window.cyan
                    value: "electrohobby3d@gmail.com"
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: Qt.openUrlExternally("mailto:electrohobby3d@gmail.com") }
                }
                AboutInfoRow { label: ui("about_license_label"); value: ui("about_license") }
            }

            RowLayout { Layout.fillWidth: true; Layout.topMargin: 8
                GameButton { text: ui("open_github_button"); Layout.preferredWidth: 230; accent: "#264966"; onClicked: Qt.openUrlExternally("https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL") }
                Item { Layout.fillWidth: true }
                GameButton { text: ui("about_close_button"); Layout.preferredWidth: 152; accent: window.cyan; onClicked: aboutDialog.close() }
            }
        }
    }

    Dialog {
        id: removeConfirmDialog
        modal: true
        anchors.centerIn: parent
        width: 420
        padding: 22
        background: Rectangle { color: window.panel; radius: 16; border.color: window.border; border.width: 1 }
        contentItem: ColumnLayout {
            spacing: 14
            LabelText { text: ui("msg_remove_confirm").replace("{name}", backend.selectedPart); wrapMode: Text.WordWrap; Layout.fillWidth: true }
            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                GameButton { text: "Cancel"; accent: "#264966"; onClicked: removeConfirmDialog.close() }
                GameButton {
                    text: ui("btn_remove_part")
                    accent: window.red
                    onClicked: { backend.removeSelectedPart(); removeConfirmDialog.close() }
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 28
        anchors.rightMargin: 28
        anchors.topMargin: 22
        anchors.bottomMargin: 18
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 78
            spacing: 16
            Rectangle {
                width: 54; height: 54; radius: 16
                color: "#0e3045"; border.width: 1; border.color: "#2d7695"
                VectorImage {
                    anchors.fill: parent
                    anchors.margins: 5
                    source: "../../../images/HYDRA_UMC_ICON.svg"
                    preferredRendererType: VectorImage.CurveRenderer
                    animations.loops: Animation.Infinite
                    animations.paused: false
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 1
                LabelText { text: "HYDRA-UMC"; color: window.cyan; font.pixelSize: 13; font.bold: true; font.letterSpacing: 1.2 }
                LabelText { text: "EDITOR STL"; font.pixelSize: 27; font.bold: true; font.letterSpacing: 1.1 }
                LabelText { text: backend.ecosystemRoot ? ui("ecosystem_root_label").replace("{path}", backend.ecosystemRoot) : ui("ecosystem_root_unset"); color: window.textMuted; font.pixelSize: 13 }
            }
            GameButton { text: ui("browse_button"); Layout.preferredWidth: 150; accent: window.cyan; onClicked: rootDialog.open() }
            LabelText { text: ui("lang_label"); color: window.textMuted; font.pixelSize: 12 }
            GameCombo {
                id: languageCombo
                Layout.preferredWidth: 145
                model: backend.availableLanguages
                textRole: "label"
                valueRole: "code"
                Component.onCompleted: {
                    for (var i = 0; i < model.length; ++i) if (model[i].code === backend.language) currentIndex = i
                }
                onActivated: backend.setLanguage(model[currentIndex].code)
            }
            GameButton { text: ui("menu_about"); Layout.preferredWidth: 110; accent: "#264966"; onClicked: aboutDialog.open() }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            // --- left column: library / category / model / parts -------
            SectionPanel {
                Layout.preferredWidth: 420
                Layout.fillHeight: true
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    ListLabel { text: ui("library_label") }
                    GameCombo {
                        Layout.fillWidth: true
                        model: backend.libraries
                        Component.onCompleted: currentIndex = model.indexOf(backend.selectedLibrary)
                        onActivated: backend.selectLibrary(model[currentIndex])
                    }

                    ListLabel { text: ui("category_label") }
                    GameCombo {
                        id: categoryCombo
                        Layout.fillWidth: true
                        model: backend.categories
                        onActivated: backend.selectCategory(model[currentIndex])
                        Connections {
                            target: backend
                            function onCategoriesChanged() { categoryCombo.currentIndex = -1 }
                        }
                    }

                    ListLabel { text: ui("model_label") }
                    GameCombo {
                        id: modelCombo
                        Layout.fillWidth: true
                        model: backend.models
                        onActivated: backend.selectModel(model[currentIndex])
                        Connections {
                            target: backend
                            function onModelsChanged() { modelCombo.currentIndex = -1 }
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: window.border }

                    RowLayout {
                        Layout.fillWidth: true
                        ListLabel { text: ui("col_part"); Layout.fillWidth: true }
                        ListLabel { text: ui("col_size"); Layout.preferredWidth: 80 }
                        ListLabel { text: ui("col_editable"); Layout.preferredWidth: 60 }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: backend.parts
                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 34
                            radius: 6
                            color: modelData.filename === backend.selectedPart ? "#1c3b52" : "transparent"
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 6
                                anchors.rightMargin: 6
                                LabelText { text: modelData.filename; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                LabelText { text: modelData.sizeBytes + " B"; color: window.textMuted; Layout.preferredWidth: 80; font.pixelSize: 10 }
                                LabelText { text: modelData.editable ? "✓" : "—"; color: modelData.editable ? window.green : window.textMuted; Layout.preferredWidth: 60 }
                            }
                            MouseArea { anchors.fill: parent; onClicked: backend.selectPart(modelData.filename) }
                        }
                    }
                }
            }

            // --- center: big 3D viewer + right: slim tool panel ---------
            SectionPanel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    // Real orbit camera state - a mouse-drag orbit around
                    // the currently loaded model's own real combined
                    // bounding-box center (backend.boundsCenter/boundsRadius,
                    // computed from the real parts just loaded, never a
                    // fixed guess that would look broken for a 400mm robot
                    // base and a 5mm screw alike).
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        property real camYaw: 35
                        property real camPitch: -22
                        property real camZoom: 1.0
                        property real dragStartX: 0
                        property real dragStartY: 0
                        property bool dragMoved: false

                        Rectangle {
                            anchors.fill: parent
                            radius: 12
                            color: "#050b13"
                            border.width: 1
                            border.color: window.border
                            clip: true

                            View3D {
                                id: view3d
                                anchors.fill: parent
                                camera: orbitCamera
                                environment: SceneEnvironment {
                                    clearColor: "#050b13"
                                    backgroundMode: SceneEnvironment.Color
                                    antialiasingMode: SceneEnvironment.MSAA
                                    antialiasingQuality: SceneEnvironment.High
                                }

                                Node {
                                    id: cameraPivot
                                    position: Qt.vector3d(backend.boundsCenter[0], backend.boundsCenter[1], backend.boundsCenter[2])
                                    eulerRotation: Qt.vector3d(parent.parent.camPitch, parent.parent.camYaw, 0)
                                    PerspectiveCamera {
                                        id: orbitCamera
                                        position: Qt.vector3d(0, 0, backend.boundsRadius * 2.4 * parent.parent.parent.camZoom)
                                        clipNear: Math.max(1, backend.boundsRadius * 0.01)
                                        clipFar: backend.boundsRadius * 50
                                    }
                                }

                                DirectionalLight { eulerRotation: Qt.vector3d(-45, -35, 0); brightness: 1.1 }
                                DirectionalLight { eulerRotation: Qt.vector3d(35, 135, 0); brightness: 0.35 }

                                Repeater3D {
                                    model: backend.parts
                                    delegate: Model {
                                        visible: modelData.editable
                                        objectName: modelData.filename
                                        geometry: StlGeometry { source: modelData.editable ? modelData.absolutePath : "" }
                                        materials: PrincipledMaterial {
                                            baseColor: modelData.filename === backend.selectedPart
                                                ? Qt.lighter(modelData.color, 1.7)
                                                : modelData.color
                                            roughness: 0.55
                                            metalness: 0.05
                                        }
                                    }
                                }
                            }

                            LabelText {
                                anchors.centerIn: parent
                                visible: backend.parts.length === 0
                                text: ui("viewer_empty_hint")
                                color: window.textMuted
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Text.AlignHCenter
                                width: parent.width * 0.7
                            }

                            MouseArea {
                                id: orbitArea
                                anchors.fill: parent
                                acceptedButtons: Qt.LeftButton
                                onPressed: (mouse) => {
                                    parent.parent.dragStartX = mouse.x
                                    parent.parent.dragStartY = mouse.y
                                    parent.parent.dragMoved = false
                                }
                                onPositionChanged: (mouse) => {
                                    if (pressed) {
                                        var dx = mouse.x - parent.parent.dragStartX
                                        var dy = mouse.y - parent.parent.dragStartY
                                        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) parent.parent.dragMoved = true
                                        parent.parent.camYaw -= dx * 0.4
                                        parent.parent.camPitch = Math.max(-85, Math.min(85, parent.parent.camPitch - dy * 0.4))
                                        parent.parent.dragStartX = mouse.x
                                        parent.parent.dragStartY = mouse.y
                                    }
                                }
                                onClicked: (mouse) => {
                                    if (parent.parent.dragMoved) return
                                    var result = view3d.pick(mouse.x, mouse.y)
                                    if (result.objectHit) backend.selectPart(result.objectHit.objectName)
                                }
                                onWheel: (wheel) => {
                                    parent.parent.camZoom = Math.max(0.15, Math.min(6, parent.parent.camZoom - wheel.angleDelta.y / 1000))
                                }
                            }
                        }
                    }

                    // --- slim tool panel - the project owner's own
                    // explicit preference over the previous boxed-forms
                    // layout that used to occupy this whole column. ---
                    SectionPanel {
                        Layout.preferredWidth: 230
                        Layout.fillHeight: true
                        color: window.panelAlt
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            ListLabel { text: ui("selected_part_label") }
                            LabelText {
                                text: backend.selectedPart || ui("no_part_selected")
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                                color: backend.selectedPart ? window.textPrimary : window.textMuted
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: window.border }

                            GameButton {
                                text: ui("btn_change_color")
                                accent: window.cyan
                                Layout.fillWidth: true
                                enabled: !!backend.selectedPart
                                onClicked: colorDialog.open()
                            }
                            GameButton {
                                text: ui("btn_choose_replacement")
                                accent: window.amber
                                Layout.fillWidth: true
                                enabled: !!backend.selectedPart
                                onClicked: replaceDialog.open()
                            }
                            GameButton {
                                text: ui("btn_remove_part")
                                accent: window.red
                                Layout.fillWidth: true
                                enabled: !!backend.selectedPart
                                onClicked: removeConfirmDialog.open()
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: window.border }

                            ListLabel { text: ui("panel_transform_title") }
                            ListLabel { text: ui("lbl_translate") }
                            RowLayout {
                                spacing: 4
                                GameField { id: txField; text: "0"; Layout.fillWidth: true }
                                GameField { id: tyField; text: "0"; Layout.fillWidth: true }
                                GameField { id: tzField; text: "0"; Layout.fillWidth: true }
                            }
                            ListLabel { text: ui("lbl_rotate") }
                            RowLayout {
                                spacing: 4
                                GameField { id: rxField; text: "0"; Layout.fillWidth: true }
                                GameField { id: ryField; text: "0"; Layout.fillWidth: true }
                                GameField { id: rzField; text: "0"; Layout.fillWidth: true }
                            }
                            ListLabel { text: ui("lbl_scale") }
                            GameField { id: scaleField; text: "1"; Layout.fillWidth: true }
                            GameButton {
                                text: ui("btn_apply_transform")
                                accent: window.blue
                                Layout.fillWidth: true
                                enabled: !!backend.selectedPart
                                onClicked: backend.applyTransform(
                                    parseFloat(txField.text) || 0, parseFloat(tyField.text) || 0, parseFloat(tzField.text) || 0,
                                    parseFloat(rxField.text) || 0, parseFloat(ryField.text) || 0, parseFloat(rzField.text) || 0,
                                    parseFloat(scaleField.text) || 1
                                )
                            }

                            Rectangle { Layout.fillWidth: true; height: 1; color: window.border }

                            ListLabel { text: ui("panel_add_title") }
                            RowLayout {
                                Layout.fillWidth: true
                                GameField { id: addFileField; Layout.fillWidth: true; readOnly: true }
                                GameButton { text: "..."; Layout.preferredWidth: 36; accent: "#264966"; onClicked: addDialog.open() }
                            }
                            GameField { id: addDestField; Layout.fillWidth: true; placeholderText: ui("dest_filename_label") }
                            GameButton {
                                text: ui("btn_add_part")
                                accent: window.green
                                Layout.fillWidth: true
                                onClicked: backend.addPart(addFileField.text, addDestField.text)
                            }

                            Item { Layout.fillHeight: true }

                            LabelText { text: ui("trash_note"); color: window.textMuted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 36
                                radius: 8
                                color: "#10283a"
                                border.width: 1
                                border.color: "#21516a"
                                LabelText {
                                    anchors.fill: parent
                                    anchors.margins: 6
                                    text: backend.statusText
                                    color: window.textMuted
                                    font.pixelSize: 10
                                    wrapMode: Text.WordWrap
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    ColorDialog {
        id: colorDialog
        title: ui("btn_change_color")
        onAccepted: backend.setSelectedPartColor(selectedColor.toString())
    }
}
