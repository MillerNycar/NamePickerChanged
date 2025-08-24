# NamePicker v2.2.0 For Shiru
## 基于 NamePicker v2.2.0d4rel 二次开发
## 本人已上高三没时间再开发，这大概率是最后一版NamePickerChanged了，本项目大概率不再更新(至少高三这一年)，喜欢就拿走吧！

## 由于此版本代码量过大，不适合作为后台API服务，且上一次修改后存在未知或者奇奇怪怪的问题，所以API服务改用一点1.1.0的版本来开发，请[点击访问](https://github.com/MillerNycar/NamePickerChanged/tree/1.1.0)

### 修改内容

1.去除悬浮窗元素，删除有关更新的代码；实现运行直接打开主界面，关闭主界面后程序退出；

~~2.新增参数-ban；未带参数运行时直接启动主界面，并在主界面关闭后退出程序；带参数运行时，首次启动后台驻留，再次运行时打开主界面，当主界面关闭时不会退出程序；允许在带参数运行时多开主界面，不允许程序多开运行；~~

~~3.新增api端口，默认在127.0.0.1:32763上开放通信端口，在配置文件中新增ip与端口参数，当接收到通信 kscx4cw 时，自动完成一次抽选，若联动插件已开启，则与cw联动；~~

4.新增 摄像头抽选 左侧栏目，抽选时启动对应路径程序；

5.修改抽选数量逻辑，当抽选数量大于3时，取消与插件联动，并以默认显示方式显示抽选结果；若小于等于3且插件联动已启用，则与插件联动；

6.新增QuickPicker快捷抽选程序，使用Python语言编写，无GUI配置界面，无后台驻留，无日志文件，实现启动后向点名软件发送特定字符串 kscx4cw ，执行完成之后关闭；使用json配置文件，配置文件中包含通信ip以及端口号，可根据需求修改；

7.其他主界面显示内容修改（关闭了关于界面中的跳转相关链接，防手贱，可以自己在qml中改回来）.

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/5355453d-13a3-4ed5-8022-fda2b4c73c32" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/d8bde6e8-35c9-429a-b1f5-4889c46dea8c" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/27fd4772-5c18-4761-846d-85c416efa0b9" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/919d4106-9802-436d-b526-45d66fecf40e" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/0995ccaa-44a0-4f2c-95e5-a08e4e6b7a92" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/c6b01a5f-395f-4176-8744-914f4ad703c3" />

### 摄像头抽选功能

在摄像头抽选栏目填写程序路径，LuckyRandom默认在C:\Program Files (x86)\Seewo\SEEWO-FAMILY-BUCKET\MiniApps下，不需要指定参数，当然也可以启动其他程序.


### QuickPicker

API服务已关闭，QuickPicker不再适合本版本的代码，如果需要，请切换到1.1.0。

如要使用QuickPicker，替换掉机器自带的摄像头随机抽选，则需要将LuckyRandom.exe更名为LuckyRandomForCam.exe，将QuickPicker.exe重命名为LuckyRandom.exe；同时NamePicker摄像头抽选栏目程序路径要注意更换名称.

注意：要把NamePicker设置为开机自启动，如果np没启动，QuickPicker是无法实现抽选的.


### 如何打包

**请先先去[原项目](https://github.com/NamePickerOrg/NamePicker)下载完整项目；下载完成后，将本分支内容下载并替换掉原来的main.py以及pages文件夹中的内容**


1.(可选)创建虚拟环境，建议使用[conda](https://anaconda.org/anaconda/conda)创建虚拟环境.

2. 安装依赖项.
pip install -r requirements.txt

3. 在虚拟环境中运行.
pyinstaller main.spec


### 已知问题

本人代码水平较差，不知道怎么解决，欢迎大佬提意见或自行修改.

1.内存占用比较高，对于仅有8G的"希沃大板砖"非常不友好；

~~2.性别和学号偏好抽选无效（不是哥们，原版也有这个问题，我硬是改了5次都还是不行，实在是没办法了）~~ [终于修复了，******{做个文明的开发者}]

~~3.日志变成垃圾堆(懒得管了只要不是太多就死不了)；~~

~~4.带不带参数都无法正常在关闭主窗口的时候退出程序，托盘菜单时有时无，导致程序直接变成允许多开(没啥头绪，上课别崩就行).~~


### 本项目遵循GNU GPLv3开源协议

### NamePicker官方[QQ群](https://qm.qq.com/q/fTjhKuAlCU)

## 原作者：[@LHGS-github](https://github.com/LHGS-github)
## 原项目地址：https://github.com/NamePickerOrg/NamePicker
