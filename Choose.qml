import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    width: parent.width
    Column{
        Layout.fillWidth: true
        Layout.alignment: parent.left
        width: parent.width
        spacing: 10
        ListView{
            id: nameList
            textRole: "name"
            width: parent.width
            height: 370
            model:ListModel {
                id: studentsModel
                ListElement { name: qsTr("别紧张...")}
            }
        }
        Button{
            width: parent.width
            highlighted: true
            text: qsTr("点击抽选")
            onClicked: {
                var pk = Bridge.Pick(chooseNum.value)
                if(pk[0]!="bydcnm"){
                    studentsModel.clear()
                    for(var i = 0; i < pk.length; i++){
                        studentsModel.append({name: pk[i]})
                    }
                }
                else{
                    floatLayer.createInfoBar({
                        severity: Severity.Error,
                        title: qsTr("Error"),
                        text: qsTr(pk[1])
                    })
                }
            }
        }
        RowLayout{
            Layout.fillWidth: true
            Layout.alignment: parent.left
            width: parent.width
            Text{
                typography:Typography.Body
                text: qsTr("抽选数量")
            }
            SpinBox {
                id: chooseNum
                width: parent.width
                Layout.alignment: Qt.AlignRight
                validator: IntValidator
                from: 1
                to: 40
            }
        }
        RowLayout{
            Layout.fillWidth: true
            width: parent.width
            Text{
                typography:Typography.Body
                text: qsTr("选择性别偏好")
            }
            ComboBox {
                id: sexCombo
                Layout.alignment: Qt.AlignRight
                model: ["全部抽选", "只抽男生", "只抽女生"]
                currentIndex: 0
                placeholderText: qsTr("选择性别偏好")
                onCurrentIndexChanged: {
                    Bridge.setSexFavor(sexCombo.currentText)
                }
            }
        }
        RowLayout{
            Layout.fillWidth: true
            Layout.alignment: parent.left
            width: parent.width
            Text{
                typography:Typography.Body
                text: qsTr("选择学号偏好")
            }
            ComboBox {
                id: numCombo
                Layout.alignment: Qt.AlignRight
                model: ["全部抽选", "只抽单数", "只抽双数"]
                currentIndex: 0
                placeholderText: qsTr("选择学号偏好")
                onCurrentTextChanged: {
                    Bridge.setNumFavor(numCombo.currentText)
                }
            }
        }
        RowLayout{
            Layout.fillWidth: true
            width: parent.width
            Text{
                typography:Typography.Body
                text: qsTr("选择抽选名单")
            }
            ComboBox {
                id: nameCombo
                Layout.alignment: Qt.AlignRight
                model: Bridge.getNameList()
                currentIndex: 0
                placeholderText: qsTr("选择抽选名单")
                onCurrentTextChanged: {
                    Bridge.changeNameList(currentIndex)
                }
            }
        }
    }
}
