import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI
import Qt5Compat.GraphicalEffects

FluentPage {
    horizontalPadding: 0
    wrapperWidth: width - 42*2

    contentHeader: Item {
        width: parent.width
        height: Math.max(window.height * 0.4, 200)

        Image {
            id: banner
            anchors.fill: parent
            source: "../assets/banner.png"
            fillMode: Image.PreserveAspectCrop
            verticalAlignment: Image.AlignTop

            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    width: banner.width
                    height: banner.height
                    gradient: Gradient {
                        GradientStop { position: 0.7; color: "white" }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
            }
        }
    }

    Column {
        Layout.fillWidth: true
        spacing: 3   
        Text{
            typography: Typography.Title
            text: "关于NamePicker"
        }

        SettingCard {
            width: parent.width
            title: qsTr(Bridge.VerTxt)
            icon: "ic_fluent_info_sparkle_20_regular"
        }
        SettingCard {
            width: parent.width
            title: qsTr("检查更新")
            description: qsTr("当前已是最新版本")
            icon: "ic_fluent_arrow_sync_checkmark_20_regular"
        }
        SettingCard {
            width: parent.width
            title: qsTr("作者")
            description: qsTr("by Nycar （基于 灵魂歌手er 二次开发）")
            icon: "ic_fluent_people_20_regular"
        }
        SettingCard {
            width: parent.width
            title: qsTr("开源许可")
            description: qsTr("使用 GPL-3.0 开源许可协议")
            icon: "ic_fluent_document_20_regular"
        }
    }
    Column{
        Layout.fillWidth: true
        spacing: 3  
        Text{
            typography: Typography.Subtitle
            text: "相关链接"
        }
        SettingCard {
            width: parent.width
            title: qsTr("官方文档")
            description: qsTr("点击查看官方文档")
            icon: "ic_fluent_document_20_regular"
            content: Hyperlink {
                text: qsTr("点击跳转")
                openUrl: "https://namepicker-docs.netlify.app"
                enabled: false
            }
        }
        SettingCard {
            width: parent.width
            title: qsTr("GitHub仓库")
            description: qsTr("觉得满意的话欢迎Star")
            icon: "ic_fluent_box_20_regular"
            content: Hyperlink {
                text: qsTr("点击跳转")
                openUrl: "https://github.com/NamePickerOrg/NamePicker"
                enabled: false
            }
        }
    }
}
