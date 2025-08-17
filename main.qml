import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import Qt.labs.platform 1.1 as Platform
import "../assets/"
import RinUI

FluentWindow {
    id: window
    visible: true
    title: qsTr("NamePicker")
    icon: Qt.resolvedUrl("../assets/NamePicker.png")
    width: 900
    height: 700
    minimumWidth: 550
    minimumHeight: 400
    navigationItems: [
        {
            title: "随机抽选",
            page: Qt.resolvedUrl("Choose.qml"),
            icon: "ic_fluent_home_20_regular",
        },
        {
            title: "摄像头抽选",
            page: Qt.resolvedUrl("Update.qml"),
            icon: "ic_fluent_camera_20_regular",
        },
        {
            title: "设置",
            page: Qt.resolvedUrl("Settings.qml"),
            icon: "ic_fluent_settings_20_regular",
        },
        {
            title: "关于",
            page: Qt.resolvedUrl("About.qml"),
            icon: "ic_fluent_info_20_regular",
        }
    ]
    // Platform.SystemTrayIcon {
    //     id: trayIcon
    //     visible: true
    //     icon.source: Qt.resolvedUrl("../assets/NamePicker.png")
    //     tooltip: qsTr("NamePicker")
    //     menu: Platform.Menu {
    //         Platform.MenuItem {
    //             text: qsTr("显示主窗口")
    //             onTriggered: {
    //                 window.show()
    //                 window.raise()
    //             }
    //         }
    //         Platform.MenuItem {
    //             text: qsTr("隐藏主窗口")
    //             onTriggered: {
    //                 window.hide()
    //             }
    //         }
    //         Platform.MenuSeparator {}
    //         Platform.MenuItem {
    //             text: qsTr("退出")
    //             onTriggered: Qt.quit()
    //         }
    //     }
    //     onActivated: {
    //         if (window.visible) {
    //             window.hide()
    //         } else {
    //             window.show()
    //             window.raise()
    //         }
    //     }
    // }
    onClosing: {
        if (Qt.platform.os === "windows" || Qt.platform.os === "linux") {
            close.accepted = false
            window.hide()
        }
    }
}
