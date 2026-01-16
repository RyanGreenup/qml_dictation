import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    width: 320
    height: 280
    visible: false
    title: "Dictation"
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    // Catppuccin Mocha colors
    readonly property color bgBase: "#1e1e2e"
    readonly property color bgSurface: "#313244"
    readonly property color bgOverlay: "#45475a"
    readonly property color textMain: "#cdd6f4"
    readonly property color textSubtle: "#6c7086"
    readonly property color accentBlue: "#89b4fa"
    readonly property color accentRed: "#f38ba8"
    readonly property color accentGreen: "#a6e3a1"
    readonly property color accentYellow: "#f9e2af"

    color: bgBase

    // State-based button color
    function getButtonColor(isDown) {
        if (dictation.isRecording) return accentRed
        if (dictation.isTranscribing) return accentYellow
        return isDown ? bgOverlay : bgSurface
    }

    function getButtonText() {
        if (dictation.isRecording) return "Stop Recording"
        if (dictation.isTranscribing) return "Transcribing..."
        if (dictation.state === 3) return "Record Again"  // COMPLETED
        return "Start Recording"
    }

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
    ColumnLayout {
        id: mainContent
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8
        focus: true

        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_V) {
                dictation.toggle()
                event.accepted = true
            }
        }

        Keys.onEscapePressed: {
            root.hide()
        }

        // Main record button
        Button {
            id: recordButton
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 160
            Layout.preferredHeight: 48

            background: Rectangle {
                id: buttonBg
                color: getButtonColor(recordButton.down)
                radius: 8
                border.color: recordButton.activeFocus ? accentBlue : bgOverlay
                border.width: 1

                // Pulsing animation when recording
                SequentialAnimation on opacity {
                    running: dictation.isRecording
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.7; duration: 500 }
                    NumberAnimation { to: 1.0; duration: 500 }
                }
            }

            contentItem: Text {
                text: getButtonText()
                font.pixelSize: 14
                font.bold: dictation.isRecording
                color: dictation.isRecording ? bgBase : textMain
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: dictation.toggle()
            enabled: !dictation.isTranscribing
        }

        // Status / Progress text
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: {
                if (dictation.errorMessage) return dictation.errorMessage
                if (dictation.progressMessage) return dictation.progressMessage
                if (dictation.isRecording) return "Recording..."
                return ""
            }
            color: dictation.errorMessage ? accentRed : textSubtle
            font.pixelSize: 12
            visible: text.length > 0
            wrapMode: Text.WordWrap
            Layout.maximumWidth: parent.width - 24
            horizontalAlignment: Text.AlignHCenter
        }

        // Transcribed text area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: bgSurface
            radius: 6
            border.color: bgOverlay
            border.width: 1
            visible: dictation.transcribedText.length > 0 || dictation.state === 3

            ScrollView {
                anchors.fill: parent
                anchors.margins: 8

                TextArea {
                    id: transcribedTextArea
                    text: dictation.transcribedText
                    color: textMain
                    font.pixelSize: 13
                    wrapMode: TextArea.Wrap
                    readOnly: true
                    background: null
                    selectByMouse: true
                }
            }
        }

        // Spacer when no text
        Item {
            Layout.fillHeight: true
            visible: dictation.transcribedText.length === 0 && dictation.state !== 3
        }

        // Copy button (only shown when text exists)
        Button {
            id: copyButton
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 100
            Layout.preferredHeight: 36
            visible: dictation.transcribedText.length > 0

            background: Rectangle {
                color: copyButton.down ? bgOverlay : bgSurface
                radius: 6
                border.color: accentGreen
                border.width: 1
            }

            contentItem: Text {
                text: "Copy"
                font.pixelSize: 13
                color: accentGreen
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: dictation.copyToClipboard()
        }

        // Help text at bottom
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "v: toggle  Esc: close"
            color: textSubtle
            font.pixelSize: 11
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
