# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time
import threading
from SocketClient import SocketClient


class RFIDProductionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID贴标生产系统")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)

        # 系统状态变量
        self.is_running = False
        self.current_load = 20
        self.daily_production = 199999
        self.line_runtime = "20时10分"
        self.error_message = "无异常"

        # Socket客户端
        self.socket_client = SocketClient('192.168.1.100', 2000)
        self.setup_socket_callbacks()

        # 创建界面
        self.create_title_section()
        self.create_socket_section()
        self.create_device_info_section()
        self.create_rfid_info_section()
        self.create_production_stats_section()
        self.create_status_control_section()

        # 启动时间更新
        self.update_time()

        # 尝试自动连接Socket服务器
        self.auto_connect()

    def create_title_section(self):
        """创建标题区域"""
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="RFID贴标生产系统",
                               font=("微软雅黑", 24, "bold"),
                               bg='#2c3e50', fg='white')
        title_label.pack(pady=20)

    def setup_socket_callbacks(self):
        """设置Socket回调函数"""
        self.socket_client.set_callbacks(
            receive_callback=self.on_socket_receive,
            connection_callback=self.on_connection_status,
            error_callback=self.on_socket_error
        )

    def create_socket_section(self):
        """创建Socket连接控制区域"""
        socket_frame = tk.LabelFrame(self.root, text="网络通信设置",
                                     font=("微软雅黑", 11, "bold"),
                                     bg='white', bd=2, relief='groove',
                                     fg='#2c3e50')
        socket_frame.pack(fill='x', padx=15, pady=5)

        # 服务器配置
        config_frame = tk.Frame(socket_frame, bg='white')
        config_frame.pack(fill='x', padx=10, pady=8)

        tk.Label(config_frame, text="服务器地址:", font=("微软雅黑", 9),
                 bg='white').pack(side='left', padx=(0, 5))

        self.host_entry = tk.Entry(config_frame, width=15, font=("微软雅黑", 9),
                                   relief='solid', bd=1)
        self.host_entry.insert(0, "192.168.1.200")
        self.host_entry.pack(side='left', padx=(0, 15))

        tk.Label(config_frame, text="端口号:", font=("微软雅黑", 9),
                 bg='white').pack(side='left', padx=(0, 5))

        self.port_entry = tk.Entry(config_frame, width=8, font=("微软雅黑", 9),
                                   relief='solid', bd=1)
        self.port_entry.insert(0, "2000")
        self.port_entry.pack(side='left', padx=(0, 20))

        # Socket连接状态和控制按钮
        status_frame = tk.Frame(socket_frame, bg='white')
        status_frame.pack(fill='x', padx=10, pady=8)

        tk.Label(status_frame, text="连接状态:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))

        self.socket_status_label = tk.Label(status_frame, text="未连接",
                                            font=("微软雅黑", 10, "bold"),
                                            bg='white', fg='#e74c3c')
        self.socket_status_label.pack(side='left', padx=(0, 30))

        # 连接控制按钮
        button_frame = tk.Frame(status_frame, bg='white')
        button_frame.pack(side='right')

        self.connect_button = tk.Button(button_frame, text="连接服务器",
                                        font=("微软雅黑", 9), bg='#3498db', fg='white',
                                        width=12, height=1,
                                        command=self.connect_socket)
        self.connect_button.pack(side='left', padx=(0, 10))

        self.disconnect_button = tk.Button(button_frame, text="断开连接",
                                           font=("微软雅黑", 9), bg='#95a5a6', fg='white',
                                           width=12, height=1,
                                           command=self.disconnect_socket,
                                           state='disabled')
        self.disconnect_button.pack(side='left')

        # 消息显示区域
        msg_frame = tk.Frame(socket_frame, bg='white')
        msg_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(msg_frame, text="通信日志:", font=("微软雅黑", 9),
                 bg='white').pack(anchor='w')

        msg_text_frame = tk.Frame(msg_frame, bg='white')
        msg_text_frame.pack(fill='x', pady=5)

        self.message_text = tk.Text(msg_text_frame, height=4, font=("Consolas", 8),
                                    relief='solid', bd=1, wrap='word')
        scrollbar = tk.Scrollbar(msg_text_frame, command=self.message_text.yview)
        self.message_text.config(yscrollcommand=scrollbar.set)

        self.message_text.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.message_text.config(state='disabled')

    def create_device_info_section(self):
        """创建设备信息区域"""
        info_frame = tk.Frame(self.root, bg='white', relief='groove', bd=1)
        info_frame.pack(fill='x', padx=15, pady=5)

        # 第一行信息
        row1_frame = tk.Frame(info_frame, bg='white')
        row1_frame.pack(fill='x', padx=10, pady=5)

        # 设备号
        tk.Label(row1_frame, text="设备号:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        tk.Label(row1_frame, text="RFID-PROD-001", font=("微软雅黑", 10, "bold"),
                 bg='white', fg='#2c3e50').pack(side='left', padx=(0, 40))

        # 软件版本
        tk.Label(row1_frame, text="软件版本:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        tk.Label(row1_frame, text="v2.0.1", font=("微软雅黑", 10, "bold"),
                 bg='white', fg='#2c3e50').pack(side='left')

        # 第二行信息
        row2_frame = tk.Frame(info_frame, bg='white')
        row2_frame.pack(fill='x', padx=10, pady=5)

        # 当前位置
        tk.Label(row2_frame, text="当前位置:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        tk.Label(row2_frame, text="经度116.3918173°, 纬度39.9797956°",
                 font=("微软雅黑", 10), bg='white', fg='#2c3e50').pack(side='left', padx=(0, 40))

        self.time_label = tk.Label(row2_frame, text="", font=("微软雅黑", 10),
                                   bg='white', fg='#2c3e50')
        self.time_label.pack(side='left')

    def create_rfid_info_section(self):
        """创建RFID信息区域"""
        tray_frame = tk.LabelFrame(self.root, text="标签信息",
                                   font=("微软雅黑", 12, "bold"),
                                   bg='white', bd=2, relief='groove',
                                   fg='#2c3e50')
        tray_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # 第一行：托盘编号和托盘装载货物数量
        row1_frame = tk.Frame(tray_frame, bg='white')
        row1_frame.grid(row=0, column=0, columnspan=2, sticky='w', padx=10, pady=15)

        # 托盘编号
        tk.Label(row1_frame, text="托盘编号:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        self.tray_id_entry = tk.Entry(row1_frame, width=30, font=("微软雅黑", 10),
                                      relief='solid', bd=1)
        self.tray_id_entry.insert(0, "TRAY-2024-001")
        self.tray_id_entry.pack(side='left', padx=(0, 40))

        # 托盘装载货物数量
        tk.Label(row1_frame, text="托盘装载货物数量:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        self.tray_load_entry = tk.Entry(row1_frame, width=15, font=("微软雅黑", 10),
                                        relief='solid', bd=1)
        self.tray_load_entry.insert(0, "32")
        self.tray_load_entry.pack(side='left')

        # 取标内容
        tk.Label(tray_frame, text="取标内容:", font=("微软雅黑", 10),
                 bg='white').grid(row=1, column=0, sticky='nw', padx=10, pady=10)
        self.fetch_text = tk.Text(tray_frame, width=50, height=4, font=("微软雅黑", 10),
                                  relief='solid', bd=1, wrap='word')
        self.fetch_text.insert("1.0", "RFID: 001-2024-08-15-001\n产品编码: PROD-001\n生产批次: BATCH-2024-08A")
        self.fetch_text.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # 贴标后内容
        tk.Label(tray_frame, text="贴标后内容:", font=("微软雅黑", 10),
                 bg='white').grid(row=2, column=0, sticky='nw', padx=10, pady=10)
        self.after_text = tk.Text(tray_frame, width=50, height=4, font=("微软雅黑", 10),
                                  relief='solid', bd=1, wrap='word')
        self.after_text.insert("1.0", "RFID: 001-2024-08-15-001-VERIFIED\n产品编码: PROD-001\n状态: 已贴标完成")
        self.after_text.grid(row=2, column=1, padx=10, pady=10, sticky='w')

    def create_production_stats_section(self):
        """创建生产统计区域"""
        stats_frame = tk.Frame(self.root, bg='#f8f9fa', relief='groove', bd=1)
        stats_frame.pack(fill='x', padx=15, pady=10)

        # 产线运行时间
        tk.Label(stats_frame, text="产线运行时间:", font=("微软雅黑", 10, "bold"),
                 bg='#f8f9fa').grid(row=0, column=0, sticky='w', padx=20, pady=15)
        self.runtime_label = tk.Label(stats_frame, text=self.line_runtime,
                                      font=("微软雅黑", 10), bg='#f8f9fa', fg='#e74c3c')
        self.runtime_label.grid(row=0, column=1, sticky='w', padx=5, pady=15)

        # 当前托盘装载数量
        tk.Label(stats_frame, text="当前托盘装载数量:", font=("微软雅黑", 10, "bold"),
                 bg='#f8f9fa').grid(row=0, column=2, sticky='w', padx=20, pady=15)
        self.current_load_label = tk.Label(stats_frame, text=str(self.current_load),
                                           font=("微软雅黑", 10), bg='#f8f9fa', fg='#e74c3c')
        self.current_load_label.grid(row=0, column=3, sticky='w', padx=5, pady=15)

        # 今日生产总量
        tk.Label(stats_frame, text="今日生产总量:", font=("微软雅黑", 10, "bold"),
                 bg='#f8f9fa').grid(row=0, column=4, sticky='w', padx=20, pady=15)
        self.daily_label = tk.Label(stats_frame, text=str(self.daily_production),
                                    font=("微软雅黑", 10), bg='#f8f9fa', fg='#e74c3c')
        self.daily_label.grid(row=0, column=5, sticky='w', padx=5, pady=15)

    def create_status_control_section(self):
        """创建状态和控制区域"""
        bottom_frame = tk.Frame(self.root, bg='#f0f0f0')
        bottom_frame.pack(fill='x', padx=15, pady=10)

        # 左侧状态区域
        status_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        status_frame.pack(side='left', fill='both', expand=True)

        # 产线运行状态
        status_title = tk.Label(status_frame, text="当前产线运行状态:",
                                font=("微软雅黑", 11, "bold"), bg='#f0f0f0')
        status_title.pack(anchor='w')

        status_indicators = tk.Frame(status_frame, bg='#f0f0f0')
        status_indicators.pack(anchor='w', pady=5)

        self.normal_status = tk.Label(status_indicators, text="● 正常",
                                      font=("微软雅黑", 12, "bold"),
                                      fg='#27ae60', bg='#f0f0f0')
        self.normal_status.pack(side='left', padx=10)

        self.abnormal_status = tk.Label(status_indicators, text="● 异常",
                                        font=("微软雅黑", 12),
                                        fg='#bdc3c7', bg='#f0f0f0')
        self.abnormal_status.pack(side='left', padx=10)

        # 异常信息
        error_title = tk.Label(status_frame, text="异常信息:",
                               font=("微软雅黑", 11, "bold"), bg='#f0f0f0')
        error_title.pack(anchor='w', pady=(10, 0))

        self.error_label = tk.Label(status_frame, text=self.error_message,
                                    font=("微软雅黑", 11), fg='#27ae60', bg='#f0f0f0')
        self.error_label.pack(anchor='w')

        # 右侧控制按钮区域
        control_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        control_frame.pack(side='right')

        # 运行产线按钮
        self.run_button = tk.Button(control_frame, text="运行产线",
                                    font=("微软雅黑", 12, "bold"),
                                    bg='#27ae60', fg='white',
                                    width=12, height=2,
                                    command=self.toggle_production)
        self.run_button.pack(pady=5)

        # 紧急制动按钮
        self.emergency_button = tk.Button(control_frame, text="紧急制动",
                                          font=("微软雅黑", 12, "bold"),
                                          bg='#e74c3c', fg='white',
                                          width=12, height=2,
                                          command=self.emergency_stop)
        self.emergency_button.pack(pady=5)

    def update_time(self):
        """更新当前时间显示"""
        current_time = datetime.now().strftime("当前时间: %Y年%m月%d日 %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def toggle_production(self):
        """切换产线运行状态"""
        self.is_running = not self.is_running
        if self.is_running:
            self.run_button.config(text="停止产线", bg='#f39c12')
            self.normal_status.config(fg='#27ae60')
            self.abnormal_status.config(fg='#bdc3c7')
            self.error_label.config(text="运行中", fg='#27ae60')
            self.add_message("产线开始运行")

            # 发送开始生产命令到服务器
            if self.socket_client.is_connected:
                # command = {
                #     "type": "production_control",
                #     "command": "start",
                #     "timestamp": datetime.now().isoformat(),
                #     "data": {
                #         "current_load": self.current_load,
                #         "daily_production": self.daily_production
                #     }
                # }
                # self.socket_client.send_data(command)
                command_bytes = bytes([0xA5, 0x5A, 0x00, 0x0A, 0x80, 0x00, 0x64, 0xEE, 0x0D, 0x0A])
                # print(command_bytes)
                print(len(command_bytes))
                self.socket_client.send_data(command_bytes)

        else:
            self.run_button.config(text="运行产线", bg='#27ae60')
            self.normal_status.config(fg='#bdc3c7')
            self.abnormal_status.config(fg='#bdc3c7')
            self.error_label.config(text="已停止", fg='#95a5a6')
            self.add_message("产线已停止")

            # 发送停止生产命令到服务器
            if self.socket_client.is_connected:
                # command = {
                #     "type": "production_control",
                #     "command": "stop",
                #     "timestamp": datetime.now().isoformat()
                # }
                # self.socket_client.send_data(command)
                command_bytes = bytes([0xA5, 0x5A, 0x00, 0x0A, 0x80, 0x00, 0x64, 0xEE, 0x0D, 0x0A])
                # print(command_bytes)
                print(len(command_bytes))
                self.socket_client.send_data(command_bytes)

    def emergency_stop(self):
        """紧急制动"""
        self.is_running = False
        self.run_button.config(text="运行产线", bg='#27ae60')
        self.normal_status.config(fg='#bdc3c7')
        self.abnormal_status.config(fg='#e74c3c')
        self.error_label.config(text="紧急制动！", fg='#e74c3c')
        self.add_message("紧急制动！系统已停止")

        # 发送紧急停止命令到服务器
        if self.socket_client.is_connected:
            command = {
                "type": "emergency_stop",
                "timestamp": datetime.now().isoformat(),
                "message": "用户触发紧急制动"
            }
            self.socket_client.send_data(command)

        messagebox.showwarning("紧急制动", "系统已紧急停止！")

    def simulate_production(self):
        """模拟生产数据更新（可选功能）"""
        if self.is_running:
            self.current_load += 1
            self.daily_production += 1
            self.current_load_label.config(text=str(self.current_load))
            self.daily_label.config(text=str(self.daily_production))

        self.root.after(5000, self.simulate_production)

    # Socket相关方法
    def auto_connect(self):
        """自动连接Socket服务器"""
        self.add_message("系统启动，准备连接服务器...")

        def connect_thread():
            time.sleep(2)  # 延迟2秒连接，让界面先加载完成
            if self.socket_client.connect():
                self.add_message("自动连接服务器成功")
            else:
                self.add_message("自动连接失败，请手动连接")

        threading.Thread(target=connect_thread, daemon=True).start()

    def connect_socket(self):
        """连接Socket服务器"""
        # 更新服务器配置
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            self.socket_client.host = host
            self.socket_client.port = port
        except ValueError:
            messagebox.showerror("错误", "端口号必须是数字")
            return

        def connect_thread():
            if self.socket_client.connect():
                self.add_message(f"手动连接服务器 {host}:{port} 成功")

        threading.Thread(target=connect_thread, daemon=True).start()
        self.connect_button.config(state='disabled', text="连接中...")
        self.add_message(f"正在连接服务器 {host}:{port}...")

    def disconnect_socket(self):
        """断开Socket连接"""
        self.socket_client.disconnect()
        self.add_message("手动断开服务器连接")

    def on_connection_status(self, connected, message):
        """连接状态回调（在Socket线程中调用）"""

        def update_ui():
            if connected:
                self.socket_status_label.config(text="● 已连接", fg='#27ae60')
                self.connect_button.config(state='disabled', text="已连接")
                self.disconnect_button.config(state='normal', bg='#e74c3c')
                self.host_entry.config(state='disabled')
                self.port_entry.config(state='disabled')
            else:
                self.socket_status_label.config(text="● 未连接", fg='#e74c3c')
                self.connect_button.config(state='normal', text="连接服务器")
                self.disconnect_button.config(state='disabled', bg='#95a5a6')
                self.host_entry.config(state='normal')
                self.port_entry.config(state='normal')

            self.add_message(message)

        # 使用after确保线程安全
        self.root.after(0, update_ui)

    def on_socket_receive(self, data):
        """接收到Socket数据的回调（支持二进制数据）"""
        print('on_socket_receive')
        def update_ui():
            if isinstance(data, bytes):
                # 处理二进制数据
                self.handle_binary_data(data)
            elif isinstance(data, dict):
                # 处理JSON数据
                self.handle_json_data(data)
            else:
                # 其他类型数据
                self.add_message(f"收到未知格式数据: {type(data)}")

        self.root.after(0, update_ui)

    def handle_binary_data(self, data: bytes):
        """处理二进制数据"""
        # 将二进制数据转换为十六进制字符串显示
        hex_data = data.hex().upper()
        formatted_hex = ' '.join([hex_data[i:i + 2] for i in range(0, len(hex_data), 2)])

        self.add_message(f"收到二进制数据: {formatted_hex}")

        # 解析特定的二进制协议
        if len(data) >= 10:  # 假设你的协议数据包至少10字节
            # 示例：解析 A5 5A 开头的协议
            if data[0] == 0xA5 and data[1] == 0x5A:
                self.parse_protocol_a55a(data)

    def parse_protocol_a55a(self, data: bytes):
        """解析 A5 5A 协议格式"""
        try:
            # 示例解析逻辑
            header = data[0:2]  # A5 5A
            length = data[2]  # 数据长度
            command = data[4]  # 命令字
            # ... 根据你的实际协议解析

            self.add_message(f"解析协议: 长度={len(data)}, 命令=0x{command:02X}")

            # 根据命令类型更新界面
            if command == 0x80:  # 生产状态命令
                self.update_production_status(data)
            elif command == 0x81:  # RFID数据命令
                self.update_rfid_data(data)

        except Exception as e:
            self.add_message(f"协议解析错误: {e}")

    def handle_json_data(self, data: dict):
        """处理JSON数据"""
        msg_type = data.get('type', '')
        if msg_type == 'production_data':
            self.handle_production_data(data)
        elif msg_type == 'status_update':
            self.handle_status_update(data)
        elif msg_type == 'rfid_data':
            self.handle_rfid_data(data)
        else:
            self.add_message(f"收到JSON数据: {data}")

    def on_socket_error(self, error_msg):
        """Socket错误回调（在Socket线程中调用）"""

        def update_ui():
            self.add_message(f"错误: {error_msg}")
            # 只在重要错误时显示弹窗
            if "连接" in error_msg or "断开" in error_msg:
                messagebox.showerror("Socket错误", error_msg)

        self.root.after(0, update_ui)

    def handle_production_data(self, data):
        """处理生产数据"""
        production_data = data.get('data', {})

        if 'daily_production' in production_data:
            self.daily_production = production_data['daily_production']
            self.daily_label.config(text=str(self.daily_production))

        if 'current_load' in production_data:
            self.current_load = production_data['current_load']
            self.current_load_label.config(text=str(self.current_load))
            self.tray_load_entry.delete(0, tk.END)
            self.tray_load_entry.insert(0, str(self.current_load))

        if 'line_runtime' in production_data:
            self.line_runtime = production_data['line_runtime']
            self.runtime_label.config(text=self.line_runtime)

        self.add_message("生产数据已更新")

    def handle_status_update(self, data):
        """处理状态更新"""
        status_data = data.get('data', {})

        if 'line_status' in status_data:
            status = status_data['line_status']
            if status == 'normal':
                self.normal_status.config(fg='#27ae60')
                self.abnormal_status.config(fg='#bdc3c7')
                if not self.is_running:
                    self.is_running = True
                    self.run_button.config(text="停止产线", bg='#f39c12')
            else:
                self.normal_status.config(fg='#bdc3c7')
                self.abnormal_status.config(fg='#e74c3c')
                if self.is_running:
                    self.is_running = False
                    self.run_button.config(text="运行产线", bg='#27ae60')

        if 'error_message' in status_data:
            self.error_message = status_data['error_message']
            self.error_label.config(text=self.error_message)
            if status_data['error_message'] != "无异常":
                self.error_label.config(fg='#e74c3c')
            else:
                self.error_label.config(fg='#27ae60')

        self.add_message("设备状态已更新")

    def handle_rfid_data(self, data):
        """处理RFID数据"""
        rfid_data = data.get('data', {})

        if 'tray_id' in rfid_data:
            self.tray_id_entry.delete(0, tk.END)
            self.tray_id_entry.insert(0, rfid_data['tray_id'])

        if 'fetch_content' in rfid_data:
            self.fetch_text.delete('1.0', tk.END)
            self.fetch_text.insert('1.0', rfid_data['fetch_content'])

        if 'after_content' in rfid_data:
            self.after_text.delete('1.0', tk.END)
            self.after_text.insert('1.0', rfid_data['after_content'])

        if 'load_count' in rfid_data:
            self.tray_load_entry.delete(0, tk.END)
            self.tray_load_entry.insert(0, str(rfid_data['load_count']))

        self.add_message("RFID标签数据已更新")

    def handle_heartbeat(self, data):
        """处理心跳数据"""
        # 可以在这里更新最后通信时间等状态
        pass

    def add_message(self, message):
        """添加消息到消息框"""

        def _add_message():
            self.message_text.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.message_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.message_text.see(tk.END)
            self.message_text.config(state='disabled')

            # 限制消息数量
            lines = int(self.message_text.index('end-1c').split('.')[0])
            if lines > 100:  # 保留最近100条消息
                self.message_text.delete('1.0', '2.0')

        # 确保线程安全
        self.root.after(0, _add_message)

    def on_closing(self):
        """程序关闭时的清理工作"""
        if self.socket_client.is_connected:
            self.socket_client.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = RFIDProductionSystem(root)

    # 设置关闭窗口事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # 可选：启动生产数据模拟
    # app.simulate_production()

    root.mainloop()


if __name__ == "__main__":
    main()