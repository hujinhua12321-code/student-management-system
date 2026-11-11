"""学生信息管理系统入口：组装 MVC 并启动界面。"""
from controllers.student_controller import StudentController
from models.database import get_connection, init_db
from models.student import StudentRepository
from views.main_window import MainWindow


def main():
    conn = get_connection()
    init_db(conn)
    controller = StudentController(StudentRepository(conn))
    app = MainWindow(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
