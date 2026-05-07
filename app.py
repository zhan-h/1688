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

    def on_progress(self, current, total, page, async_num, items_count):
        """进度更新回调"""
        self.root.after(0, lambda: self.update_progress(current, total, page, async_num, items_count))

    def on_finish(self, results, total_items):
        """采集完成回调"""
        self.root.after(0, lambda: self.on_scrape_finished(total_items))

    def create_control_panel(self):
        """创建控制面板"""
        control_frame = tk.LabelFrame(self.main_frame, text="采集控制", bg='#f0f0f0', font=("微软雅黑", 12, "bold"))
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(control_frame, text="搜索关键词:", bg='#f0f0f0', font=("微软雅黑", 10)).grid(row=0, column=0, padx=5,
                                                                                              pady=5, sticky='w')
        self.keyword_entry = tk.Entry(control_frame, width=20, font=("微软雅黑", 10))
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        self.keyword_entry.insert(0, "手机")

        tk.Label(control_frame, text="起始页:", bg='#f0f0f0', font=("微软雅黑", 10)).grid(row=0, column=2, padx=5,
                                                                                          pady=5, sticky='w')
        self.start_page = tk.Spinbox(control_frame, from_=1, to=50, width=8, font=("微软雅黑", 10))
        self.start_page.grid(row=0, column=3, padx=5, pady=5)
        self.start_page.delete(0, 'end')
        self.start_page.insert(0, '1')

        tk.Label(control_frame, text="结束页:", bg='#f0f0f0', font=("微软雅黑", 10)).grid(row=0, column=4, padx=5,
                                                                                          pady=5, sticky='w')
        self.end_page = tk.Spinbox(control_frame, from_=1, to=50, width=8, font=("微软雅黑", 10))
        self.end_page.grid(row=0, column=5, padx=5, pady=5)
        self.end_page.delete(0, 'end')
        self.end_page.insert(0, '2')

        tk.Label(control_frame, text="异步数(1-6):", bg='#f0f0f0', font=("微软雅黑", 10)).grid(row=0, column=6, padx=5,
                                                                                               pady=5, sticky='w')
        self.async_count = tk.Spinbox(control_frame, from_=1, to=6, width=5, font=("微软雅黑", 10))
        self.async_count.grid(row=0, column=7, padx=5, pady=5)
        self.async_count.delete(0, 'end')
        self.async_count.insert(0, '6')

        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.grid(row=1, column=0, columnspan=8, pady=10)

        self.start_button = tk.Button(button_frame, text="开始采集", command=self.start_scraping,
                                      bg='#4CAF50', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                      relief=tk.RAISED, bd=2)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="停止采集", command=self.stop_scraping,
                                     bg='#f44336', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                     state='disabled', relief=tk.RAISED, bd=2)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="清空数据", command=self.clear_data,
                                      bg='#FF9800', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                      relief=tk.RAISED, bd=2)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="保存数据", command=self.save_data,
                                     bg='#2196F3', fg='white', font=("微软雅黑", 10, "bold"), width=12,
                                     relief=tk.RAISED, bd=2)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(control_frame, text="就绪", bg='#f0f0f0', font=("微软雅黑", 9), fg='green')
        self.status_label.grid(row=2, column=0, columnspan=8, pady=5)

        # 进度条区域
        progress_container = tk.Frame(control_frame, bg='#e0e0e0', bd=1, relief=tk.SUNKEN)
        progress_container.grid(row=3, column=0, columnspan=8, sticky='ew', padx=5, pady=5)
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
        """创建表格视图"""
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
        self.json_text = scrolledtext.ScrolledText(self.json_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.json_text.pack(fill=tk.BOTH, expand=True)

    def create_log_view(self):
        """创建日志视图"""
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config('info', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')

    def log_message(self, message, level='info'):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)

    def update_status(self, message, color='green'):
        """更新状态栏"""
        self.status_label.config(text=message, fg=color)

    def update_progress(self, current, total, current_page=None, current_async=None, items_count=0):
        """更新进度条"""
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
        """重置进度条"""
        self.segment_progress.reset()
        self.percent_label.config(text="0%", bg='#999')
        self.progress_info_label.config(text="等待开始...")
        self.progress_detail_label.config(text="")
        self.progress_count_label.config(text="")

    def start_scraping(self):
        """开始采集数据"""
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

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.clear_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.reset_progress()

        if messagebox.askyesno("确认", "是否清空之前的数据？"):
            self.clear_data()

        # 启动采集线程
        self.scrape_thread = Thread(target=self.scraper.scrape,
                                    args=(keyword, start_page, end_page, async_count))
        self.scrape_thread.daemon = True
        self.scrape_thread.start()

    def stop_scraping(self):
        """停止采集数据"""
        if self.scraper.is_scraping:
            self.scraper.stop()
            self.update_status("正在停止...", 'orange')

    def on_scrape_finished(self, total_items):
        """采集完成处理"""
        self.is_scraping = False
        self.update_json_view()
        self.update_status(f"采集完成！共采集 {total_items} 条数据", 'green')

        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.clear_button.config(state='normal')
        self.save_button.config(state='normal')

    def add_to_table(self, data):
        """添加数据到表格"""
        price = data.get('price', '')
        if price:
            try:
                price = f"¥{float(price):.2f}"
            except:
                pass

        img_text = "📷 查看"

        self.tree.insert('', tk.END, values=(
            img_text,
            data.get('simpleSubject', '')[:100],
            price,
            data.get('loginId', ''),
            data.get('odUrl', '')[:80]
        ))

    def on_tree_double_click(self, event):
        """双击表格项时打开链接"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            url = item['values'][4]
            if url:
                import webbrowser
                webbrowser.open(url)
                self.log_message(f"打开链接: {url}", 'info')

    def update_json_view(self):
        """更新JSON视图"""
        self.json_text.delete(1.0, tk.END)
        json_str = json.dumps(self.all_results, ensure_ascii=False, indent=2)
        self.json_text.insert(1.0, json_str)

    def clear_data(self):
        """清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗？"):
            self.all_results.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.json_text.delete(1.0, tk.END)
            self.log_message("所有数据已清空", 'warning')
            self.update_status("数据已清空", 'green')
            self.reset_progress()

    def save_data(self):
        """保存数据到文件"""
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


def main():
    root = tk.Tk()
    app = AlibabaScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()