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
from PySide6.QtCore import QObject,Slot,Property,Signal,QPoint,Qt,QThread,QWaitCondition,QMutex,QMutexLocker
from PySide6.QtWidgets import QApplication,QSystemTrayIcon, QMenu, QWidget
from PySide6.QtGui import QIcon,QGuiApplication, QPixmap, QPainter
from RinUI import RinUIWindow
import network
if os.name == 'nt':
    from win32com.client import Dispatch

# 作为主力开发者，我只需要夹带致死量私货就行了
# 但是别的贡献者和Pylint要考虑的可就多了

temp_dir = tempfile.gettempdir()
err_info = ""
err_dialog = ""
VERSION = "v2.2.0 For Shiru"
CODENAME = "Fugue"
VER_NO = 8
APIVER = 2
SEXFAVOR_ALL = NUMFAVOR_BOTH = -1
SEXFAVOR_BOY = NUMFAVOR_1 = 0
SEXFAVOR_GIRL = NUMFAVOR_2 = 1

# 为了让logger正常工作制造的stderr
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

def get_writable_temp_dir():
    temp_dir = tempfile.gettempdir()
    try:
        test_file = os.path.join(temp_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return temp_dir
    except (IOError, OSError):
        # 如果没有写入权限，使用当前目录
        return os.path.abspath('.')

# 使用可写的临时目录
temp_dir = get_writable_temp_dir()
logger.info(f"使用临时目录: {temp_dir}")

# NamePicker核心
class Choose:
    def __init__(self,path:str):
        self.names = []
        self.namel = []
        self.sex = [[],[],[]]
        self.num = [[],[],[]]
        self.chosen = []
        self.sexFavor = SEXFAVOR_ALL
        self.numFavor = NUMFAVOR_BOTH
        self.load_names(path)
        self.load_favor()

    def load_names(self,path:str) -> None:
        try:
            self.names = []
            self.namel = []
            with open(path,"r",encoding="utf-8") as f:
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
            self.load_favor()
        except (UnicodeDecodeError,IndexError):
            logger.warning("名单文件无效")
            os.remove(path)
            if not os.path.exists("names"):
                os.makedirs("names")
            with open(path,"w",encoding="utf-8") as f:
                f.write("name,sex,no\n某人,0,1")
        except FileNotFoundError:
            logger.warning("没有找到指定文件")
            if not os.path.exists("names"):
                os.makedirs("names")
            with open(path,"w",encoding="utf-8") as f:
                f.write("name,sex,no\n某人,0,1")

    def load_favor(self) -> None:
        logger.debug("loadFavor")
        self.namel = []

            
        for i in range(len(self.names)):
                
            sex_ok = (self.sexFavor == SEXFAVOR_ALL) or (int(self.names[i]["sex"]) == self.sexFavor)

            num_ok = (self.numFavor == NUMFAVOR_BOTH) or \
                     (self.numFavor == NUMFAVOR_1 and int(self.names[i]["no"]) % 2 == 1) or \
                     (self.numFavor == NUMFAVOR_2 and int(self.names[i]["no"]) % 2 == 0)
            
            if sex_ok and num_ok:
                self.namel.append(i)

    def set_sex_favor(self,target:int) -> None:
        self.sexFavor = target
        self.load_favor()

    def set_num_favor(self,target:int) -> None:
        self.numFavor = target
        self.load_favor()

    def pick(self,num:int=1) -> list:
        resi = []
        res = []
        for i in range(num):
            if not cfg.get("General","allowRepeat") and not self.namel==[]:
                ans = random.choice(self.namel)
                resi.append(self.namel[self.namel.index(ans)])
                del self.namel[self.namel.index(ans)]
                logger.debug(self.namel)
                continue
            elif not cfg.get("General","allowRepeat") and self.namel==[]:
                self.load_favor()
                ans = random.choice(self.namel)
            else:
                ans = random.choice(self.namel)
            resi.append(self.namel[self.namel.index(ans)])

        for i in resi:
            res.append(self.names[i])
        if res != []:
            return res
        else:
            return ["bydcnm"] # 做个文明开发者

def set_startup() -> None:
    if os.name != 'nt':
        return
    file_path=f'{os.path.dirname(os.path.abspath(__file__))}/main.exe'
    icon_path = 'assets/favicon.ico'
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    name = os.path.splitext(os.path.basename(file_path))[0]  # 使用文件名作为快捷方式名称
    shortcut_path = os.path.join(startup_folder, f'{name}.lnk')
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = file_path
    shortcut.WorkingDirectory = os.path.dirname(file_path)
    shortcut.IconLocation = icon_path  # 设置图标路径
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

# 简陋的配置管理类
class Config:
    def __init__(self,filename:str,rules:dict,default:dict):
        self.filename = filename
        try:
            with open(filename,"r",encoding="utf-8") as f:
                self.cfgf = f.read()
                self.cfg = json.loads(self.cfgf)
            for i in list(rules.keys()):
                if i not in self.cfg.keys():
                    self.cfg[i] = default[i]
                    continue
                for j in list(rules[i].keys()):
                    if j not in rules[i].keys():
                        self.cfg[i][j] = default[i][j]
                    elif j not in self.cfg[i].keys():
                        self.cfg[i][j] = default[i][j]
                    elif not self.val(i,j,self.cfg[i][j],rules):
                        self.cfg[i][j] = default[i][j]
        except FileNotFoundError:
            logger.warning("未找到配置文件，将创建默认配置")
            with open(filename,"w",encoding="utf-8") as f:
                f.write(json.dumps(default))
            self.cfg = default
        except json.JSONDecodeError:
            logger.warning("无效的配置文件")
            with open(filename,"w",encoding="utf-8") as f:
                f.write(json.dumps(default))
            self.cfg = default

    def val(self,i:str,j:str,chk:any,rules:dict) -> bool:
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

    def get(self,cls:str,key:str) -> any:
        return self.cfg[cls][key]
    
    def set(self,cls:str,key:str,val) -> None:
        self.cfg[cls][key] = val
        with open(self.filename,"w",encoding="utf-8") as f:
            f.write(json.dumps(self.cfg))

# Huanyu子项没有任何作用，但是我就是懒得删
CFGRULE = {
    "General": {"allowRepeat": bool,"autoStartup": bool,"chooseKey": str,"supportCS": bool,"floatingPos":str,"autoCheck":bool,"cameraAppPath":str,"cameraAppArgs":str},
    "Secure": {"lock":bool,"password":str,"require2FA":bool,"2FAMethod":str,"OTPnote":str},
    "Version": {"apiver": ["range",2,2],"channel":["option","rel","dev"]},
    "Huanyu": {"ecoMode": bool,"justice": bool},
    "Debug": {"logLevel": ["option","DEBUG","INFO","WARNING","ERROR"]}
}

CFGDEFAULT = {
    "General": {"allowRepeat": False,"autoStartup": False,"chooseKey": "ctrl+w","supportCS": False,"floatingPos":"auto","autoCheck":False,"cameraAppPath":"","cameraAppArgs":""},
    "Secure": {"lock":False,"password":"","require2FA":False,"2FAMethod":"otp","OTPnote":""},
    "Version": {"apiver": 2,"channel":"rel"},
    "Huanyu": {"ecoMode": False,"justice": False},
    "Debug": {"logLevel": "INFO"}
}

# 初始化一堆意义不明的变量
cfg = Config("config.json",CFGRULE,CFGDEFAULT)
force = False
if os.path.exists("out.log"):
    os.remove("out.log")
logger.add("out.log")
logger.add(sys.stderr, level=cfg.get("Debug","logLevel"))
logger.info(f"NamePicker {VERSION} - Codename {CODENAME} (Inside version {VER_NO},Plugin API Version {APIVER})")
logger.info("「历经生死、重获新生的忘归人，何时才能返乡？⌋")
# 信我，我真没夹带私货
# 我萤伟大，无需多言
try:
    core = Choose(f"names/{os.listdir('names')[0]}")
except FileNotFoundError:
    logger.warning("没有找到指定文件")
    if not os.path.exists("names"):
        os.makedirs("names")
    with open("names/names.csv","w",encoding="utf-8") as f:
        f.write("name,sex,no\n某人,0,1")
verified = False
mac = mac_addr()
secret_key = base64.b32encode(mac.encode(encoding="utf-8"))
totp = pyotp.TOTP(secret_key)
a = cfg.get("Secure","2FAMethod").split(",")
if a != [""]:
    methods = cfg.get("Secure","2FAMethod").split(",")
else:
    methods = []
totp_url = totp.provisioning_uri(f"NamePicker - {cfg.get('Secure','OTPnote')}", issuer_name="NamePicker 2FA")
x = 0
y = 0
ver = ""

class UI(RinUIWindow):
    def __init__(self):
        super().__init__(resource_path("pages/main.qml"))
        self.bridge = Bridge()
        self.engine.rootContext().setContextProperty("Bridge", self.bridge)

# 瞎jb命名重灾区，你猜我pylint怎么干到3/10的
# 和qml通信，也算一种code behind?
class Bridge(QObject):
    chgVer = Signal(str)
    chgProg = Signal(int)
    chgPhase = Signal(str)
    showMessageSignal = Signal(str, str, str)
    cameraResult = Signal(bool, str)  # 添加 cameraResult 信号

    @Slot(str,result=list)
    def Pick(self,num:str) -> list:
        num_int = int(num)
        r = core.pick(num_int)
        re = []
        if r == ["bydcnm"]:
            return r
        else:
            support_cs = cfg.get("General","supportCS")
            if num_int > 3 and support_cs:
                for i in r:
                    re.append(f"{i['name']}({i['no']})")
                re.append("数量超出限制联动失败")
            elif num_int <= 3 and support_cs:
                for i in r:
                    re.append(f"{i['name']}({i['no']})")
                with open(f"{temp_dir}/res.txt","w",encoding="utf-8") as f:
                    f.write(",".join(re))
                with open(f"{temp_dir}/unread","w") as f:
                    f.write("1")
            else:
                for i in r:
                    re.append(f"{i['name']}({i['no']})")
            return re
        
    @Slot(str,str,result=list)
    def GetCfg(self,cls:str,key:str) -> list:
        try:
            return [cfg.get(cls,key)]
        except KeyError:
            # 如果配置项不存在，返回默认值
            if cls in CFGDEFAULT and key in CFGDEFAULT[cls]:
                return [CFGDEFAULT[cls][key]]
            return [""]
    
    @Slot(result=int)
    def GetNLen(self) -> int:
        return len(core.names)
    
    @Slot(str,str,list)
    def SetCfg(self,cls:str,key:str,val:list) -> list:
        cfg.set(cls,key,val[0])

    @Slot(int,result=int)
    def GetDbg(self,cls:int) -> int:
        return ["DEBUG","INFO","WARNING","ERROR"].index(cfg.get("Debug","logLevel"))

    @Slot(bool)
    def Startup(self,stat:bool) -> None:
        if stat:
            set_startup()
        else:
            remove_startup()

    @Slot(str,result=bool)
    def VerifyPassword(self,password:str) -> bool:
        return hashlib.md5(password.encode(encoding='UTF-8')).hexdigest() == cfg.get("Secure","password")
    
    @Slot(bool,result=bool)
    def setVerified(self,vl:bool) -> None:
        global verified
        logger.debug("setVerified")
        verified = vl

    @Slot(result=bool)
    def getVerified(self) -> bool:
        global verified
        if verified:
            return True
        else:
            return not cfg.get("Secure","lock")
    
    @Slot(str,result=bool)
    def VerifyFile(self,path:str) -> bool:
        pass

    @Slot(str)
    def setPassword(self,password:str) -> None:
        cfg.set("Secure","password",hashlib.md5(password.encode(encoding='UTF-8')).hexdigest())

    @Slot(str,result=bool)
    def VerifyOTP(self,code:str) -> bool:
        global totp
        return totp.verify(code)
        
    @Slot(int,result=int)
    def Get2FA(self,cls:int) -> int:
        return ["otp"].index(cfg.get("Secure","2FAMethod"))
    
    @Property(str)
    def GetOTPSecret(self) -> str:
        logger.debug("GetOTPSecret")
        global secret_key
        return secret_key
    
    @Slot(str)
    def GenTOTPImg(self,note:str) -> None:
        global totp,totp_url
        logger.debug("TOTP Image")
        cfg.set("Secure","OTPnote",note)
        totp_url = totp.provisioning_uri(f"NamePicker/{note}", issuer_name="NamePicker 2FA")
        qr = qrcode.make(totp_url)
        qr.save("qr.png")

    @Slot(bool)
    def chgStartup(self,stat:bool) -> None:
        cfg.set("General","autoStartup",stat)
        if stat:
            set_startup()
        else:
            remove_startup()

    @Property(str)
    def VerTxt(self) -> str:
        return f"当前版本：{VERSION}"

    @Slot(str)
    def setSexFavor(self,sexf:str) -> None:
        sex_map = {"全部抽选": SEXFAVOR_ALL, "只抽男生": SEXFAVOR_BOY, "只抽女生": SEXFAVOR_GIRL}
        if sexf in sex_map:
            core.set_sex_favor(sex_map[sexf])
        else:
            logger.warning(f"未知的性别偏好选项: {sexf}")

    @Slot(str)
    def setNumFavor(self,numf:str) -> None:
        num_map = {"全部抽选": NUMFAVOR_BOTH, "只抽单数": NUMFAVOR_1, "只抽双数": NUMFAVOR_2}
        if numf in num_map:
            core.set_num_favor(num_map[numf])
        else:
            logger.warning(f"未知的学号偏好选项: {numf}")
    
    @Slot(result=list)
    def getNameList(self) -> list:
        return os.listdir("names")
    
    @Slot(int)
    def changeNameList(self,path:int) -> None:
        logger.debug(f"names/{os.listdir('names')[path]}")
        core.load_names(f"names/{os.listdir('names')[path]}")

    @Property(int)
    def getDwn(self) -> int:
        return 0
    
    @Property(str)
    def getStat(self) -> str:
        return 1
    
    @Slot()
    def checkNew(self) -> str:
        global force
        th = network.Version()
        th.versionChange.connect(self.emitCg)
        th.local = VER_NO
        th.channel = cfg.get("Version","channel")
        th.force = force
        th.start()
        # return self.ver
        
    def emitCg(self,s):
        global ver
        logger.debug(s)
        ver = s
        self.chgVer.emit(s)

    # @Property(str)
    # def getVer(self):
    #     global ver
    #     logger.debug(ver)
    #     return ver
        
    
    @Slot(bool)
    def setForce(self,b:bool):
        global force
        force = b

    @Slot(result=bool)
    def getForce(self):
        global force
        return force

    def emitProg(self,s):
        self.chgProg.emit(s)

    def emitPhase(self,s):
        self.chgPhase.emit(s)

    @Slot(str)
    def add2FA(self,s:str):
        global methods
        t = set(methods)
        t.add(s)
        methods = list(t)
        cfg.set("Secure","2FAMethod",",".join(methods))

    @Slot(str)
    def rem2FA(self,s:str):
        global methods
        t = set(methods)
        t.remove(s)
        methods = list(t)
        cfg.set("Secure","2FAMethod",",".join(methods))

    @Property(list)
    def get2FA(self):
        global methods
        readable = []
        for i in range(len(methods)):
            if methods[i] == "otp":
                readable.append("2FA APP")
        return [methods,readable]
    
    @Slot(str,result=bool)
    def have2FA(self,s:str):
        global methods
        return s in methods
    
    @Slot(str, str, str)
    def showMessage(self, severity: str, title: str, message: str) -> None:
        """显示提示信息"""
        self.showMessageSignal.emit(severity, title, message)
        logger.info(f"{severity}: {title} - {message}")
    
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
    
    @Slot()
    def error(self):
        raise Exception("喵")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/favicon.ico")))
    
    main_window = UI()
    main_window.show()
    
    app.setQuitOnLastWindowClosed(True)
    
    app.exec()
