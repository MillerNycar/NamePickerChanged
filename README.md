# NamePickerChanged
## 基于 NamePicker 二次开发


### 修改内容

1.移除浮窗元素，删除任务栏常驻，即开即用，关闭退出
2.为六代机及以上新设备添加摄像头抽选功能（请注意，没有安装希沃桌面的新设备同样无法抽选，工作原理是调用希沃自带的随机抽选）
![屏幕截图 2025-04-05 151440](https://github.com/user-attachments/assets/f06e329e-dfd5-478c-802c-402328a71987)
3.移去cw开关避免学生乱改，默认配置文件是关闭（可以用记事本编辑，修改"supportCS": false为true即可）
![屏幕截图 2025-04-05 151446](https://github.com/user-attachments/assets/3e6357d4-5c43-489c-b4f6-21f2e0702f9b)
4.移除非二元抽选，需要添加可以在第84行附近重新添加即可
![屏幕截图 2025-04-05 151430](https://github.com/user-attachments/assets/b593bc39-b46a-41f0-b654-5c35deb7f1a5)
![image](https://github.com/user-attachments/assets/764dc5b2-1668-48ea-be37-50bd5f6e54d0)
5.修改环保模式提示
![屏幕截图 2025-04-05 151419](https://github.com/user-attachments/assets/88aa1054-d3cc-4113-88b8-136c06bef294)


### 摄像头抽选功能指南：

1.找到luckyradom所在文件夹，一般在c→pf→seewo→desk→miniapp下面
2.将luckyrandom.exe更名为LuckyRandomForCam.exe，其他不变
3.把zip解压并把文件拖入同目录下，将main.exe重命名为luckxxxxxxxxx即可


### 如何打包
请先下载好mingu64并添加到指定位置，不知道的可以先打包一次看看路径及下载地址，否则可能会因为网络环境提示打包失败
建议先去原项目下载assets文件夹避免出现图片图标加载错误

不带ico图标指令：
nuitka --standalone --include-data-dir=assets=assets --windows-console-mode=attach --enable-plugins=pyqt5 main.py
带ico图标指令，请将图标拖到同目录下：
nuitka --standalone --include-data-dir=assets=assets --windows-console-mode=attach --enable-plugins=pyqt5 --windows-icon-from-ico=./favicon.ico main.py


## 原作者：@LHGS-github	
## 原项目地址：https://github.com/NamePickerOrg/NamePicker
