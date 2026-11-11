# 学生信息管理系统

基于 **Python + Tkinter + SQLite** 的桌面端学生信息管理系统，采用 **MVC 架构** 分离界面、业务逻辑与数据存取。

## 功能特性

- **增删改查**：学生信息（学号、姓名、性别、专业、年级）的完整管理
- **成绩管理**：语文 / 数学 / 英语三科成绩录入，自动计算总分与平均分
- **条件筛选**：按姓名、专业模糊查询，支持平均分区间过滤
- **数据持久化**：SQLite 本地存储，学号唯一约束防止重复录入
- **输入校验**：成绩范围 0~100、必填项等表单校验

## 技术栈

| 模块   | 技术            |
| ------ | --------------- |
| GUI    | Tkinter（ttk）  |
| 数据库 | SQLite3         |
| 架构   | MVC             |
| 测试   | unittest        |

## 项目结构

```
student-management-system/
├── main.py                        # 入口：组装 MVC 并启动
├── models/                        # Model 层
│   ├── database.py                # SQLite 连接与建表
│   └── student.py                 # Student 实体 + 仓储（CRUD/筛选）
├── views/
│   └── main_window.py             # View 层：Tkinter 主窗口
├── controllers/
│   └── student_controller.py      # Controller 层：事件分发与校验
└── tests/
    └── test_repository.py         # Model 层单元测试（内存数据库）
```

## 快速开始

环境要求：Python 3.8+（仅使用标准库，无需安装依赖）

```bash
# 启动系统
python main.py

# 运行单元测试
python -m unittest discover -s tests -v
```

首次启动会在项目根目录自动创建 `students.db` 数据文件。
