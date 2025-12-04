import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    width: 600
    height: 400
    visible: true
    title: "popup"
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    color: "#1e1e2e"

    property int selectedIndex: 0

    // Close on escape or focus loss
    onActiveFocusItemChanged: {
        if (!activeFocusItem && visible) {
            // Small delay to check if we really lost focus
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

    // Debounce timer for search
    Timer {
        id: searchTimer
        interval: 150
        onTriggered: {
            searchModel.search(searchField.text)
            selectedIndex = 0
        }
    }

    function selectItem(index) {
        if (index >= 0 && index < listView.count) {
            var link = searchModel.getMarkdownLink(index)
            if (link) {
                clipboard.copy(link)
                root.hide()
                searchField.text = ""
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        // Search input
        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: "Search notes by path..."
            font.pixelSize: 16
            color: "#cdd6f4"
            placeholderTextColor: "#6c7086"

            background: Rectangle {
                color: "#313244"
                radius: 6
                border.color: searchField.activeFocus ? "#89b4fa" : "#45475a"
                border.width: 1
            }

            onTextChanged: {
                searchTimer.restart()
            }

            Keys.onDownPressed: {
                if (selectedIndex < listView.count - 1) {
                    selectedIndex++
                    listView.positionViewAtIndex(selectedIndex, ListView.Contain)
                }
            }

            Keys.onUpPressed: {
                if (selectedIndex > 0) {
                    selectedIndex--
                    listView.positionViewAtIndex(selectedIndex, ListView.Contain)
                }
            }

            Keys.onReturnPressed: {
                selectItem(selectedIndex)
            }

            Keys.onEnterPressed: {
                selectItem(selectedIndex)
            }

            Keys.onEscapePressed: {
                root.hide()
                searchField.text = ""
            }

            Component.onCompleted: {
                forceActiveFocus()
            }
        }

        // Results list
        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: searchModel
            clip: true
            currentIndex: selectedIndex

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }

            delegate: Rectangle {
                width: listView.width
                height: 56
                color: index === selectedIndex ? "#45475a" : "transparent"
                radius: 4

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: selectedIndex = index
                    onClicked: selectItem(index)
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 2

                    Text {
                        Layout.fillWidth: true
                        text: fullPath
                        color: "#cdd6f4"
                        font.pixelSize: 14
                        elide: Text.ElideMiddle
                    }

                    Text {
                        Layout.fillWidth: true
                        text: markdownLink
                        color: "#89b4fa"
                        font.pixelSize: 12
                        font.family: "monospace"
                        elide: Text.ElideRight
                    }
                }
            }

            // Empty state
            Text {
                anchors.centerIn: parent
                visible: listView.count === 0 && searchField.text.length > 0
                text: "No results found"
                color: "#6c7086"
                font.pixelSize: 14
            }

            Text {
                anchors.centerIn: parent
                visible: listView.count === 0 && searchField.text.length === 0
                text: "Type to search..."
                color: "#6c7086"
                font.pixelSize: 14
            }
        }

        // Status bar
        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: "#313244"
            radius: 4

            RowLayout {
                anchors.fill: parent
                anchors.margins: 4

                Text {
                    text: listView.count > 0 ? listView.count + " results" : ""
                    color: "#6c7086"
                    font.pixelSize: 11
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "↑↓ Navigate  ⏎ Select  Esc Close"
                    color: "#6c7086"
                    font.pixelSize: 11
                }
            }
        }
    }

    // Center on screen when shown
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 3 - height / 2
    }

    onVisibleChanged: {
        if (visible) {
            searchField.forceActiveFocus()
            raise()
            requestActivate()
        }
    }
}
