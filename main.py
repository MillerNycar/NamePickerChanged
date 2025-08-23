import os.path
import sys
import random
import json
import pandas as pd
import tempfile
import logging
import traceback
import socket
import threading

if os.path.exists("DEBUG"):
    logging.basicConfig(filename='log.log',encoding="UTF-8",level=logging.DEBUG,filemode='w')
elif os.path.exists("IDE"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(filename='log.log', encoding="UTF-8", level=logging.INFO, filemode='w')
temp_dir = tempfile.gettempdir()
VERSION = "1.1.0rel"
VER_NO = 5
CODENAME = "Firefly"

logging.info("⌈飞萤扑火，向死而生⌋")

class NamePickerCore:
    def __init__(self):
        self.allowRepeat = False
        self.SupportCW = False
        self.pickNames = 1
        self.sexPref = "男女都抽"
        self.numPref = "单双都抽"
        self.names = []
        self.chosen = []
        self.length = 0
        self.sexlen = [0,0,0]
        self.sexl = [[],[],[]]
        self.numlen = [0,0]
        self.numl = [[],[]]
        self.api_host = "127.0.0.1"
        self.api_port = 32763
        
        self.loadcfg()
        self.loadname()

    def pick(self):
        if self.sexPref != "男女都抽":
            if self.sexPref == "只抽男":
                le = self.sexlen[0]
                tar = self.sexl[0]
            elif self.sexPref == "只抽女":
                le = self.sexlen[1]
                tar = self.sexl[1]
            else:
                le = self.sexlen[2]
                tar = self.sexl[2]
        else:
            le = self.length
            tar = self.names[0]

        if self.numPref != "单双都抽":
            if self.numPref == "只抽双数":
                tar = list(set(tar)&set(self.numl[0]))
                le = len(tar)
            else:
                tar = list(set(tar) & set(self.numl[1]))
                le = len(tar)
                
        if le != 0:
            chs = random.randint(0, le - 1)
            if not self.allowRepeat:
                if len(self.chosen) >= le:
                    self.chosen = []
                    chs = random.randint(0, le-1)
                else:
                    while chs in self.chosen:
                        chs = random.randint(0, le-1)
                self.chosen.append(chs)
                logging.debug(self.chosen)
            logging.info("抽选完成")
            return [tar[chs], self.names[2][self.names[0].index(tar[chs])]]
        else:
            logging.warning("没有符合筛选条件的学生")
            return ["尚未抽选", "尚未抽选"]

    def pick_and_respond(self):
        """执行抽选并处理联动"""
        results = []
        for i in range(self.pickNames):
            res = self.pick()
            results.append(res)
            
        if self.SupportCW:
            rese = []
            for i in results:
                rese.append("%s（%s）" % (i[0], i[1]))
            try:
                with open("%s\\unread" % temp_dir, "w", encoding="utf-8") as f:
                    f.write("111")
                with open("%s\\res.txt" % temp_dir, "w", encoding="utf-8") as f:
                    f.write("，".join(rese))
                logging.info("CW联动文件已更新")
            except Exception as e:
                logging.error(f"写入CW联动文件时出错: {str(e)}")
                
        return results

    def loadname(self):
        try:
            name_df = pd.read_csv("names.csv", sep=",", header=0, dtype={'name': str, 'sex': int, "no": int})
            name_dict = name_df.to_dict()
            self.names.append(list(name_dict["name"].values()))
            self.names.append(list(name_dict["sex"].values()))
            self.names.append(list(name_dict["no"].values()))
            self.length = len(name_dict["name"])
            self.sexlen[0] = self.names[1].count(0)
            self.sexlen[1] = self.names[1].count(1)
            self.sexlen[2] = self.names[1].count(2)
            
            for i in self.names[0]:
                if self.names[1][self.names[0].index(i)] == 0:
                    self.sexl[0].append(i)
                elif self.names[1][self.names[0].index(i)] == 1:
                    self.sexl[1].append(i)
                else:
                    self.sexl[2].append(i)

            for i in self.names[0]:
                if self.names[2][self.names[0].index(i)] % 2 == 0:
                    self.numl[0].append(i)
                else:
                    self.numl[1].append(i)
                    
            self.numlen[0] = len(self.numl[0])
            self.numlen[1] = len(self.numl[1])
            logging.info("名单导入完成")
        except FileNotFoundError:
            with open("names.csv", "w", encoding="utf-8") as f:
                st = ["name,sex,no\n", "example,0,1"]
                f.writelines(st)
            logging.error("names.csv不存在，已创建样板文件")
            sys.exit(1)

    def loadcfg(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                
            self.allowRepeat = config.get("allowRepeat", False)
            self.SupportCW = config.get("SupportCW", False)
            self.pickNames = config.get("pickNames", 1)
            self.sexPref = config.get("sexPref", "男女都抽")
            self.numPref = config.get("numPref", "单双都抽")
            self.api_host = config.get("api_host", "127.0.0.1")
            self.api_port = config.get("api_port", 32763)
            
            if config.get("VER_NO", 0) < VER_NO:
                logging.warning("当前配置文件版本较低，可能会出现一些问题")
            elif config.get("VER_NO", 0) > VER_NO:
                logging.warning("当前配置文件版本较高，可能会出现一些问题")
                
        except FileNotFoundError:
            cfg = {
                "VERSION": VERSION,
                "VER_NO": VER_NO,
                "CODENAME": CODENAME,
                "allowRepeat": False,
                "SupportCW": False,
                "pickNames": 1,
                "sexPref": "男女都抽",
                "numPref": "单双都抽",
                "api_host": "127.0.0.1",
                "api_port": 32763
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
            logging.warning("没有找到config.json，已创建默认配置")

class TCPServer:
    def __init__(self, host, port, name_picker):
        self.host = host
        self.port = port
        self.name_picker = name_picker
        self.socket = None
        self.running = False
        
    def start(self):
        """启动TCP服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logging.info(f"TCP服务器已启动，监听 {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    logging.info(f"接收到来自 {addr} 的连接")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        logging.error(f"接受连接时出错: {str(e)}")
                    
        except Exception as e:
            logging.error(f"启动TCP服务器时出错: {str(e)}")
            self.stop()
            
    def handle_client(self, client_socket, addr):
        """处理客户端连接"""
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            logging.info(f"接收到数据: {data}")
            
            if data == "[kscx4cw]":
                results = self.name_picker.pick_and_respond()
                
                response = {
                    "status": "success",
                    "results": results,
                    "supportCW": self.name_picker.SupportCW
                }
                
                client_socket.send(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                logging.info("已发送抽选结果响应")
            else:
                response = {
                    "status": "error",
                    "message": "未知命令"
                }
                client_socket.send(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            logging.error(f"处理客户端 {addr} 时出错: {str(e)}")
            try:
                error_response = {
                    "status": "error",
                    "message": str(e)
                }
                client_socket.send(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
            
    def stop(self):
        """停止TCP服务器"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        logging.info("TCP服务器已停止")

def main():
    """主函数"""
    name_picker = NamePickerCore()
    
    server = TCPServer(name_picker.api_host, name_picker.api_port, name_picker)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logging.info("接收到中断信号，正在停止服务器...")
    except Exception as e:
        logging.error(f"服务器运行出错: {str(e)}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
