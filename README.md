# NamePicker v2.2.0 For Shiru
## 基于 NamePicker v2.2.0d4rel 二次开发
## 本人已上高三没时间再开发，这大概率是最后一版NamePickerChanged了，本项目大概率不再更新(至少高三这一年)，喜欢就拿走吧！

## 由于此版本代码量过大，不适合作为后台API服务，且上一次修改后存在未知或者奇奇怪怪的问题，所以API服务改用一点1.1.0的版本来开发，请[点击访问](https://github.com/MillerNycar/NamePickerChanged/tree/1.1.0)

### 修改内容

1.去除悬浮窗元素，删除有关更新的代码；

~~2.新增参数-ban；未带参数运行时直接启动主界面，并在主界面关闭后退出程序；带参数运行时，首次启动后台驻留，再次运行时打开主界面，当主界面关闭时不会退出程序；允许在带参数运行时多开主界面，不允许程序多开运行；~~

~~3.新增api端口，默认在127.0.0.1:32763上开放通信端口，在配置文件中新增ip与端口参数，当接收到通信 kscx4cw 时，自动完成一次抽选，若联动插件已开启，则与cw联动；~~

4.新增 摄像头抽选 左侧栏目，抽选时启动对应路径程序；

5.修改抽选数量逻辑，当抽选数量大于3时，取消与插件联动，并以默认显示方式显示抽选结果；若小于等于3且插件联动已启用，则与插件联动；

6.新增QuickPicker快捷抽选程序，使用Python语言编写，无GUI配置界面，无后台驻留，无日志文件，实现启动后向点名软件发送特定字符串 kscx4cw ，执行完成之后关闭；使用json配置文件，配置文件中包含通信ip以及端口号，可根据需求修改；

7.其他主界面显示内容修改.

<img width="1858" height="1454" alt="image" src="https://github.com/user-attachments/assets/ba85d555-dff5-4718-b44f-2c55841701cb" />

<img width="2880" height="1800" alt="image" src="https://github.com/user-attachments/assets/5d8f5f41-a44a-429c-ad83-df40b441bee0" />

<img width="1830" height="1429" alt="image" src="https://github.com/user-attachments/assets/201c5094-91f2-42a1-aad9-fedfc2ee6d7f" />

<img width="1834" height="1441" alt="image" src="https://github.com/user-attachments/assets/c57691b7-d591-4a67-a3e4-3bff3e5584d6" />

<img width="1827" height="1429" alt="image" src="https://github.com/user-attachments/assets/6d59f857-b729-4c62-9409-0726620b2248" />


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


### 已知问题：bug一堆

本人代码水平较差，不知道怎么解决，欢迎大佬提意见或自行修改.

1.内存占用比较高，对于仅有8G的"希沃大板砖"非常不友好；

2.性别和学号偏好抽选无效（不是哥们，原版也有这个问题，我硬是改了5次都还是不行，实在是没办法了）；

~~3.日志变成垃圾堆(懒得管了只要不是太多就死不了)；~~

~~4.带不带参数都无法正常在关闭主窗口的时候退出程序，托盘菜单时有时无，导致程序直接变成允许多开(没啥头绪，上课别崩就行).~~


### 本项目遵循GNU GPLv3开源协议

### NamePicker官方[QQ群](https://qm.qq.com/q/fTjhKuAlCU)

## 原作者：[@LHGS-github](https://github.com/LHGS-github)
## 原项目地址：https://github.com/NamePickerOrg/NamePicker
