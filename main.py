import json
import time
import base64
import hashlib
import socket
import os
import sys
import tempfile
import random
import traceback
import subprocess
from loguru import logger
import pyotp
import qrcode
from PySide6.QtCore import QObject, Slot, Property, Signal, QThread
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from RinUI import RinUIWindow

if os.name == 'nt':
    from win32com.client import Dispatch

temp_dir = tempfile.gettempdir()
VERSION = "v2.2.0 For Shiru"
CODENAME = "Fugue"
VER_NO = 7
APIVER = 2
SEXFAVOR_ALL = NUMFAVOR_BOTH = -1
SEXFAVOR_BOY = NUMFAVOR_1 = 0
SEXFAVOR_GIRL = NUMFAVOR_2 = 1

if not sys.stderr:
    class FakeStderr:
        def __init__(self):
            pass
        def write(self, message):
            pass
        def flush(self):
            pass
        def isatty(self):
            return True
    sys.stderr = FakeStderr()

def hook_exceptions(exc_type, exc_value, exc_tb):
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    if "TypeError: disconnect() of all signals failed" in error_details:
        return
    logger.error(error_details)

sys.excepthook = hook_exceptions

def resource_path(relative_path:str)-> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

class Choose:
    def __init__(self, path:str):
        self.names = []
        self.namel = []
        self.sexFavor = SEXFAVOR_ALL
        self.numFavor = NUMFAVOR_BOTH
        self.load_names(path)

    def load_names(self, path:str) -> None:
        try:
            self.names = []
            self.namel = []
            with open(path, "r", encoding="utf-8") as f:
                fl = f.readlines()
            head = fl[0].strip("\n").split(",")
            del fl[0]
            for i in range(len(fl)):
                l = fl[i].strip("\n").split(",")
                struct = {}
                for j in range(len(head)):
                    struct[head[j]] = l[j]
                self.names.append(struct)
                self.namel.append(i)
        except (UnicodeDecodeError, IndexError):
            logger.warning("名单文件无效")
            os.remove(path)
            if not os.path.exists("names"):
                os.makedirs("names")
            with open(path, "w", encoding="utf-8") as f:
                f.write("name,sex,no\n某人,0,1")
        except FileNotFoundError:
            logger.warning("没有找到指定文件")
            if not os.path.exists("names"):
                os.makedirs("names")
            with open(path, "w", encoding="utf-8") as f:
                f.write("name,sex,no\n某人,0,1")
        self.load_favor()

    def load_favor(self) -> None:
        self.namel = []
        for i in range(len(self.names)):
            sex_ok = (self.sexFavor == SEXFAVOR_ALL) or \
                     (self.sexFavor == SEXFAVOR_BOY and int(self.names[i]["sex"]) == 0) or \
                     (self.sexFavor == SEXFAVOR_GIRL and int(self.names[i]["sex"]) == 1)
            
            num_val = int(self.names[i]["no"])
            num_ok = (self.numFavor == NUMFAVOR_BOTH) or \
                     (self.numFavor == NUMFAVOR_1 and num_val % 2 == 1) or \
                     (self.numFavor == NUMFAVOR_2 and num_val % 2 == 0)
            
            if sex_ok and num_ok:
                self.namel.append(i)

    def set_sex_favor(self, target:int) -> None:
        self.sexFavor = target
        self.load_favor()

    def set_num_favor(self, target:int) -> None:
        self.numFavor = target
        self.load_favor()

    def pick(self, num:int=1) -> list:
        resi = []
        res = []
        for i in range(num):
            if not self.namel:
                logger.warning("名单为空，重新加载偏好")
                self.load_favor()
                if not self.namel:
                    return ["名单为空"]
                
            if not cfg.get("General", "allowRepeat") and self.namel:
                ans = random.choice(self.namel)
                resi.append(ans)
                self.namel.remove(ans)
            else:
                resi.append(random.choice(self.namel))

        for i in resi:
            res.append(self.names[i])
        return res

def set_startup() -> None:
    if os.name != 'nt':
        return
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/main.exe'
    icon_path = 'assets/favicon.ico'
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    name = os.path.splitext(os.path.basename(file_path))[0]
    shortcut_path = os.path.join(startup_folder, f'{name}.lnk')
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = file_path
    shortcut.WorkingDirectory = os.path.dirname(file_path)
    shortcut.IconLocation = icon_path
    shortcut.save()

def remove_startup() -> None:
    if os.name != 'nt':
        return
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/main.exe'
    name = os.path.splitext(os.path.basename(file_path))[0]
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, f'{name}.lnk')
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

def mac_addr() -> str:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    mac_address = ':'.join(['{:02x}'.format((int(i, 16) & 0xff)) for i in hex(int(ip_address.split('.')[0])).split('0x')[1:]])
    return mac_address

class Config:
    def __init__(self, filename:str, rules:dict, default:dict):
        self.filename = filename
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.cfgf = f.read()
                self.cfg = json.loads(self.cfgf)
            for i in list(rules.keys()):
                if i not in self.cfg.keys():
                    self.cfg[i] = default[i]
                    continue
                for j in list(rules[i].keys()):
                    if j not in self.cfg[i].keys():
                        self.cfg[i][j] = default[i][j]
                    elif not self.val(i, j, self.cfg[i][j], rules):
                        self.cfg[i][j] = default[i][j]
        except FileNotFoundError:
            logger.warning("未找到配置文件，将创建默认配置")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(default))
            self.cfg = default
        except json.JSONDecodeError:
            logger.warning("无效的配置文件")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(default))
            self.cfg = default

    def val(self, i:str, j:str, chk:any, rules:dict) -> bool:
        try:
            if type(rules[i][j]) == list:
                if ((rules[i][j][0] == "range" and (rules[i][j][1] > chk or rules[i][j][2] < chk)) 
                    or (rules[i][j][0] == "option" and chk not in rules[i][j]) 
                    or (rules[i][j][0] == "list" and type(chk) != list)):
                    return False
            elif type(chk) != rules[i][j]:
                return False
            else:
                return True
        except KeyError:
            return False

    def get(self, cls:str, key:str) -> any:
        return self.cfg[cls][key]
    
    def set(self, cls:str, key:str, val) -> None:
        self.cfg[cls][key] = val
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.cfg))

CFGRULE = {
    "General": {
        "allowRepeat": bool,
        "autoStartup": bool,
        "chooseKey": str,
        "supportCS": bool,
        "autoCheck": bool,
        "apiIP": str,
        "apiPort": int,
        "cameraAppPath": str,
        "cameraAppArgs": str
    },
    "Secure": {"lock":bool, "password":str, "require2FA":bool, "2FAMethod":str, "OTPnote":str},
    "Version": {"apiver": ["range", 2, 2], "channel":["option", "rel", "dev"]},
    "Huanyu": {"ecoMode": bool, "justice": bool},
    "Debug": {"logLevel": ["option", "DEBUG", "INFO", "WARNING", "ERROR"]}
}

CFGDEFAULT = {
    "General": {
        "allowRepeat": False,
        "autoStartup": False,
        "chooseKey": "ctrl+w",
        "supportCS": False,
        "autoCheck": False,
        "apiIP": "127.0.0.1",
        "apiPort": 32763,
        "cameraAppPath": "",
        "cameraAppArgs": ""
    },
    "Secure": {"lock":False, "password":"", "require2FA":False, "2FAMethod":"otp", "OTPnote":""},
    "Version": {"apiver": 2, "channel":"rel"},
    "Huanyu": {"ecoMode": False, "justice": False},
    "Debug": {"logLevel": "INFO"}
}

cfg = Config("config.json", CFGRULE, CFGDEFAULT)

log_file = "out.log"
try:
    if os.path.exists(log_file):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        os.rename(log_file, f"out_{timestamp}.log")
except Exception as e:
    print(f"无法重命名日志文件: {e}")

logger.add(log_file, rotation="1 MB")
logger.add(sys.stderr, level=cfg.get("Debug", "logLevel"))
logger.info(f"NamePicker {VERSION} - Codename {CODENAME} (Inside version {VER_NO}, Plugin API Version {APIVER})")
logger.info("「历经生死、重获新生的忘归人，何时才能返乡？⌋")

try:
    core = Choose(f"names/{os.listdir('names')[0]}")
except (FileNotFoundError, IndexError):
    logger.warning("没有找到名单文件")
    if not os.path.exists("names"):
        os.makedirs("names")
    with open("names/names.csv", "w", encoding="utf-8") as f:
        f.write("name,sex,no\n某人,0,1")
    core = Choose("names/names.csv")

class APIServer(QThread):
    dataReceived = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.server_socket = None
        
    def run(self):
        ip = cfg.get("General", "apiIP")
        port = cfg.get("General", "apiPort")
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(0.5)
        
        try:
            self.server_socket.bind((ip, port))
            self.server_socket.listen(1)
            logger.info(f"API服务器启动，监听 {ip}:{port}")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    logger.info(f"收到来自 {addr} 的连接")
                    
                    data = client_socket.recv(1024).decode('utf-8')
                    if data:
                        self.dataReceived.emit(data)
                        response = "OK"
                    else:
                        response = "ERROR"
                    
                    client_socket.send(response.encode('utf-8'))
                    client_socket.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"API服务器错误: {str(e)}")
        except Exception as e:
            if self.running:
                logger.error(f"API服务器启动失败: {str(e)}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            logger.info("API服务器已停止")
    
    def stop(self):
        if not self.isRunning():
            return
            
        logger.info("正在停止API服务器...")
        self.running = False
        if self.wait(1000):
            logger.info("API服务器已安全停止")
        else:
            logger.warning("API服务器未在指定时间内停止，强制终止")
            self.terminate()

class UI(RinUIWindow):
    def __init__(self):
        super().__init__(resource_path("pages/main.qml"))
        self.bridge = Bridge()
        self.engine.rootContext().setContextProperty("Bridge", self.bridge)

    def closeEvent(self, event):
        logger.info("主窗口关闭，清理资源...")
        if self.bridge:
            self.bridge.cleanup()
        event.accept()
        super().closeEvent(event)
        
    def deleteLater(self):
        logger.info("UI资源完全释放")
        if self.bridge:
            self.bridge.cleanup()
            self.bridge = None
        super().deleteLater()

class Bridge(QObject):
    showMessage = Signal(str, str)
    cameraResult = Signal(bool, str)
    aboutToQuit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verified = False
        self.mac = mac_addr()
        self.secret_key = base64.b32encode(self.mac.encode(encoding="utf-8"))
        self.totp = pyotp.TOTP(self.secret_key)
        
        a = cfg.get("Secure", "2FAMethod").split(",")
        self.methods = a if a != [""] else []
        
        self.api_server = APIServer()
        self.api_server.dataReceived.connect(self.handle_api_request)
        self.api_server.start()

    def handle_api_request(self, data: str):
        logger.debug(f"收到API请求: {data}")
        if data.strip() == "[kscx4cw]":
            r = core.pick(1)
            re = []
            if r != ["bydcnm"]:
                for i in r:
                    re.append(f"{i['name']}({i['no']})")
                
                if len(re) <= 3 and cfg.get("General", "supportCS"):
                    with open(f"{temp_dir}/unread", "w", encoding="utf-8") as f:
                        f.write("91")
                    with open(f"{temp_dir}/res.txt", "w", encoding="utf-8") as f:
                        f.write(",".join(re))
                    logger.info("API抽选完成并与插件联动")
                else:
                    logger.info("API抽选完成，未联动")
            else:
                logger.warning("API抽选失败")
    
    def cleanup(self):
        logger.info("执行资源清理")
        
        if self.api_server and self.api_server.isRunning():
            try:
                self.api_server.dataReceived.disconnect()
                self.api_server.stop()
            except Exception as e:
                logger.error(f"停止API服务器时出错: {str(e)}")
            self.api_server = None
        
        try:
            self.showMessage.disconnect()
            self.cameraResult.disconnect()
        except:
            pass
        
        self.deleteLater()
        logger.info("资源清理完成")

    @Slot(str, result=list)
    def Pick(self, num:str) -> list:
        try:
            num_int = int(num)
            r = core.pick(num_int)
            re = []
            if r and r[0] == "名单为空":
                return ["名单为空"]
                
            for i in r:
                re.append(f"{i['name']}({i['no']})")
            
            if num_int > 3:
                self.showMessage.emit("数量超出限制", "抽选数量大于3，无法与插件联动")
            elif cfg.get("General", "supportCS") and re:
                with open(f"{temp_dir}/unread", "w", encoding="utf-8") as f:
                    f.write("91")
                with open(f"{temp_dir}/res.txt", "w", encoding="utf-8") as f:
                    f.write(",".join(re))
                logger.info("抽选完成并与插件联动")
            
            return re
        except Exception as e:
            logger.error(f"抽选出错: {str(e)}")
            return ["抽选出错"]

    @Slot(str, str, result=list)
    def GetCfg(self, cls:str, key:str) -> list:
        return [cfg.get(cls, key)]
    
    @Slot(result=int)
    def GetNLen(self) -> int:
        return len(core.names)
    
    @Slot(str, str, list)
    def SetCfg(self, cls:str, key:str, val:list) -> list:
        cfg.set(cls, key, val[0])

    @Slot(int, result=int)
    def GetDbg(self, cls:int) -> int:
        return ["DEBUG", "INFO", "WARNING", "ERROR"].index(cfg.get("Debug", "logLevel"))

    @Slot(bool)
    def Startup(self, stat:bool) -> None:
        if stat:
            set_startup()
        else:
            remove_startup()

    @Slot(str, result=bool)
    def VerifyPassword(self, password:str) -> bool:
        return hashlib.md5(password.encode(encoding='UTF-8')).hexdigest() == cfg.get("Secure", "password")
    
    @Slot(bool)
    def setVerified(self, vl:bool) -> None:
        self.verified = vl

    @Slot(result=bool)
    def getVerified(self) -> bool:
        if self.verified:
            return True
        else:
            return not cfg.get("Secure", "lock")
    
    @Slot(str)
    def setPassword(self, password:str) -> None:
        cfg.set("Secure", "password", hashlib.md5(password.encode(encoding='UTF-8')).hexdigest())

    @Slot(str, result=bool)
    def VerifyOTP(self, code:str) -> bool:
        return self.totp.verify(code)
        
    @Slot(int, result=int)
    def Get2FA(self, cls:int) -> int:
        return ["otp"].index(cfg.get("Secure", "2FAMethod"))
    
    @Property(str)
    def GetOTPSecret(self) -> str:
        return self.secret_key.decode()
    
    @Slot(str)
    def GenTOTPImg(self, note:str) -> None:
        cfg.set("Secure", "OTPnote", note)
        totp_url = self.totp.provisioning_uri(f"NamePicker/{note}", issuer_name="NamePicker 2FA")
        qr = qrcode.make(totp_url)
        qr.save("qr.png")

    @Slot(bool)
    def chgStartup(self, stat:bool) -> None:
        cfg.set("General", "autoStartup", stat)
        if stat:
            set_startup()
        else:
            remove_startup()

    @Property(str)
    def VerTxt(self) -> str:
        return f"当前版本：{VERSION}"
    
    @Slot(str)
    def setSexFavor(self, sexf:str) -> None:
        if sexf == "全部抽选":
            core.set_sex_favor(SEXFAVOR_ALL)
        elif sexf == "只抽男生":
            core.set_sex_favor(SEXFAVOR_BOY)
        elif sexf == "只抽女生":
            core.set_sex_favor(SEXFAVOR_GIRL)
        logger.info(f"设置性别偏好: {sexf} ({core.sexFavor})")
    
    @Slot(str)
    def setNumFavor(self, numf:str) -> None:
        if numf == "全部抽选":
            core.set_num_favor(NUMFAVOR_BOTH)
        elif numf == "只抽单数":
            core.set_num_favor(NUMFAVOR_1)
        elif numf == "只抽双数":
            core.set_num_favor(NUMFAVOR_2)
        logger.info(f"设置学号偏好: {numf} ({core.numFavor})")

    @Slot(result=list)
    def getNameList(self) -> list:
        return os.listdir("names")
    
    @Slot(int)
    def changeNameList(self, path:int) -> None:
        try:
            name_file = os.listdir("names")[path]
            logger.info(f"切换到名单: {name_file}")
            core.load_names(f"names/{name_file}")
        except (IndexError, FileNotFoundError):
            logger.error("切换名单失败")

    @Property(int)
    def getDwn(self) -> int:
        return 0
    
    @Property(str)
    def getStat(self) -> str:
        return "1"
    
    @Slot(str)
    def add2FA(self, s:str):
        t = set(self.methods)
        t.add(s)
        self.methods = list(t)
        cfg.set("Secure", "2FAMethod", ",".join(self.methods))

    @Slot(str)
    def rem2FA(self, s:str):
        t = set(self.methods)
        t.remove(s)
        self.methods = list(t)
        cfg.set("Secure", "2FAMethod", ",".join(self.methods))

    @Property(list)
    def get2FA(self):
        readable = []
        for method in self.methods:
            if method == "otp":
                readable.append("2FA APP")
        return [self.methods, readable]
    
    @Slot(str, result=bool)
    def have2FA(self, s:str):
        return s in self.methods
    
    @Slot()
    def startCameraApp(self):
        app_path = cfg.get("General", "cameraAppPath")
        app_args = cfg.get("General", "cameraAppArgs")
        
        if not app_path:
            self.cameraResult.emit(False, "未配置摄像头应用")
            return
            
        try:
            args_list = app_args.split() if app_args else []
            subprocess.Popen([app_path] + args_list)
            self.cameraResult.emit(True, "摄像头应用启动成功")
            logger.info(f"启动摄像头应用: {app_path} {app_args}")
        except Exception as e:
            error_msg = f"启动失败: {str(e)}"
            self.cameraResult.emit(False, error_msg)
            logger.error(f"启动摄像头应用失败: {str(e)}")
    
    @Slot(result=list)
    def getAPIConfig(self):
        return [
            cfg.get("General", "apiIP"),
            cfg.get("General", "apiPort")
        ]

class SingleInstance:
    def __init__(self, lock_id):
        self.lock_id = lock_id
        self.lockfile = os.path.join(tempfile.gettempdir(), f"{lock_id}.lock")
        self.fd = None
        
    def is_running(self):
        if os.path.exists(self.lockfile):
            try:
                with open(self.lockfile, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    os.kill(pid, 0)
                    return True
                except ProcessLookupError:
                    return False
                except PermissionError:
                    return True
                except OSError:
                    return False
                    
            except (ValueError, IOError):
                return False
        return False
        
    def acquire(self):
        if self.is_running():
            return False
            
        try:
            self.fd = open(self.lockfile, 'w')
            self.fd.write(str(os.getpid()))
            self.fd.flush()
            return True
        except IOError:
            return False
        
    def release(self):
        if self.fd:
            try:
                self.fd.close()
            except:
                pass
            self.fd = None
            
        try:
            if os.path.exists(self.lockfile):
                os.remove(self.lockfile)
        except:
            pass

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(resource_path("assets/NamePickerCircle.png")))
        self.menu = QMenu()
        self.product_name = self.menu.addAction("NamePicker")
        self.menu.addSeparator()
        self.show_action = self.menu.addAction("显示主界面")
        self.res_action = self.menu.addAction("重启")
        self.exit_action = self.menu.addAction("退出")
        self.show_action.triggered.connect(self.show_main_window)
        self.res_action.triggered.connect(self.restart)
        self.exit_action.triggered.connect(QApplication.quit)
        self.setContextMenu(self.menu)
        self.main_window = None
    
    def show_main_window(self) -> None:
        if self.main_window is None or not self.main_window.isVisible():
            self.main_window = UI()
            self.main_window.show()
        else:
            self.main_window.activateWindow()
    
    def restart(self) -> None:
        self.hide()
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    def deleteLater(self):
        if self.main_window:
            self.main_window.deleteLater()
            self.main_window = None
        super().deleteLater()

def global_cleanup():
    logger.info("应用程序退出，执行全局清理")
    
    if 'instance_lock' in globals() and instance_lock:
        instance_lock.release()
    
    import gc
    gc.collect()
    logger.info("全局清理完成")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/favicon.ico")))
    
    app.aboutToQuit.connect(global_cleanup)
    
    instance_lock = SingleInstance("NamePickerLock")
    
    ban_mode = "-ban" in sys.argv
    
    if ban_mode:
        if instance_lock.is_running():
            tray = TrayIcon()
            tray.show_main_window()
            app.exec()
        else:
            if instance_lock.acquire():
                tray = TrayIcon()
                tray.show()
                app.exec()
                instance_lock.release()
            else:
                logger.error("无法获取单实例锁")
    else:
        main = UI()
        main.show()
        app.exec()
        
        main.deleteLater()
