from Tkinter import *
from ttk import *
import socket
import struct
import os
import pickle
import threading
import SocketServer
import md5
import base64   


BAK_PATH = r'C:\Users\kashing\Desktop\ServerBackUp'

def getmd5(filename):  
    file_txt = open(filename,'rb').read()  
    m = md5.new(file_txt)  
    return m.hexdigest()
      
def dedup():  
 
    path = BAK_PATH  
    all_md5 = {}  
    all_size = {}  
    total_file=0 
    total_delete=0 
  
    for file in os.listdir(path):  
        total_file += 1  
        real_path=os.path.join(path,file)  
        if os.path.isfile(real_path) == True:  
            size = os.stat(real_path).st_size  
            name_and_md5=[real_path,'']  
            if size in all_size.keys():  
                new_md5 = getmd5(real_path)  
                if all_size[size][1]=='':  
                    all_size[size][1]=getmd5(all_size[size][0])  
                if new_md5 in all_size[size]:  
                    print 'Delete',file
                    os.remove(real_path)
                    f=open(os.path.join(path,'log'),'a+')
                    f.write(real_path+" "+all_size[size][0]+'\n')
                    f.close()    
                    total_delete += 1 
                else:  
                    all_size[size].append(new_md5)  
            else:  
                all_size[size]=name_and_md5  

    print 'Total Files : ',total_file  
    print 'Deteled File : ',total_delete  


def recv_unit_data(clnt,infos_len):
    data = b''
    if 0 < infos_len <= 1024:
        data += clnt.recv(infos_len)
    else:
        while True:
            if infos_len > 1024:
                data += clnt.recv(1024)
                infos_len -= 1024
            else:
                data += clnt.recv(infos_len)
                break
    return data

def get_files_info(clnt):
    fmt_str = 'Q?'
    headsize = struct.calcsize(fmt_str)
    data = clnt.recv(headsize)
    infos_len,compress = struct.unpack(fmt_str,data)
    data = recv_unit_data(clnt,infos_len)
    return pickle.loads(data),compress

def mk_path(filepath):
    paths = filepath.split(os.path.sep)[:-1]
    p = BAK_PATH
   
    for path in paths:
        p = os.path.join(p,path)       
        if not os.path.exists(p):
            os.mkdir(p)
        
def get_compress_size(clnt):
    fmt_str = "Q"
    size = struct.calcsize(fmt_str)
    data = clnt.recv(size)
    size = struct.unpack(fmt_str,data)
    return size

def recv_file(clnt,infos_len,filepath,compress):

    mk_path(filepath)
    filepath = os.path.join(BAK_PATH,filepath)
   
    if compress:
        infos_len = get_compress_size(clnt)
        filepath = ''.join([os.path.splitext(filepath)[0],'.tar.gz'])
    f = open(filepath,'wb+')
    try:
        if 0 < infos_len <= 1024:
            data = clnt.recv(infos_len)
            f.write(base64.encodestring(data))
        else:
            while True:
                if infos_len > 1024:
                    data = clnt.recv(1024)
                    f.write(base64.encodestring(data))
                    infos_len -= 1024
                else:
                    data = clnt.recv(infos_len)
                    f.write(base64.encodestring(data))
                    break
    except:
        print('error')
    else:
        return True
    finally:
        f.close()

def send_echo(clnt,res):
    if res:
        clnt.sendall(b'success')
    else:
        clnt.sendall(b'failure')

def client_operate(client):
    files_lst,compress = get_files_info(client)
    for size,filepath in files_lst:
        res = recv_file(client,size,filepath,compress)
        send_echo(client,res)
    client.close()

class BakHdl(SocketServer.StreamRequestHandler):
    def handle(self):
        client_operate(self.request)

def start(host,port):
    server = SocketServer.ThreadingTCPServer((host,port),BakHdl)
    s = threading.Thread(target=server.serve_forever)
    s.start()
    return server

class MyFrame(Frame):

    def __init__(self,root):
        Frame.__init__(self, root)
        self.root = root
        self.server = None
        self.grid()
        self.local_ip = '127.0.0.1'
        self.serv_ports = [10888,20888,30888,89]
        self.init_components()

    def init_components(self):
        proj_name = Label(self,text="Remote Backup Server")
        proj_name.grid(columnspan=3)

        serv_ip_label = Label(self,text="Service Address: ")
        serv_ip_label.grid(row=1)

        self.serv_ip = Combobox(self,values=self.get_ipaddr())
        self.serv_ip.set(self.local_ip)
        self.serv_ip.grid(row=1,column=2)

        serv_port_label = Label(self,text="Service Port: ")
        serv_port_label.grid(row=2)

        self.serv_port = Combobox(self,values=self.serv_ports)
        self.serv_port.set(self.serv_ports[0])
        self.serv_port.grid(row=2,column=2)

        self.start_serv_btn = Button(self,text="START",command=self.start_serv)
        self.start_serv_btn.grid(row=3)

        self.start_exit_btn = Button(self,text="STOP",command=self.exit)
        self.start_exit_btn.grid(row=3,column=1)

        self.start_dedup_btn = Button(self,text="DEDUP",command=dedup)
        self.start_dedup_btn.grid(row=3,column=2)

    def exit(self):
        if self.server:
            threading.Thread(target=self.server.shutdown()).start()
        self.root.destroy()

    def get_ipaddr(self):
        host_name = socket.gethostname()
        info = socket.gethostbyname_ex(host_name)
        info = info[2]
        info.append(self.local_ip)
        return info

    def start_serv(self):
        if not os.path.exists(BAK_PATH):
            os.mkdir(BAK_PATH)           
        print(self.serv_ip.get(),self.serv_port.get())
        host = self.serv_ip.get()
        port = int(self.serv_port.get())
        self.server = start(host,port)
        self.start_serv_btn.state(['disabled',])
        self.serv_ip.state(['disabled',])
        self.serv_port.state(['disabled',])


if __name__ == '__main__':
    root = Tk()
    root.title('Backup Server')
    root.resizable(False,False)
    app = MyFrame(root)
    app.mainloop()

