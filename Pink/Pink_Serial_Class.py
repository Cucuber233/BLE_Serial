import math
import serial     
from PIL import Image 
import binascii
import threading            
import serial.tools.list_ports  
import tkinter as tk
##from tkinter.constants import (HORIZONTAL, VERTICAL, RIGHT, LEFT, X, Y, BOTH, BOTTOM, YES, NONE, END, CURRENT)
import tkinter.messagebox

STRGLO = ""    #读取的数据缓冲区
total_Num = 0    #总包
current_Num = 0  #当前包
############################__ImageDispose__##########################################
'''
@brief  图片数据解析
@param  path
''' 
class ImageDispose:
    def __init__(self, path):
        self.image = Image.open(path)
        self.imagePath = path
        self.image_width = self.image.size[0]
        self.image_height = self.image.size[1]
        self.Range = self.image_height * self.image_width
        self.Size = self.Range//8
        self.image_data = []  #图片RGB数据
        self.image_red_bit = []
        self.image_white_bit = []
        self.Line = 0
        self.Column = self.image.size[0] - 1
        self.red_byte = []    #红色图层数据
        self.white_byte = []  #白色图层数据
        self.ImageRGB()
        self.ImageBit()
        self.ImageByte()
        
    def ImageRGB(self):          
        for i in range(self.Range):
            if  self.Column < 0:
                self.Line += 1
                self.Column = self.image_width - 1
            self.image_data.append(self.image.getpixel((self.Column, self.Line)))
            self.Column -= 1

    def ImageBit(self):        
        for i in range(self.Range):
            #绿色
            if self.image_data[i][0] == 0 and self.image_data[i][1] > 100 and self.image_data[i][2] == 0:
                self.image_red_bit.append(1)
                self.image_white_bit.append(1)
                continue
                            
            #红图层
            if self.image_data[i][0] >= 50 and self.image_data[i][1] <= 20 and self.image_data[i][2] <= 20:
                self.image_red_bit.append(1)
                self.image_white_bit.append(0)
                continue

            else:
                self.image_red_bit.append(0)

            #白图层
            if self.image_data[i][0] > 50 and self.image_data[i][1] > 50 and self.image_data[i][2] > 50:
                self.image_white_bit.append(1)
            else:
                self.image_white_bit.append(0)

    def ImageByte(self):
        global total_Num
        global current_Num
##        total_Num = self.Range//8//200  #一个图层的包数,共有两图层
        total_Num = math.ceil(self.Range//8/200)   #一个图层的包数,共有两图层
##        if self.Range//8/200 > self.Range//8//200:
##            total_Num = self.Range//8//200 + 1
##        else:
##            total_Num = self.Range//8/200
            
        current_Num = 1                 #当前包
        for i in range(self.Range):
            if (i+1) % 8 == 0:
                cur_red_byte = 0
                cur_white_byte = 0
                for j in range(7,-1,-1):
                    if self.image_red_bit[i - j] == 1:
                        cur_red_byte = (cur_red_byte << 1) + 1
                    else:
                        cur_red_byte = cur_red_byte << 1

                    if self.image_white_bit[i - j] == 1:
                        cur_white_byte = (cur_white_byte << 1) + 1
                    else:
                        cur_white_byte = cur_white_byte << 1
                        
                self.red_byte.append(cur_red_byte)
                self.white_byte.append(cur_white_byte)
##        print(len(self.red_byte))
##        print(len(self.white_byte))
#################################################################################               
###第一包       
##first = [
##         #数据头
##         0x57,0x43,
##         #长度
##         0xE8,\
##         #设备类型
##         0x70,\
##         #命令类型
##         0x90,\
##         #长度
##         0xE3,\
##         #指令
##         0x30,\
##         #总包，当前包
##         0x00,total_Num*2,0x00,current_Num,\
##         #MAC地址
####         0xC8,0x2F,0x69,0x69,0x48,0x6D,
##         0xEF,0xCD,0xAB,0x63,0xAA,0xBB,\
##         #seriveUUID, charUUID
##         0x00,0x00,0x00,0x00,\
##         #图片信息
##         0x01,0x10,0x01,0x00,0x00,0x01,0x2C,0x01,0x90,0x01,0x2C,0x01
##         ]
############################__Tkinter__##########################################
class Application():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('TB4A')
        self.root.geometry("370x370+300+300")
        self.root.resizable(False, False) # 窗口大小不可变
##        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file = "C:/Users/13432/Desktop/P/icon.ico"))
        self.root.config(bg = 'bisque')
        self.creatWidget()  #创建组件
        
    def run(self):
        self.root.mainloop()   #窗口事件循环    

    def creatWidget(self):
        #======串口选择项=====
        #创建矩形区域，用于放置其他子组件
        self.frame_port = tk.Frame(self.root)
        self.frame_port.pack(pady = 10)
        self.frame_port.config(bg = 'pink')
        
        tk.Label(self.frame_port,text='串口号:',font=('楷体', 14), bg = 'pink').grid(row=0, column=0, pady = 8)
        self.btn_port_flag = 0     
        options = serial_object.port_list 
        self.serialPort = tk.StringVar()
        self.serialPort.set('串口选择')

        tk.Label(self.frame_port,text='波特率:',font=('楷体', 14), bg = 'pink').grid(row=1, column=0)
        option_BaudRate = [38400, 56000, 57600, 115200]  #波特率列表
        self.serialPort_BaudRate = tk.StringVar()
        self.serialPort_BaudRate.set('波特率选择')
        
        self.drop_down_box = tk.OptionMenu(self.frame_port, self.serialPort, *options)  #串口下拉框
        self.drop_down_box.config(width = 32)  #修改组件参数
        self.drop_down_box.grid(row = 0, column = 1)
        
        self.drop_down_box_BaudRate = tk.OptionMenu(self.frame_port, self.serialPort_BaudRate, *option_BaudRate)   #波特率下拉框
        self.drop_down_box_BaudRate.config(width = 7)  #修改组件参数

        self.drop_down_box_BaudRate.grid(row = 1, column = 1, sticky = 'w')
        
        self.btn_port = tk.Button(self.frame_port, text = "打开串口", command = self.greet, width = 8)
        self.btn_port.grid(row = 2, column = 1, sticky = 'e', pady = 2 ,padx = 2)          

        label01 = tk.Label(self.root, text = "--------------------------------------------------------------", bg = 'bisque')
        label01.pack()
        #图片导入路径
        #创建矩形区域，用于放置其他子组件
        self.frame_image_path = tk.Frame(self.root)
        self.frame_image_path.pack()
        label05 = tk.Label(self.frame_image_path, text = "image_path:", bg = 'bisque')
        label05.grid(row =3, column = 0, sticky = 'e') 
        self.image_path = tk.StringVar()
        self.image_path.set('C:/Users/13432/Desktop/bg_3.jpg')
        self.image_path_input = tk.Entry(self.frame_image_path, textvariable = self.image_path, width = 38)
        self.image_path_input.grid(row = 3, column = 1)
        label0B = tk.Label(self.root, text = "--------------------------------------------------------------", bg = 'bisque')
        label0B.pack()
        #======功能选择项====== 
        label02 = tk.Label(self.root, text = "请选择功能", anchor = 'w', font = ('楷体', 14), fg = 'purple', bg = 'bisque')
        label02.pack()
        
        #创建矩形区域，用于放置其他子组件
        self.frame_primary = tk.Frame(self.root)      
        self.frame_primary.pack()
        self.frame_primary.config(bg = 'bisque')
        
        b01=tk.Button(self.frame_primary, text = '连接指定设备', command = lambda: self.new_window('1'), relief = 'ridge')
        b01.pack(side='left', padx = 2)
        b02 = tk.Button(self.frame_primary, text = '更改图片数据', command = lambda: self.new_window('2'), relief = 'ridge')
        b02.pack(side='right', padx = 2)
        b04 = tk.Button(self.frame_primary, text = '连接指定设备并传输数据', command = lambda: self.new_window('3'), relief = 'ridge')
        b04.pack(side='bottom', pady = 4)
        b03 = tk.Button(self.frame_primary, text = '传输数据', command = lambda: self.new_window('4'), relief = 'ridge')
        b03.pack(side='top', pady = 4)
        b05 = tk.Button(self.frame_primary, text = '二维码数据传输', command = lambda: self.new_window('5'), relief = 'ridge')
        b05.pack(side='top', pady = 4)

        #创建矩形区域，用于放置其他子组件
        self.frame_protocol = tk.Frame(self.root)
        self.frame_protocol.pack()
        self.protocol = tk.StringVar()
        self.r1 = tk.Radiobutton(self.root,text = "旧协议",value = "old", variable = self.protocol) 
        # value值代表该按钮被选中后所返回的值. 
        self.r2 = tk.Radiobutton(self.root,text = "新协议前景",value = "new", variable = self.protocol)
        self.protocol.set("old")
        self.r1.pack(side='left', padx = 2)
        self.r2.pack(side='right', padx = 2)

##        tk.Button(self.root,text = "确定",command = self.confirm).pack(side = "bottom")
##    def confirm(self): 
##        s = self.protocol.get() 
##        if s == "old": 
##            tk.messagebox.showinfo("测试","你选择的是old") 
##        else: 
##            tk.messagebox.showinfo("测试","你选择的是new")

    def new_window(self, window_type):
        self.window_type = window_type
        self.window = tk.Toplevel(self.root)
        self.window.geometry("430x550+700+300")
##        self.window.tk.call('wm', 'iconphoto', self.window, tk.PhotoImage(file = "C:/Users/13432/Desktop/P/icon.ico")) 
        self.window.resizable(False, False)  # 窗口大小不可变

        self.window_type = window_type
        
        if self.window_type == '1':
            self.cmd = 0x90        #命令类型
            self.msgId = 0x10     
            label03 = tk.Label(self.window, text = "连接指定设备", font = ('楷体', 14), fg = 'purple', pady = 10)
            label03.pack()
            
        elif self.window_type == '2':
            self.cmd = 0x90        
            self.msgId = 0x20      
            label03 = tk.Label(self.window, text = "更改图片数据", font = ('楷体', 14), fg = 'purple', pady = 10)
            label03.pack()
            
        elif self.window_type == '3':
            self.cmd = 0x90        
            self.msgId = 0x30      
            label03 = tk.Label(self.window, text = "连接指定设备并传输数据", font = ('楷体', 14), fg = 'purple', pady = 10)
            label03.pack()
            
        elif self.window_type == '4':
            self.cmd = 0x5F      
            label03 = tk.Label(self.window, text = "传输数据", font = ('楷体', 14), fg = 'purple', pady = 10)
            label03.pack()

        elif self.window_type == '5':
            self.cmd = 0x90
            self.msgId = 0x30 
            label03 = tk.Label(self.window, text = "二维码数据传输", font = ('楷体', 14), fg = 'purple', pady = 10)
            label03.pack()
            
        #创建矩形区域，用于放置其他子组件
        self.frame_primary = tk.Frame(self.window)      
        self.frame_primary.pack()
        #MAC地址
        if window_type != '4':
            label04 = tk.Label(self.frame_primary, text = "MAC地址：")
            label04.grid(row = 0, column = 0, sticky = 'e')

            self.mac = tk.StringVar()
##            self.mac.set('EFCDAB63AABB')
            self.mac.set('796D6963AB23')
            self.mac_input = tk.Entry(self.frame_primary, textvariable = self.mac, cursor='mouse')
            self.mac_input.grid(row = 0, column = 1)
        
        #单行输入框: 图片信息
        #图片类型
        if window_type != '1' and window_type != '5':    
            label05 = tk.Label(self.frame_primary, text = "image_type：")
            label05.grid(row = 1, column = 0, sticky = 'e')
            self.image_type = tk.StringVar()
            self.image_type_input = tk.Entry(self.frame_primary, textvariable = self.image_type, cursor = 'mouse')
            self.image_type_input.grid(row = 1, column = 1, pady = 5)
            self.image_type.set('1')
            
        #图片ID
        if window_type != '1' and window_type != '5':
            label06 = tk.Label(self.frame_primary, text = "image_id：")
            label06.grid(row = 2, column = 0, sticky = 'e')
            self.image_Id = tk.StringVar()
            self.image_Id_input = tk.Entry(self.frame_primary, textvariable = self.image_Id, cursor = 'mouse')
            self.image_Id_input.grid(row = 2, column = 1)
            self.image_Id.set('10')

        #图片尺寸
        if window_type != '1' and window_type != '5':
            label07 = tk.Label(self.frame_primary, text = "ScreenSize：")
            label07.grid(row = 3, column = 0, pady = 5)
            self.image_size = tk.StringVar()
            self.image_size_input = tk.Entry(self.frame_primary, textvariable = self.image_size, cursor = 'mouse')
            self.image_size_input.grid(row = 3, column = 1)
            self.image_size.set('1')

        #位置position
        if window_type == '4' or window_type == '3' or window_type == '5':
            #x坐标
            label08 = tk.Label(self.frame_primary, text = 'x：')
            label08.grid(row = 4, column = 0, sticky = 'e')
            self.image_x = tk.StringVar()
            self.image_x_input = tk.Entry(self.frame_primary, textvariable = self.image_x, cursor = 'mouse')
            self.image_x_input.grid(row = 4, column = 1, pady = 5)
            self.image_x.set('0')
            #y坐标
            label09 = tk.Label(self.frame_primary, text = "y：")
            label09.grid(row = 5, column = 0, sticky = 'e')
            self.image_y = tk.StringVar()
            self.image_y_input = tk.Entry(self.frame_primary, textvariable = self.image_y, cursor = 'mouse')
            self.image_y_input.grid(row = 5, column = 1)
            self.image_y.set('300')

        if window_type == '5':
            #二维码放大倍数
            label10 = tk.Label(self.frame_primary, text = "QRcodeSize：")
            label10.grid(row = 6, column = 0, sticky = 'e')
            self.QRcodeSize = tk.StringVar()
            self.image_QRcodeSize_input = tk.Entry(self.frame_primary, textvariable = self.QRcodeSize, cursor = 'mouse')
            self.image_QRcodeSize_input.grid(row = 6, column = 1)

##            #创建矩形区域，用于放置其他子组件
##            self.frame_QRcodetext = tk.Frame(self.window)      
##            self.frame_QRcodetext.pack()
##            label0B = tk.Label(self.window, text = 'QRcodeStr：' , font = ('楷体',12), fg = 'coral')
##            label0B.grid(row = 0, column = 0)
##            self.text0 = tk.Text(self.frame_QRcodetext, width = 30, height = 3, bg="pink", fg = "teal", font = ('楷体', 12))
##            self.text0.grid(row = 0, column = 1)
##            label0B = tk.Label(self.window, text = 'QRcode：' , font = ('楷体',12), fg = 'coral')
##            label0B.pack(pady = 5, anchor = 'w')
            self.QRcodetext = tk.Text(self.window, width = 50, height = 4, bg = "pink", fg = "teal", font = ('楷体', 12))
            app.QRcodetext.insert('end', "https://demo.openiots.com:39331/epo-web/pda/rtchelp/position/digest\\t50ebd5500ffe4c7a\\t50ebd5500ffe4c7a50ebd5500ffe4c7a\\t12960\\t")  ##状态返回
            self.QRcodetext.pack(padx = 3, anchor = 'w')

        label0A = tk.Label(self.window, text = '状态返回：' , font = ('楷体',15), fg = 'coral')
        label0A.pack(pady = 5, anchor = 'w')


        #创建矩形区域，用于放置其他子组件
        self.frame_text = tk.Frame(self.window)      
        self.frame_text.pack()
        ##多行输入框
        self.text = tk.Text(self.frame_text, width = 50, height = 15, bg="pink",fg = "teal", font = ('楷体', 12))    
        self.scroll = tk.Scrollbar(self.frame_text)       ##滚动条
        # 放到窗口的右侧, 填充Y竖直方向
        self.scroll.pack(side = tk.RIGHT, fill = tk.Y)
        self.text.pack()
        # 两个控件关联
        self.scroll.config(command = self.text.yview)
        self.text.config(yscrollcommand = self.scroll.set)

        b04 = tk.Button(self.window, text = '确定', command = self.processing_data, relief = 'flat', fg = 'brown', bg = 'yellow', width = 8, font = ('楷体', 13))
        b04.pack(side='top', pady = 15)

    def processing_data(self):
        global total_Num, current_Num
        global image_object

        
        
        x = [int(self.image_x.get())//256, int(self.image_x.get())%256]
        y = [int(self.image_y.get())//256, int(self.image_y.get())%256]
        
        mac_str = ''
        mac = []
        for i in range(1, len(self.mac.get())+1):
            mac_str += self.mac.get()[i-1]
            if i % 2 == 0:
                mac.append(int(mac_str.encode(), 16))
                mac_str = ''
                
        if int(self.image_type.get().encode(), 16) == 9 or int(self.image_type.get().encode(), 16) == 10 or int(self.image_type.get().encode(), 16) == 6 or int(self.image_type.get().encode(), 16) == 3:
            total_Num = 0.5
            current_Num = 1
        else:
            try:
                image_object = ImageDispose(self.image_path.get())      ##图片导入
            except Exception as e:
                tk.messagebox.showinfo('image', "---image异常---" + str(e))
                print("---image异常---", e)
                return

        
        if self.window_type == '5':
            QRcodeString = self.QRcodetext.get("1.0","end")
            first_QRcode = [
                             #数据头
                             0x57,0x43,
                             #长度
                             0x20+len(QRcodeString),\
                             #设备类型
                             0x70,\
                             #命令类型
                             self.cmd,\
                             #长度
                             0x1B+len(QRcodeString),\
                             #指令
                             self.msgId,\
                             #总包      当前包
                             0x00,0x01, 0x00,0x01] + \
                             mac + \
                             [0x00,0x00,0x00,0x00, \
                             #图片信息        x    y   倍数
                             0x03,0x10,0x01] + x + y + [int(self.QRcodeSize.get()), 0x90,0x01,0x2C,0x01]
            first_QRcode_data = first_QRcode + [ord(i) for i in QRcodeString] + [0x00, 0xAA]
##            print(first_QRcode_data)
            count = serial_object.DWritePort(first_QRcode_data)
            print("写入字节数：", count)
            return 

        image_width = [int(image_object.image_width)//256,int(image_object.image_width)%256]
        image_height = [int(image_object.image_height)//256,int(image_object.image_height)%256]
    
        self._image_size_ = int(self.image_size.get())
    
        image_Inf = [
                #图片类型
                int(self.image_type.get().encode(), 16),
                #图片ID
                int(self.image_Id.get().encode(), 16),
                #图片尺寸编号      x坐标   y坐标  图片宽度      图片高度       颜色图层
                self._image_size_] + x    +  y +    image_width + image_height + [0x01]

        #第一包       
        self.first_data = [   #数据头
                         0x57,0x43,
                         #长度
                         0xE8,\
                         #设备类型
                         0x70,\
                         #命令类型
                         self.cmd,\
                         #长度
                         0xE3,\
                         #指令
                         self.msgId,\
                         #总包，当前包                         #MAC地址  #seriveUUID, charUUID      #图片信息
                         0x00,int(total_Num*2),0x00,current_Num ] + mac   +   [0x00, 0x00, 0x00, 0x00] + image_Inf
        
##        print(self.first_data)
        if(serial_object.ret == True):  #判断串口是否成功打开
            if self.protocol.get() == "new" and int(self.image_type.get().encode(), 16) == 0x02:
                total = image_object.Range//8/200       #一个图层的包数,共有两图层
                total_Num = int(total)
                first_data = self.first_data + image_object.red_byte[:100] + image_object.white_byte[:100] + [0x00, 0xAA]
                count = serial_object.DWritePort(first_data)
                print("写入字节数：", count)
            else:
                first_data = self.first_data + image_object.red_byte[:200] + [0x00, 0xAA]
                count = serial_object.DWritePort(first_data)
                print("写入字节数：", count)
 
    def greet(self):
        if self.btn_port_flag == 0:
            self.btn_port.config(text = "关闭串口")
            self.btn_port_flag = 1
            serial_object.DOpenPort()    #打开串口
##            print(self.serialPort.get()[:5])
            
        else:
            self.btn_port.config(text = "打开串口")
            self.btn_port_flag = 0
            if  serial_object.ret == True:
                serial_object.DClosePort()    #关闭串口
##            print(self.serialPort.get()[:5])
        
###################################################################################################################### 
############################__Serial__################################################################################
'''
@brief  串口各功能
@param  Port, BaudRate,OutTime
'''
# 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
# 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
# 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
class Serial:
    def __init__(self):
        self.portx = 0      #串口号
        self.bps = 0        #波特率
        self.timeout = 0    #超时时间
        self.port_list = 0  #当前串口个数元组
        self.ser = 0        #串口对象
        self.ret = 0        #串口开关状态
        self.DFindPort()    #查找串口
        
    def DFindPort(self):
        self.port_list = list(serial.tools.list_ports.comports())    ##获取串口对象元组
        if len(self.port_list) == 0:
            print('无可用串口')
        else:
            for i in range(len(self.port_list)):
                print(self.port_list[i])
                
    #打开串口
    def DOpenPort(self):
        self.portx = app.serialPort.get()[:5]         #串口号
        self.bps = app.serialPort_BaudRate.get()  #波特率
        
        if self.portx == "串口选择" or self.bps == "波特率选择":
            return
        
        print(self.portx, self.bps)
        self.ret = False
        self.T = 0
        
        try:
            # 打开串口，并得到串口对象
            self.ser = serial.Serial(self.portx, self.bps, timeout = self.timeout)
            #判断是否打开成功
            if(self.ser.is_open):
                
                if self.T != 0:
                    stop_thread(self.T)
                
                self.ret = True
                self.T = threading.Thread(target = self.ReadData, args=())
                print(self.T, type(self.T))
                self.T.start()
                
        except Exception as e:
            tk.messagebox.showinfo('Serial', "---异常---：" + str(e))
            print("---异常---：", e)
            
        return self.ser, self.ret

    #关闭串口
    def DClosePort(self):
        self.ret = False
        self.ser.close()

    #写数据
    def DWritePort(self, text):
        result = self.ser.write(text)
        return result

    #读数据
    def DReadPort():
        global STRGLO
        str = STRGLO
        STRGLO = ""  #清空当次读取
        return str

    #读数代码本体实现
    def ReadData(self):
        global STRGLO
        # 循环接收数据，线程实现
        print("ReadData")
        while self.ret:
            global total_Num
            global current_Num
            if self.ser.in_waiting:
                app.text.see(tk.END) # 一直显示最新的一行
                app.text.update()
                
                STRGLO = self.ser.read(self.ser.in_waiting).hex()

##                percentage = self.format_percentage(curren`t_Num, total_Num*2)       #进度百分比
##                app.text.insert('end', STRGLO + '\t\t进度：' + str(round(current_Num*50/total_Num, 2)) + '%\n')  ##状态返回
                if STRGLO[:14] == '57430b80a00630' and STRGLO[22:24] == '01':
                    app.text.insert('end', STRGLO + '\t\t进度：' + str(round(current_Num*50/total_Num, 2)) + '%\n')  ##状态返回
                    current_Num += 1
                    
                    if app.protocol.get() == "new" and int(app.image_type.get().encode(), 16) == 0x02:   ##新协议前景
                        if image_object.Size - 100*(current_Num-1) >= 100:
                            other_data = [0x57,0x43,0xD2,0x70,0x90,0xCD,0x30] + [0x00, total_Num*2] + \
                                [0x00, current_Num] + image_object.red_byte[100*(current_Num-1):100*current_Num] + image_object.white_byte[100*(current_Num-1):100*current_Num] + [0x00,0xAA]
                        else:
                            other_data = [0x57,0x43,image_object.Size - 100*(current_Num-1)+10,0x70,0x90,image_object.Size - 100*(current_Num-1)+5,0x30] + [0x00, total_Num*2] + \
                                [0x00, current_Num] + image_object.red_byte[100*(current_Num-1):100*current_Num] + image_object.white_byte[100*(current_Num-1):100*current_Num] + [0x00,0xAA]
              
                    else:
                        if current_Num <= total_Num:                  #旧协议背景与前景
                            if image_object.Size - 200*(current_Num-1) >= 200:
                                other_data = [0x57,0x43,0xD2,0x70,0x90,0xCD,0x30] + [0x00,total_Num*2] + \
                                    [0x00,current_Num] + image_object.red_byte[200*(current_Num-1):200*current_Num] +  [0x00,current_Num]

                            elif image_object.Size - 200*(current_Num-1) <  200:                          ##一包不足200字节   
                                other_data = [0x57,0x43,image_object.Size - 200*(current_Num-1)+10, 0x70,0x90, image_object.Size - 200*(current_Num-1)+5, 0x30] + [0x00,total_Num*2] + \
                                    [0x00,current_Num] + image_object.red_byte[200*(current_Num-1):200*(current_Num-1)+(image_object.Size - 200*(current_Num-1))] + [0x00, current_Num]
                            
                        elif current_Num > total_Num and current_Num <= total_Num*2:
                            if image_object.Size - 200*(current_Num-total_Num-1) >= 200:
                                other_data = [0x57,0x43,0xD2,0x70,0x90,0xCD,0x30] + [0x00,total_Num*2] + \
                                    [0x00,current_Num] + image_object.white_byte[200*(current_Num-total_Num-1):200*(current_Num-total_Num)] +[0x00, current_Num]

                            elif image_object.Size - 200*(current_Num-total_Num-1) <  200:
                                other_data = [0x57,0x43,image_object.Size - 200*(current_Num-total_Num-1)+10,0x70,0x90,image_object.Size - 200*(current_Num-total_Num-1)+5,0x30] + \
                                                     [0x00,total_Num*2] + [0x00,current_Num] + image_object.white_byte[200*(current_Num-total_Num-1):200*(current_Num-total_Num) + \
                                                            (image_object.Size - 200*(current_Num-total_Num-1))] +  [0x00, current_Num]                                                

                    if current_Num <= total_Num*2 and total_Num != 0.5:
                        self.DWritePort(other_data)
                        
                        
##    #计算百分比
##    def format_percentage(self, a, b):
##        p = 100 * a / b
##        if p == 0.0:
##            q = '0%'
##        else:
##            q = f'%.2f%%' % p
##        return q
##################################################################################################################
if __name__ == "__main__":
    serial_object = Serial() #串口对象
    app = Application()      #图形主窗口对象
    app.run()
    
