import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time


class RFIDProductionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID贴标生产系统")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)

        # 系统状态变量
        self.is_running = False
        self.current_load = 20
        self.daily_production = 199999
        self.line_runtime = "20时10分"
        self.error_message = "标签读取失败"

        # 创建界面
        # self.create_title_section()
        self.create_device_info_section()
        self.create_tray_info_section()
        self.create_production_stats_section()
        self.create_status_control_section()

        # 启动时间更新
        self.update_time()

    def create_title_section(self):
        """创建标题区域"""
        title_frame = tk.Frame(self.root, bg='#f0f0f0', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="RFID贴标生产系统",
                               font=("微软雅黑", 20, "bold"),
                               bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)

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
        tk.Label(row1_frame, text="1234567890ABCDEFGH", font=("微软雅黑", 10, "bold"),
                 bg='white', fg='#2c3e50').pack(side='left', padx=(0, 20))

        # 软件版本
        tk.Label(row1_frame, text="软件版本:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        tk.Label(row1_frame, text="v1.0.0", font=("微软雅黑", 10, "bold"),
                 bg='white', fg='#2c3e50').pack(side='left')

        # 第二行信息
        row2_frame = tk.Frame(info_frame, bg='white')
        row2_frame.pack(fill='x', padx=10, pady=5)

        # 当前位置
        tk.Label(row2_frame, text="当前位置:", font=("微软雅黑", 10),
                 bg='white').pack(side='left', padx=(0, 5))
        tk.Label(row2_frame, text="经度116.3918173°,纬度39.9797956°",
                 font=("微软雅黑", 10), bg='white', fg='#2c3e50').pack(side='left')

        # 第三行信息 - 当前时间
        row3_frame = tk.Frame(info_frame, bg='white')
        row3_frame.pack(fill='x', padx=10, pady=5)

        self.time_label = tk.Label(row3_frame, text="", font=("微软雅黑", 10),
                                   bg='white', fg='#e74c3c')
        self.time_label.pack(side='left')

    def create_tray_info_section(self):
        """创建托盘信息区域"""
        tray_frame = tk.LabelFrame(self.root, text="托盘信息",
                                   font=("微软雅黑", 12, "bold"),
                                   bg='white', bd=2, relief='groove',
                                   fg='#2c3e50')
        tray_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # 托盘编号
        tk.Label(tray_frame, text="托盘编号:", font=("微软雅黑", 10),
                 bg='white').grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.tray_id_entry = tk.Entry(tray_frame, width=50, font=("微软雅黑", 10),
                                      relief='solid', bd=1)
        self.tray_id_entry.insert(0, "XXXXXXXXXXXXXXX")
        self.tray_id_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # 托盘装载货物数量
        tk.Label(tray_frame, text="托盘装载货物数量:", font=("微软雅黑", 10),
                 bg='white').grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.tray_load_entry = tk.Entry(tray_frame, width=15, font=("微软雅黑", 10),
                                        relief='solid', bd=1)
        self.tray_load_entry.insert(0, "32")
        self.tray_load_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # 取标内容
        tk.Label(tray_frame, text="取标内容:", font=("微软雅黑", 10),
                 bg='white').grid(row=2, column=0, sticky='nw', padx=10, pady=10)
        self.fetch_text = tk.Text(tray_frame, width=50, height=4, font=("微软雅黑", 10),
                                  relief='solid', bd=1, wrap='word')
        self.fetch_text.insert("1.0", "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        self.fetch_text.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        # 贴标后内容
        tk.Label(tray_frame, text="贴标后内容:", font=("微软雅黑", 10),
                 bg='white').grid(row=3, column=0, sticky='nw', padx=10, pady=10)
        self.after_text = tk.Text(tray_frame, width=50, height=4, font=("微软雅黑", 10),
                                  relief='solid', bd=1, wrap='word')
        self.after_text.insert("1.0", "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        self.after_text.grid(row=3, column=1, padx=10, pady=10, sticky='w')

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

        self.normal_status = tk.Label(status_indicators, text="正常",
                                      font=("微软雅黑", 12, "bold"),
                                      fg='#27ae60', bg='#f0f0f0')
        self.normal_status.pack(side='left', padx=10)

        self.abnormal_status = tk.Label(status_indicators, text="异常",
                                        font=("微软雅黑", 12),
                                        fg='#e74c3c', bg='#f0f0f0')
        self.abnormal_status.pack(side='left', padx=10)

        # 异常信息
        error_title = tk.Label(status_frame, text="异常信息:",
                               font=("微软雅黑", 11, "bold"), bg='#f0f0f0')
        error_title.pack(anchor='w', pady=(10, 0))

        self.error_label = tk.Label(status_frame, text=self.error_message,
                                    font=("微软雅黑", 11), fg='#e74c3c', bg='#f0f0f0')
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
            self.normal_status.config(font=("微软雅黑", 12, "bold"))
            self.abnormal_status.config(font=("微软雅黑", 12))
            messagebox.showinfo("系统提示", "产线开始运行")
        else:
            self.run_button.config(text="运行产线", bg='#27ae60')
            self.normal_status.config(font=("微软雅黑", 12))
            self.abnormal_status.config(font=("微软雅黑", 12))
            messagebox.showinfo("系统提示", "产线已停止")

    def emergency_stop(self):
        """紧急制动"""
        self.is_running = False
        self.run_button.config(text="运行产线", bg='#27ae60')
        self.normal_status.config(font=("微软雅黑", 12))
        self.abnormal_status.config(font=("微软雅黑", 12, "bold"))
        messagebox.showwarning("紧急制动", "系统已紧急停止！")

    def simulate_production(self):
        """模拟生产数据更新（可选功能）"""
        if self.is_running:
            self.current_load += 1
            self.daily_production += 1
            self.current_load_label.config(text=str(self.current_load))
            self.daily_label.config(text=str(self.daily_production))

        self.root.after(5000, self.simulate_production)


def main():
    root = tk.Tk()
    app = RFIDProductionSystem(root)

    # 可选：启动生产数据模拟
    # app.simulate_production()

    root.mainloop()


if __name__ == "__main__":
    main()