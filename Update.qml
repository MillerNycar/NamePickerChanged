// Camera.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: cameraPage
    title: qsTr("摄像头抽选")

    Column {
        Layout.fillWidth: true
        spacing: 10

        // 配置区域
        SettingCard {
            width: parent.width
            title: qsTr("设置")
            icon: "ic_fluent_settings_20_regular"

            ColumnLayout {
                width: parent.width
                spacing: 10

                RowLayout {
                    Text {
                        text: qsTr("环境变量")
                        Layout.fillWidth: true
                    }

                    TextField {
                        id: appPathInput
                        Layout.fillWidth: true
                        placeholderText: qsTr("程序路径")
                        text: Bridge.GetCfg("General", "cameraAppPath")[0]

                        onTextChanged: {
                            Bridge.SetCfg("General", "cameraAppPath", [text])
                        }
                    }
                }

                RowLayout {
                    Text {
                        text: qsTr("指定参数")
                        Layout.fillWidth: true
                    }

                    TextField {
                        id: appArgsInput
                        Layout.fillWidth: true
                        placeholderText: qsTr("启动参数")
                        text: Bridge.GetCfg("General", "cameraAppArgs")[0]

                        onTextChanged: {
                            Bridge.SetCfg("General", "cameraAppArgs", [text])
                        }
                    }
                }
            }
        }

        // 使用说明
        SettingCard {
            width: parent.width
            title: qsTr("发布者信息")
            icon: "ic_fluent_info_sparkle_20_regular"

            ColumnLayout {
                width: parent.width
                spacing: 15

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "广州视睿电子科技有限公司"
                    font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "Guangzhou Shiru Electronic Technology Co., Ltd"
                    font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "广州视源电子科技股份有限公司"
                    font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "Guangzhou Shiyuan Electronic Technology Co., Ltd"
                    font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "视源股份 CVTE 版权所有 © 2025"
                    font.pixelSize: 14
                }

                Text {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "Copyright © 2025 seewo. All Rights Reserved."
                    font.pixelSize: 14
                }
            }
        }
    }

    // 操作按钮区域
    Button {
        Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
        Layout.fillWidth: true
        Layout.margins: 20
        text: qsTr("使用摄像头抽选")
        highlighted: true
        onClicked: {
            Bridge.startCameraApp()
        }
    }

    // 处理摄像头启动结果
    Connections {
        target: Bridge
        function onCameraResult(success, message) {
            if (success) {
                floatLayer.createInfoBar({
                    severity: Severity.Success,
                    title: qsTr("启动成功，请在打开的新窗口内进行抽选"),
                    text: message
                })
            } else {
                floatLayer.createInfoBar({
                    severity: Severity.Error,
                    title: qsTr("启动失败，请检查设置"),
                    text: message
                })
            }
        }
    }
}
