import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    width: 600
    height: 400
    visible: false
    title: "popup"
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    color: "#1e1e2e"

    property int selectedIndex: 0
    property bool useOrgMode: false  // false = Markdown, true = Org

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
            var link = useOrgMode
                ? searchModel.getOrgLink(index)
                : searchModel.getMarkdownLink(index)
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

            Keys.onTabPressed: {
                useOrgMode = !useOrgMode
            }

            Keys.onPressed: function(event) {
                if (event.modifiers & Qt.ControlModifier) {
                    // Ctrl+P or Ctrl+K = up
                    if (event.key === Qt.Key_P || event.key === Qt.Key_K) {
                        if (selectedIndex > 0) {
                            selectedIndex--
                            listView.positionViewAtIndex(selectedIndex, ListView.Contain)
                        }
                        event.accepted = true
                    }
                    // Ctrl+N or Ctrl+J = down
                    else if (event.key === Qt.Key_N || event.key === Qt.Key_J) {
                        if (selectedIndex < listView.count - 1) {
                            selectedIndex++
                            listView.positionViewAtIndex(selectedIndex, ListView.Contain)
                        }
                        event.accepted = true
                    }
                }
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
                        text: useOrgMode ? orgLink : markdownLink
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
            height: 28
            color: "#313244"
            radius: 4

            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 8

                Text {
                    text: listView.count > 0 ? listView.count + " results" : ""
                    color: "#6c7086"
                    font.pixelSize: 11
                }

                Item { Layout.fillWidth: true }

                // Link format toggle
                RowLayout {
                    spacing: 4

                    Text {
                        text: "MD"
                        color: useOrgMode ? "#6c7086" : "#89b4fa"
                        font.pixelSize: 11
                        font.bold: !useOrgMode
                    }

                    Switch {
                        id: linkModeSwitch
                        checked: useOrgMode
                        onCheckedChanged: useOrgMode = checked

                        indicator: Rectangle {
                            implicitWidth: 32
                            implicitHeight: 16
                            x: linkModeSwitch.leftPadding
                            y: parent.height / 2 - height / 2
                            radius: 8
                            color: linkModeSwitch.checked ? "#89b4fa" : "#45475a"

                            Rectangle {
                                x: linkModeSwitch.checked ? parent.width - width - 2 : 2
                                y: 2
                                width: 12
                                height: 12
                                radius: 6
                                color: "#cdd6f4"

                                Behavior on x {
                                    NumberAnimation { duration: 100 }
                                }
                            }
                        }
                    }

                    Text {
                        text: "Org"
                        color: useOrgMode ? "#89b4fa" : "#6c7086"
                        font.pixelSize: 11
                        font.bold: useOrgMode
                    }
                }

                Text {
                    text: "│"
                    color: "#45475a"
                    font.pixelSize: 11
                }

                Text {
                    text: "Tab Toggle  ↑↓/^pk/^nj ⏎ Esc"
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
