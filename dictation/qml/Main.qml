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
            } else if (event.key === Qt.Key_Y) {
                dictation.copyToClipboard()
                event.accepted = true
            } else if (event.key === Qt.Key_H) {
                dictation.copyAsHtml()
                event.accepted = true
            } else if (event.key === Qt.Key_F) {
                dictation.formatWithGpt()
                event.accepted = true
            } else if (event.key === Qt.Key_U) {
                dictation.undoFormat()
                event.accepted = true
            } else if (event.key === Qt.Key_O) {
                dictation.copyOriginal()
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

        // Status / Progress text (selectable for error messages)
        TextArea {
            id: statusText
            Layout.alignment: Qt.AlignHCenter
            Layout.maximumWidth: parent.width - 24
            Layout.preferredHeight: contentHeight
            text: {
                if (dictation.errorMessage) return dictation.errorMessage
                if (dictation.progressMessage) return dictation.progressMessage
                if (dictation.isRecording) return "Recording..."
                return ""
            }
            color: dictation.errorMessage ? accentRed : textSubtle
            font.pixelSize: 12
            visible: text.length > 0
            wrapMode: TextArea.Wrap
            readOnly: true
            selectByMouse: true
            horizontalAlignment: Text.AlignHCenter
            background: null
            padding: 0
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

        // Copy buttons row (only shown when text exists)
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 8
            visible: dictation.transcribedText.length > 0

            Button {
                id: copyButton
                Layout.preferredWidth: 60
                Layout.preferredHeight: 32

                background: Rectangle {
                    color: copyButton.down ? bgOverlay : bgSurface
                    radius: 6
                    border.color: accentGreen
                    border.width: 1
                }

                contentItem: Text {
                    text: "Copy"
                    font.pixelSize: 12
                    color: accentGreen
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: dictation.copyToClipboard()
            }

            Button {
                id: copyHtmlButton
                Layout.preferredWidth: 60
                Layout.preferredHeight: 32

                background: Rectangle {
                    color: copyHtmlButton.down ? bgOverlay : bgSurface
                    radius: 6
                    border.color: accentBlue
                    border.width: 1
                }

                contentItem: Text {
                    text: "HTML"
                    font.pixelSize: 12
                    color: accentBlue
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: dictation.copyAsHtml()
            }

            Button {
                id: formatButton
                Layout.preferredWidth: 70
                Layout.preferredHeight: 32

                background: Rectangle {
                    color: formatButton.down ? bgOverlay : bgSurface
                    radius: 6
                    border.color: accentYellow
                    border.width: 1
                }

                contentItem: Text {
                    text: "Format"
                    font.pixelSize: 12
                    color: accentYellow
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: dictation.formatWithGpt()
            }

            Button {
                id: undoButton
                Layout.preferredWidth: 60
                Layout.preferredHeight: 32
                visible: dictation.canUndo

                background: Rectangle {
                    color: undoButton.down ? bgOverlay : bgSurface
                    radius: 6
                    border.color: accentRed
                    border.width: 1
                }

                contentItem: Text {
                    text: "Undo"
                    font.pixelSize: 12
                    color: accentRed
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: dictation.undoFormat()
            }
        }

        // Help text at bottom
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "v: toggle  y: yank  h: html  f: format  u: undo  o: orig  Esc: close"
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
