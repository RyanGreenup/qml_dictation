import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    width: 200
    height: 120
    visible: false
    title: "Dictation"
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    color: "#1e1e2e"

    // Close on focus loss
    onActiveFocusItemChanged: {
        if (!activeFocusItem && visible) {
            hideTimer.start()
        }
    }

    Timer {
        id: hideTimer
        interval: 100
        onTriggered: {
            if (!root.activeFocusItem) {
                root.hide()
            }
        }
    }

    // Main content with keyboard focus
    Item {
        id: mainContent
        anchors.fill: parent
        focus: true

        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_V) {
                todoPopup.open()
                event.accepted = true
            }
        }

        Keys.onEscapePressed: {
            root.hide()
        }

        // Single button centered
        Button {
            id: todoButton
            anchors.centerIn: parent
            text: "TODO"
            font.pixelSize: 16

            background: Rectangle {
                implicitWidth: 120
                implicitHeight: 48
                color: todoButton.down ? "#45475a" : "#313244"
                radius: 8
                border.color: todoButton.activeFocus ? "#89b4fa" : "#45475a"
                border.width: 1
            }

            contentItem: Text {
                text: todoButton.text
                font: todoButton.font
                color: "#cdd6f4"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                console.log("TODO action triggered")
            }
        }

        // Help text at bottom
        Text {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 8
            text: "v: popup  Esc: close"
            color: "#6c7086"
            font.pixelSize: 11
        }
    }

    // TODO popup dialog
    Popup {
        id: todoPopup
        anchors.centerIn: parent
        width: 160
        height: 80
        modal: true

        background: Rectangle {
            color: "#313244"
            radius: 8
            border.color: "#89b4fa"
            border.width: 1
        }

        contentItem: Item {
            Text {
                anchors.centerIn: parent
                text: "TODO"
                color: "#cdd6f4"
                font.pixelSize: 18
                font.bold: true
            }
        }

        onClosed: {
            mainContent.forceActiveFocus()
        }
    }

    // Center on screen when shown
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 3 - height / 2
    }

    onVisibleChanged: {
        if (visible) {
            mainContent.forceActiveFocus()
            raise()
            requestActivate()
        }
    }
}
