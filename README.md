# NamePickerChanged
## 基于 NamePicker 二次开发


### 修改内容

1.移除浮窗元素，删除任务栏常驻，即开即用，关闭退出

2.为六代机及以上新设备添加摄像头抽选功能（请注意，没有安装希沃桌面的新设备同样无法抽选，工作原理是调用希沃自带的随机抽选）

![屏幕截图 2025-04-05 151440](https://github.com/user-attachments/assets/f06e329e-dfd5-478c-802c-402328a71987)
3.移去cw开关避免学生乱改，默认配置文件是关闭（可以用记事本编辑，修改"supportCS": false为true即可）

![屏幕截图 2025-04-05 151446](https://github.com/user-attachments/assets/3e6357d4-5c43-489c-b4f6-21f2e0702f9b)
4.移除非二元抽选，需要可以在第84行附近重新添加即可

![屏幕截图 2025-04-05 151430](https://github.com/user-attachments/assets/b593bc39-b46a-41f0-b654-5c35deb7f1a5)
![image](https://github.com/user-attachments/assets/764dc5b2-1668-48ea-be37-50bd5f6e54d0)

5.修改 环保模式 及 程序启动 提示信息

![屏幕截图 2025-04-05 151419](https://github.com/user-attachments/assets/88aa1054-d3cc-4113-88b8-136c06bef294)
![da91edae21f6d020f64ad6933bde2398](https://github.com/user-attachments/assets/551b9eb4-442b-4675-ba9c-d1c1b7b033e3)



### 摄像头抽选功能指南

**原理：替换掉原本的随机抽选，使其直接拉起np，再通过np打开随机抽选**

1.找到LuckyRandom所在文件夹，一般在C:\Program Files (x86)\Seewo\MiniApps下面

2.将LuckyXXXXX.exe更名为LuckyRandomForCam.exe，其他不变

3.把打包好的所有文件拖入同目录下，将main.exe重命名为LuckyXXXXX.exe即可


### 如何打包

**请先下载好mingu64并添加到指定位置，不知道的可以先打包一次看看路径及下载地址，否则可能会因为网络环境提示打包失败**

**建议先去原项目下载assets文件夹避免出现图片图标加载错误**

**请先阅读原项目打包教程创建虚拟环境，如果自带的venv环境有问题，建议使用conda创建虚拟环境**

不带ico图标指令：

nuitka --standalone --include-data-dir=assets=assets --windows-console-mode=attach --enable-plugins=pyqt5 main.py

带ico图标指令，请将图标拖到同目录下：

nuitka --standalone --include-data-dir=assets=assets --windows-console-mode=attach --enable-plugins=pyqt5 --windows-icon-from-ico=./favicon.ico main.py

不想打包？[直接下载](https://www.123684.com/s/bsq9jv-5IzaH)


### 本项目遵循GNU GPLv3开源协议

## 原作者：@LHGS-github	
## 原项目地址：https://github.com/NamePickerOrg/NamePicker
