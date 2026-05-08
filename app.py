import json
import time
import tkinter as tk
from threading import Thread
from tkinter import ttk, scrolledtext, messagebox, filedialog

from scraper import AlibabaScraperCore


class SegmentProgressbar(tk.Canvas):
    """格子化进度条组件"""

    def __init__(self, master, segments=100, width=400, height=25, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        self.segments = segments
        self.segment_width = (width - (segments - 1) * 2) // segments
        self.segment_height = height - 6
        self.current_value = 0
        self.max_value = 100
        self.bg_color = '#e0e0e0'
        self.fill_color = '#4CAF50'
        self.empty_color = '#d0d0d0'
        self.border_radius = 3
        self.draw_background()

    def draw_background(self):
        """绘制背景格子"""
        self.delete("all")
        x = 3
        y = 1
        for i in range(self.segments):
            self.create_rectangle(x, y, x + self.segment_width, y + self.segment_height,
                                  fill=self.empty_color, outline='#b0b0b0', width=1,
                                  tags=f"segment_{i}")
            x += self.segment_width + 2
        self.update()

    def set_value(self, percent):
        """设置进度百分比"""
        self.current_value = min(max(percent, 0), 100)
        filled_segments = int((self.current_value / 100) * self.segments)

        x = 3
        y = 3
        for i in range(self.segments):
            if i < filled_segments:
                if i < self.segments * 0.3:
                    color = '#f44336'
                elif i < self.segments * 0.7:
                    color = '#FF9800'
                else:
                    color = '#4CAF50'

                self.create_rectangle(x, y, x + self.segment_width, y + self.segment_height,
                                      fill=color, outline='#ffffff', width=1,
                                      tags=f"segment_{i}")
                self.create_rectangle(x + 1, y + 1, x + self.segment_width - 1, y + self.segment_height - 1,
                                      fill=color, outline='', stipple='gray50', tags=f"glow_{i}")
            else:
                self.create_rectangle(x, y, x + self.segment_width, y + self.segment_height,
                                      fill=self.empty_color, outline='#b0b0b0', width=1,
                                      tags=f"segment_{i}")
            x += self.segment_width + 2
        self.update()

    def get_value(self):
        return self.current_value

    def reset(self):
        """重置进度条"""
        self.set_value(0)


class AlibabaScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("1688商品数据采集工具 V1.0")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

        # 尝试设置图标
        try:
            self.root.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='./th.ico'))
        except:
            pass

        self.main_frame = tk.Frame(root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 初始化爬虫核心
        self.scraper = AlibabaScraperCore()
        self.setup_callbacks()

        self.all_results = []
        self.is_scraping = False
        self.json_update_counter = 0

        # 商家筛选相关属性
        self.filter_keyword = ""
        self.filtered_results = []

        self.create_control_panel()
        self.create_display_area()

    def setup_callbacks(self):
        """设置爬虫回调函数"""
        self.scraper.register_callback('on_data', self.on_data_collected)
        self.scraper.register_callback('on_progress', self.on_progress)
        self.scraper.register_callback('on_log', self.log_message)
        self.scraper.register_callback('on_finish', self.on_finish)

    def on_data_collected(self, data):
        """数据采集回调"""
        self.all_results.append(data)
        self.root.after(0, lambda: self.add_to_table(data))
        self.root.after(0, self.update_json_view)

    def on_progress(self, current, total, page, async_num, items_count):
        """进度更新回调"""
        self.root.after(0, lambda: self.update_progress(current, total, page, async_num, items_count))

    def on_finish(self, results, total_items):
        """采集完成回调"""
        self.root.after(0, lambda: self.on_scrape_finished(total_items))

    def create_control_panel(self):
        """创建控制面板（顶部导航栏 + 参数设置区）"""
        # ----- 顶部导航栏 -----
        nav_frame = tk.Frame(self.main_frame, height=40)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        nav_frame.pack_propagate(False)

        # 左侧：采集控制标题
        self.control_button = tk.Button(nav_frame, text="采集控制", font=("微软雅黑", 10, "bold"),
                                        bg='#2c3e50', fg='white', relief='raised', bd=2, padx=3, pady=2,
                                         cursor="hand2")
        self.control_button.pack(side=tk.LEFT, padx=5)

        # 更新程序按钮（导航栏风格）
        self.update_button = tk.Button(nav_frame, text="更新程序", command=self.run_update_script,
                                       bg='#2c3e50', fg='white', font=("微软雅黑", 10, "bold"),
                                       relief=tk.RAISED, bd=2, padx=3, pady=2, cursor="hand2")
        self.update_button.pack(side=tk.LEFT, padx=5)

        # 可选：添加一个装饰分隔线
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 5))

        # ----- 参数设置区域（原控制面板主体）-----
        control_frame = tk.LabelFrame(self.main_frame, text="参数设置", bg='#f0f0f0',
                                      font=("微软雅黑", 10), padx=5, pady=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 第一行：输入参数
        row1 = tk.Frame(control_frame, bg='#f0f0f0')
        row1.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(row1, text="搜索关键词:", bg='#f0f0f0', font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.keyword_entry = tk.Entry(row1, width=15, font=("微软雅黑", 10))
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        self.keyword_entry.insert(0, "手机")

        tk.Label(row1, text="起始页:", bg='#f0f0f0', font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.start_page = tk.Spinbox(row1, from_=1, to=50, width=6, font=("微软雅黑", 10))
        self.start_page.pack(side=tk.LEFT, padx=5)
        self.start_page.delete(0, 'end')
        self.start_page.insert(0, '1')

        tk.Label(row1, text="结束页:", bg='#f0f0f0', font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.end_page = tk.Spinbox(row1, from_=1, to=50, width=6, font=("微软雅黑", 10))
        self.end_page.pack(side=tk.LEFT, padx=5)
        self.end_page.delete(0, 'end')
        self.end_page.insert(0, '2')

        tk.Label(row1, text="异步数(1-6):", bg='#f0f0f0', font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.async_count = tk.Spinbox(row1, from_=1, to=6, width=5, font=("微软雅黑", 10))
        self.async_count.pack(side=tk.LEFT, padx=5)
        self.async_count.delete(0, 'end')
        self.async_count.insert(0, '6')

        # 第二行：操作按钮
        row2 = tk.Frame(control_frame, bg='#f0f0f0')
        row2.pack(fill=tk.X, padx=5, pady=5)

        self.start_button = tk.Button(row2, text="开始采集", command=self.start_scraping,
                                      bg='#4CAF50', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                      relief=tk.RAISED, bd=2)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(row2, text="停止采集", command=self.stop_scraping,
                                     bg='#f44336', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                     state='disabled', relief=tk.RAISED, bd=2)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(row2, text="清空数据", command=self.clear_data,
                                      bg='#FF9800', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                      relief=tk.RAISED, bd=2)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(row2, text="保存数据", command=self.save_data,
                                     bg='#2196F3', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                     relief=tk.RAISED, bd=2)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.refresh_json_button = tk.Button(row2, text="刷新JSON", command=self.force_refresh_json,
                                             bg='#9C27B0', fg='white', font=("微软雅黑", 10, "bold"), width=10,
                                             relief=tk.RAISED, bd=2)
        self.refresh_json_button.pack(side=tk.LEFT, padx=5)

        self.auto_scroll_json = tk.BooleanVar(value=True)
        self.auto_scroll_check = tk.Checkbutton(row2, text="自动滚动", variable=self.auto_scroll_json,
                                                bg='#f0f0f0', font=("微软雅黑", 9))
        self.auto_scroll_check.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(control_frame, text="就绪", bg='#f0f0f0', font=("微软雅黑", 9), fg='green')
        self.status_label.pack(pady=5)

        # 进度条区域
        progress_container = tk.Frame(control_frame, bg='#e0e0e0', bd=1, relief=tk.SUNKEN)
        progress_container.pack(fill=tk.X, padx=5, pady=5)
        progress_container.grid_columnconfigure(0, weight=1)

        progress_inner = tk.Frame(progress_container, bg='#e0e0e0', padx=3, pady=3)
        progress_inner.pack(fill=tk.BOTH, expand=True)

        self.progress_info_label = tk.Label(progress_inner, text="等待开始...", bg='#e0e0e0',
                                            font=("微软雅黑", 8), fg='#666')
        self.progress_info_label.pack(anchor='w')

        progress_bar_frame = tk.Frame(progress_inner, bg='#e0e0e0')
        progress_bar_frame.pack(fill=tk.X, pady=(5, 5))

        self.segment_progress = SegmentProgressbar(progress_bar_frame, segments=100, width=600, height=28, bg='#e0e0e0')
        self.segment_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.percent_label = tk.Label(progress_bar_frame, text="0%", bg='#4CAF50', fg='white',
                                      font=("微软雅黑", 10, "bold"), width=6,
                                      relief=tk.RAISED, bd=1)
        self.percent_label.pack(side=tk.RIGHT, padx=(8, 0))

        detail_frame = tk.Frame(progress_inner, bg='#e0e0e0')
        detail_frame.pack(fill=tk.X, pady=(3, 0))

        self.progress_detail_label = tk.Label(detail_frame, text="", bg='#e0e0e0',
                                              font=("微软雅黑", 8), fg='#555')
        self.progress_detail_label.pack(side=tk.LEFT)

        self.progress_count_label = tk.Label(detail_frame, text="", bg='#e0e0e0',
                                             font=("微软雅黑", 8), fg='#555')
        self.progress_count_label.pack(side=tk.RIGHT)

    def create_display_area(self):
        """创建数据显示区域"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.table_frame = tk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="表格视图")
        self.create_table_view()

        self.json_frame = tk.Frame(self.notebook)
        self.notebook.add(self.json_frame, text="JSON视图")
        self.create_json_view()

        self.log_frame = tk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="采集日志")
        self.create_log_view()

    def create_table_view(self):
        """创建表格视图（商家筛选栏）"""
        filter_bar = tk.Frame(self.table_frame, bg='#f0f0f0', height=35)
        filter_bar.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filter_bar, text="商家筛选:", bg='#f0f0f0', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)

        self.filter_entry = tk.Entry(filter_bar, width=20, font=("微软雅黑", 9))
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        self.filter_entry.bind("<Return>", lambda e: self.apply_filter())

        self.filter_apply_btn = tk.Button(filter_bar, text="应用筛选", command=self.apply_filter,
                                          bg='#4CAF50', fg='white', font=("微软雅黑", 9), width=10)
        self.filter_apply_btn.pack(side=tk.LEFT, padx=2)

        self.filter_reset_btn = tk.Button(filter_bar, text="重置筛选", command=self.reset_filter,
                                          bg='#FF9800', fg='white', font=("微软雅黑", 9), width=10)
        self.filter_reset_btn.pack(side=tk.LEFT, padx=2)

        self.filter_match_label = tk.Label(filter_bar, text="", bg='#f0f0f0', font=("微软雅黑", 9), fg='blue')
        self.filter_match_label.pack(side=tk.LEFT, padx=10)

        scroll_y = ttk.Scrollbar(self.table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ('图片', '标题', '价格', '商家', '链接')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.heading('图片', text='图片')
        self.tree.heading('标题', text='商品标题')
        self.tree.heading('价格', text='价格(元)')
        self.tree.heading('商家', text='商家')
        self.tree.heading('链接', text='商品链接')

        self.tree.column('图片', width=100)
        self.tree.column('标题', width=500)
        self.tree.column('价格', width=100)
        self.tree.column('商家', width=150)
        self.tree.column('链接', width=300)

        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)

    def create_json_view(self):
        """创建JSON视图"""
        json_toolbar = tk.Frame(self.json_frame, bg='#f0f0f0')
        json_toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(json_toolbar, text="复制JSON", command=self.copy_json,
                  bg='#4CAF50', fg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(json_toolbar, text="格式化", command=self.format_json,
                  bg='#2196F3', fg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(json_toolbar, text="清空", command=self.clear_json_view,
                  bg='#f44336', fg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(json_toolbar, text="滚动到底部", command=self.scroll_json_to_end,
                  bg='#FF9800', fg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=2)

        json_line_frame = tk.Frame(self.json_frame)
        json_line_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.json_line_numbers = tk.Text(json_line_frame, width=5, padx=2, takefocus=0,
                                         border=0, background='#f0f0f0', state='disabled',
                                         font=("Consolas", 10))
        self.json_line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.json_text = scrolledtext.ScrolledText(self.json_frame, wrap=tk.WORD,
                                                   font=("Consolas", 10))
        self.json_text.pack(fill=tk.BOTH, expand=True)

        self.json_text.bind('<MouseWheel>', self.sync_json_scroll)
        self.json_text.bind('<Button-4>', self.sync_json_scroll)
        self.json_text.bind('<Button-5>', self.sync_json_scroll)
        self.json_text.bind('<<Modified>>', self.on_json_modified)

    def create_log_view(self):
        """创建日志视图"""
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config('info', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')

    # ------------------ 商家筛选 ------------------
    def apply_filter(self):
        if self.is_scraping:
            self.log_message("采集进行中，请等待采集完成后再使用筛选功能", 'warning')
            return
        self.filter_keyword = self.filter_entry.get().strip()
        self.refresh_display()

    def reset_filter(self):
        self.filter_entry.delete(0, tk.END)
        self.filter_keyword = ""
        self.refresh_display()

    def refresh_display(self):
        if not self.filter_keyword:
            self.filtered_results = self.all_results.copy()
        else:
            kw_lower = self.filter_keyword.lower()
            self.filtered_results = [item for item in self.all_results
                                     if kw_lower in item.get('loginId', '').lower()]

        for row in self.tree.get_children():
            self.tree.delete(row)
        for data in self.filtered_results:
            self._add_item_to_tree(data)

        self._display_json_for_data(self.filtered_results)

        total = len(self.all_results)
        matched = len(self.filtered_results)
        if self.filter_keyword:
            self.filter_match_label.config(text=f"匹配商家 {matched} / {total} 条")
        else:
            self.filter_match_label.config(text=f"共 {total} 条数据")

    def _add_item_to_tree(self, data):
        price = data.get('price', '')
        if price:
            try:
                price = f"¥{float(price):.2f}"
            except:
                pass
        self.tree.insert('', tk.END, values=(
            "📷 查看",
            data.get('simpleSubject', '')[:100],
            price,
            data.get('loginId', ''),
            data.get('odUrl', '')[:80]
        ))

    def _display_json_for_data(self, data_list):
        try:
            current_scroll = self.json_text.yview()[0] if not self.auto_scroll_json.get() else None
            self.json_text.delete(1.0, tk.END)
            if data_list:
                json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
                self.json_text.insert(1.0, json_str)
                self.update_line_numbers()
                if self.auto_scroll_json.get():
                    self.json_text.see(tk.END)
                    self.json_line_numbers.yview_moveto(1)
                elif current_scroll is not None:
                    self.json_text.yview_moveto(current_scroll)
            else:
                self.json_text.insert(1.0, "无匹配数据")
                self.update_line_numbers()
        except Exception as e:
            self.log_message(f"JSON显示错误: {str(e)}", 'error')

    # ------------------ 更新功能 ------------------
    def run_update_script(self):
        """运行 update.py 进行程序更新（独立子进程）"""
        if self.is_scraping:
            self.log_message("采集任务进行中，请稍后再更新", 'warning')
            return

        self.update_button.config(state='disabled')
        self.log_message("开始执行更新程序，请勿关闭窗口...", 'info')

        def target():
            import subprocess
            import sys
            from pathlib import Path

            update_script = Path(__file__).parent / "update.py"
            if not update_script.exists():
                self.root.after(0, lambda: self.log_message("错误：未找到 update.py 文件", 'error'))
                self.root.after(0, lambda: self.update_button.config(state='normal'))
                return

            try:
                proc = subprocess.Popen(
                    [sys.executable, str(update_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    bufsize=1
                )
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        self.root.after(0, lambda l=line: self.log_message(l.strip(), 'info'))
                proc.wait()
                if proc.returncode == 0:
                    self.root.after(0, lambda: self.log_message("更新完成！", 'info'))
                    # 弹出提示框
                    self.root.after(0, lambda: messagebox.showinfo("更新完成", "程序已成功更新到最新版本！"))
                else:
                    self.root.after(0, lambda: self.log_message(f"更新失败，退出码 {proc.returncode}", 'error'))
                    self.root.after(0, lambda: messagebox.showerror("更新失败", f"更新过程中出现错误，退出码：{proc.returncode}"))
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"执行更新时出错: {str(e)}", 'error'))
                self.root.after(0, lambda: messagebox.showerror("更新错误", f"执行更新脚本时发生异常：{str(e)}"))
            finally:
                self.root.after(0, lambda: self.update_button.config(state='normal'))

        Thread(target=target, daemon=True).start()

    # ------------------ 其他界面交互 ------------------
    def sync_json_scroll(self, event):
        self.json_line_numbers.yview_moveto(self.json_text.yview()[0])
        return None

    def update_line_numbers(self):
        try:
            lines = int(self.json_text.index('end-1c').split('.')[0])
            line_numbers = '\n'.join(str(i) for i in range(1, lines + 1))
            self.json_line_numbers.config(state='normal')
            self.json_line_numbers.delete(1.0, tk.END)
            self.json_line_numbers.insert(1.0, line_numbers)
            self.json_line_numbers.config(state='disabled')
        except:
            pass

    def on_json_modified(self, event=None):
        self.json_text.edit_modified(False)
        self.update_line_numbers()

    def clear_json_view(self):
        self.json_text.delete(1.0, tk.END)
        self.json_line_numbers.config(state='normal')
        self.json_line_numbers.delete(1.0, tk.END)
        self.json_line_numbers.config(state='disabled')

    def format_json(self):
        try:
            content = self.json_text.get(1.0, tk.END).strip()
            if content:
                data = json.loads(content)
                formatted = json.dumps(data, ensure_ascii=False, indent=2)
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(1.0, formatted)
                self.update_line_numbers()
                self.log_message("JSON格式化完成", 'info')
        except json.JSONDecodeError as e:
            self.log_message(f"JSON格式错误: {e}", 'error')

    def copy_json(self):
        try:
            content = self.json_text.get(1.0, tk.END).strip()
            if content:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.log_message("JSON已复制到剪贴板", 'info')
                return True
        except Exception as e:
            self.log_message(f"复制失败: {e}", 'error')
        return False

    def scroll_json_to_end(self):
        self.json_text.see(tk.END)
        self.json_line_numbers.yview_moveto(1)
        self.log_message("已滚动到JSON底部", 'info')

    def log_message(self, message, level='info'):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)

    def update_status(self, message, color='green'):
        self.status_label.config(text=message, fg=color)

    def update_progress(self, current, total, current_page=None, current_async=None, items_count=0):
        if total > 0:
            percent = (current / total) * 100
            self.segment_progress.set_value(percent)

            if percent < 30:
                bg_color = '#f44336'
            elif percent < 70:
                bg_color = '#FF9800'
            else:
                bg_color = '#4CAF50'

            self.percent_label.config(text=f"{percent:.1f}%", bg=bg_color)
            self.progress_info_label.config(text=f"请求进度: {current} / {total}")

            if current_page:
                self.progress_detail_label.config(text=f"当前位置: 第{current_page}页 / 异步{current_async}")
            else:
                self.progress_detail_label.config(text=f"完成进度: {percent:.1f}%")

            self.progress_count_label.config(text=f"已采集: {items_count} 条商品")

    def reset_progress(self):
        self.segment_progress.reset()
        self.percent_label.config(text="0%", bg='#999')
        self.progress_info_label.config(text="等待开始...")
        self.progress_detail_label.config(text="")
        self.progress_count_label.config(text="")
        self.filter_match_label.config(text="")

    def stop_scraping(self):
        if self.scraper.is_scraping:
            self.scraper.stop()
            self.update_status("正在停止...", 'orange')

    def on_scrape_finished(self, total_items):
        self.is_scraping = False
        self._set_filter_controls_state(True)
        self.refresh_display()
        self.update_status(f"采集完成！共采集 {total_items} 条数据", 'green')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.clear_button.config(state='normal')
        self.save_button.config(state='normal')
        self.log_message(f"采集完成！共采集 {total_items} 条数据", 'info')

    def add_to_table(self, data):
        self._add_item_to_tree(data)
        self.tree.yview_moveto(1)

    def clear_data(self):
        if messagebox.askyesno("确认", "确定要清空所有数据吗？"):
            self.all_results.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.clear_json_view()
            self.filter_keyword = ""
            self.filter_entry.delete(0, tk.END)
            self.filter_match_label.config(text="")
            self.log_message("所有数据已清空", 'warning')
            self.update_status("数据已清空", 'green')
            self.reset_progress()

    def start_scraping(self):
        if self.scraper.is_scraping:
            messagebox.showwarning("警告", "采集任务正在进行中！")
            return

        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词！")
            return

        start_page = int(self.start_page.get())
        end_page = int(self.end_page.get())
        async_count = int(self.async_count.get())

        if start_page > end_page:
            messagebox.showerror("错误", "起始页不能大于结束页！")
            return

        self.reset_filter()
        self._set_filter_controls_state(False)

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.clear_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.reset_progress()

        if messagebox.askyesno("确认", "是否清空之前的数据？"):
            self.clear_data()

        self.scrape_thread = Thread(target=self.scraper.scrape,
                                    args=(keyword, start_page, end_page, async_count))
        self.scrape_thread.daemon = True
        self.scrape_thread.start()

    def _set_filter_controls_state(self, enabled):
        state = 'normal' if enabled else 'disabled'
        self.filter_apply_btn.config(state=state)
        self.filter_reset_btn.config(state=state)
        self.filter_entry.config(state=state)

    def on_tree_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            url = item['values'][4]
            if url:
                import webbrowser
                webbrowser.open(url)
                self.log_message(f"打开链接: {url}", 'info')

    def save_data(self):
        if not self.all_results:
            messagebox.showwarning("警告", "没有数据可保存！")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("CSV文件", "*.csv")],
            initialfile=f"1688_{self.keyword_entry.get()}_{time.strftime('%Y%m%d_%H%M%S')}"
        )

        if filename:
            try:
                if filename.lower().endswith('.csv'):
                    self.scraper.save_as_csv(self.all_results, filename)
                else:
                    self.scraper.save_as_json(self.all_results, filename)
                self.log_message(f"数据已保存到: {filename}", 'info')
                messagebox.showinfo("成功", f"数据已保存到:\n{filename}")
            except Exception as e:
                self.log_message(f"保存失败: {str(e)}", 'error')
                messagebox.showerror("错误", f"保存文件失败:\n{str(e)}")

    def update_json_view(self):
        if self.is_scraping or (not self.filter_keyword):
            self._display_json_for_data(self.all_results)
            self.progress_count_label.config(text=f"已采集: {len(self.all_results)} 条商品")
        else:
            self.refresh_display()

    def force_refresh_json(self):
        self.refresh_display()
        self.log_message("JSON视图已刷新", 'info')


def main():
    root = tk.Tk()
    app = AlibabaScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()