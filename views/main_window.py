"""Tkinter 图形界面（MVC 中的 View 层）。

布局：顶部条件筛选区 / 中部记录列表 / 底部编辑表单。
View 不直接访问数据库，全部通过 Controller 交互。
"""
import tkinter as tk
from tkinter import messagebox, ttk

FORM_FIELDS = (
    ("student_no", "学号"), ("name", "姓名"), ("gender", "性别"), ("major", "专业"),
    ("grade", "年级"), ("chinese", "语文"), ("math", "数学"), ("english", "英语"),
)
TABLE_COLUMNS = (
    ("student_no", "学号", 100), ("name", "姓名", 80), ("gender", "性别", 50),
    ("major", "专业", 150), ("grade", "年级", 60), ("chinese", "语文", 60),
    ("math", "数学", 60), ("english", "英语", 60), ("total", "总分", 70),
    ("avg", "平均分", 70),
)


class MainWindow(tk.Tk):
    """系统主窗口。"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._selected_id = None

        self.title("学生信息管理系统")
        self.geometry("980x600")
        self.minsize(880, 540)

        self._build_search_bar()
        self._build_table()
        self._build_form()
        self.refresh_table()

    # ---------------- 界面搭建 ----------------
    def _build_search_bar(self):
        bar = ttk.LabelFrame(self, text="条件筛选")
        bar.pack(fill="x", padx=10, pady=(10, 4))

        ttk.Label(bar, text="姓名").pack(side="left", padx=(8, 2))
        self.search_name = ttk.Entry(bar, width=10)
        self.search_name.pack(side="left")

        ttk.Label(bar, text="专业").pack(side="left", padx=(8, 2))
        self.search_major = ttk.Entry(bar, width=12)
        self.search_major.pack(side="left")

        ttk.Label(bar, text="平均分").pack(side="left", padx=(8, 2))
        self.search_min = ttk.Entry(bar, width=5)
        self.search_min.pack(side="left")
        ttk.Label(bar, text="~").pack(side="left")
        self.search_max = ttk.Entry(bar, width=5)
        self.search_max.pack(side="left")

        ttk.Button(bar, text="查询", command=self.refresh_table).pack(side="left", padx=8)
        ttk.Button(bar, text="重置", command=self._reset_search).pack(side="left")

    def _build_table(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=4)

        columns = [c[0] for c in TABLE_COLUMNS]
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for key, text, width in TABLE_COLUMNS:
            self.table.heading(key, text=text)
            self.table.column(key, width=width, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self._on_select)

    def _build_form(self):
        form = ttk.LabelFrame(self, text="信息编辑")
        form.pack(fill="x", padx=10, pady=(4, 10))

        self.inputs = {}
        for i, (key, label) in enumerate(FORM_FIELDS):
            row, col = divmod(i, 4)
            ttk.Label(form, text=label).grid(
                row=row, column=col * 2, sticky="e", padx=(8, 2), pady=4)
            entry = ttk.Entry(form, width=12)
            entry.grid(row=row, column=col * 2 + 1, sticky="w", padx=(0, 8), pady=4)
            self.inputs[key] = entry

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=8, pady=(6, 2))
        ttk.Button(btns, text="添加", command=self._on_add).pack(side="left", padx=6)
        ttk.Button(btns, text="更新选中", command=self._on_update).pack(side="left", padx=6)
        ttk.Button(btns, text="删除选中", command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(btns, text="清空表单", command=self._clear_form).pack(side="left", padx=6)

    # ---------------- 事件处理 ----------------
    def refresh_table(self):
        """按当前筛选条件刷新列表。"""
        students = self.controller.list_students(
            name=self.search_name.get().strip(),
            major=self.search_major.get().strip(),
            min_avg=self._parse_score(self.search_min.get()),
            max_avg=self._parse_score(self.search_max.get()),
        )
        self.table.delete(*self.table.get_children())
        for s in students:
            self.table.insert("", "end", iid=str(s.id), values=(
                s.student_no, s.name, s.gender, s.major, s.grade,
                s.chinese, s.math, s.english, s.total_score, s.avg_score,
            ))
        self.title(f"学生信息管理系统（共 {len(students)} 条记录）")

    def _on_select(self, _event=None):
        """选中列表记录后回填表单。"""
        selected = self.table.selection()
        if not selected:
            return
        self._selected_id = int(selected[0])
        values = self.table.item(selected[0], "values")
        for (key, _), value in zip(FORM_FIELDS, values):
            self.inputs[key].delete(0, "end")
            self.inputs[key].insert(0, value)

    def _on_add(self):
        ok, msg = self.controller.add_student(self._read_form())
        self._show_result(ok, msg)

    def _on_update(self):
        if self._selected_id is None:
            messagebox.showwarning("提示", "请先在列表中选中一条记录")
            return
        ok, msg = self.controller.update_student(self._selected_id, self._read_form())
        self._show_result(ok, msg)

    def _on_delete(self):
        if self._selected_id is None:
            messagebox.showwarning("提示", "请先在列表中选中一条记录")
            return
        if messagebox.askyesno("确认", "确定删除选中的学生记录吗？"):
            ok, msg = self.controller.delete_student(self._selected_id)
            self._show_result(ok, msg)

    # ---------------- 工具方法 ----------------
    def _read_form(self):
        return {key: entry.get() for key, entry in self.inputs.items()}

    def _clear_form(self):
        for entry in self.inputs.values():
            entry.delete(0, "end")
        self._selected_id = None
        selection = self.table.selection()
        if selection:
            self.table.selection_remove(selection)

    def _reset_search(self):
        for entry in (self.search_name, self.search_major,
                      self.search_min, self.search_max):
            entry.delete(0, "end")
        self.refresh_table()

    def _show_result(self, ok, msg):
        if ok:
            self._clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("错误", msg)

    @staticmethod
    def _parse_score(text):
        text = text.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
