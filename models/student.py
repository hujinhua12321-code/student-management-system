"""学生数据模型与仓储（MVC 中的 Model 层）。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Student:
    """学生实体，对应 students 表的一行记录。"""

    student_no: str            # 学号（唯一）
    name: str                  # 姓名
    gender: str = ""           # 性别
    major: str = ""            # 专业
    grade: int = 0             # 年级（如 2022）
    chinese: float = 0.0       # 语文成绩
    math: float = 0.0          # 数学成绩
    english: float = 0.0       # 英语成绩
    id: int | None = None      # 数据库主键，新记录为 None

    @property
    def total_score(self) -> float:
        return round(self.chinese + self.math + self.english, 1)

    @property
    def avg_score(self) -> float:
        return round(self.total_score / 3, 1)


class StudentRepository:
    """学生数据存取层，封装所有 SQL 操作。"""

    COLUMNS = ("id", "student_no", "name", "gender", "major", "grade",
               "chinese", "math", "english")

    def __init__(self, conn):
        self._conn = conn

    # ---------------- 增删改 ----------------
    def add(self, student: Student) -> int:
        """新增学生，返回新记录 id；学号重复时抛出 sqlite3.IntegrityError。"""
        cur = self._conn.execute(
            """INSERT INTO students
               (student_no, name, gender, major, grade, chinese, math, english)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (student.student_no, student.name, student.gender, student.major,
             student.grade, student.chinese, student.math, student.english),
        )
        self._conn.commit()
        return cur.lastrowid

    def update(self, student: Student) -> None:
        """按 id 更新整条记录。"""
        if student.id is None:
            raise ValueError("更新前必须指定记录 id")
        self._conn.execute(
            """UPDATE students
               SET student_no=?, name=?, gender=?, major=?,
                   grade=?, chinese=?, math=?, english=?
               WHERE id=?""",
            (student.student_no, student.name, student.gender, student.major,
             student.grade, student.chinese, student.math, student.english,
             student.id),
        )
        self._conn.commit()

    def delete(self, student_id: int) -> None:
        self._conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        self._conn.commit()

    # ---------------- 查询 ----------------
    def get_by_id(self, student_id: int) -> Student | None:
        row = self._conn.execute(
            f"SELECT {', '.join(self.COLUMNS)} FROM students WHERE id=?",
            (student_id,),
        ).fetchone()
        return self._to_student(row) if row else None

    def list_all(self) -> list[Student]:
        rows = self._conn.execute(
            f"SELECT {', '.join(self.COLUMNS)} FROM students ORDER BY id"
        ).fetchall()
        return [self._to_student(r) for r in rows]

    def search(self, name: str = "", major: str = "",
               min_avg: float | None = None,
               max_avg: float | None = None) -> list[Student]:
        """按姓名 / 专业模糊筛选，并支持平均分区间过滤。"""
        sql = f"SELECT {', '.join(self.COLUMNS)} FROM students WHERE 1=1"
        params: list = []
        if name:
            sql += " AND name LIKE ?"
            params.append(f"%{name}%")
        if major:
            sql += " AND major LIKE ?"
            params.append(f"%{major}%")
        if min_avg is not None:
            sql += " AND (chinese + math + english) / 3.0 >= ?"
            params.append(min_avg)
        if max_avg is not None:
            sql += " AND (chinese + math + english) / 3.0 <= ?"
            params.append(max_avg)
        sql += " ORDER BY id"
        rows = self._conn.execute(sql, params).fetchall()
        return [self._to_student(r) for r in rows]

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    @staticmethod
    def _to_student(row) -> Student:
        return Student(
            id=row["id"], student_no=row["student_no"], name=row["name"],
            gender=row["gender"], major=row["major"], grade=row["grade"],
            chinese=row["chinese"], math=row["math"], english=row["english"],
        )
