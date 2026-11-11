"""Model 层单元测试（使用内存数据库，不污染本地数据文件）。

运行方式：python -m unittest discover -s tests -v
"""
import unittest

from models.database import get_connection, init_db
from models.student import Student, StudentRepository


def make_student(no="2022001", name="张三", **kwargs):
    defaults = dict(gender="男", major="软件工程", grade=2022,
                    chinese=80.0, math=90.0, english=85.0)
    defaults.update(kwargs)
    return Student(student_no=no, name=name, **defaults)


class StudentRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.repo = StudentRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_add_and_get(self):
        sid = self.repo.add(make_student())
        s = self.repo.get_by_id(sid)
        self.assertEqual(s.name, "张三")
        self.assertEqual(s.total_score, 255.0)
        self.assertEqual(s.avg_score, 85.0)

    def test_update(self):
        sid = self.repo.add(make_student())
        s = self.repo.get_by_id(sid)
        s.name = "李四"
        s.math = 100.0
        self.repo.update(s)
        updated = self.repo.get_by_id(sid)
        self.assertEqual(updated.name, "李四")
        self.assertEqual(updated.math, 100.0)

    def test_delete(self):
        sid = self.repo.add(make_student())
        self.repo.delete(sid)
        self.assertIsNone(self.repo.get_by_id(sid))

    def test_search_by_name_and_major(self):
        self.repo.add(make_student(no="1", name="张三", major="软件工程"))
        self.repo.add(make_student(no="2", name="张四", major="计算机科学"))
        self.repo.add(make_student(no="3", name="王五", major="软件工程"))
        self.assertEqual(len(self.repo.search(name="张")), 2)
        self.assertEqual(len(self.repo.search(major="软件")), 2)
        self.assertEqual(len(self.repo.search(name="张", major="计算机")), 1)

    def test_search_by_avg_range(self):
        self.repo.add(make_student(no="1", chinese=60, math=60, english=60))
        self.repo.add(make_student(no="2", chinese=90, math=90, english=90))
        self.assertEqual(len(self.repo.search(min_avg=80)), 1)
        self.assertEqual(len(self.repo.search(max_avg=70)), 1)
        self.assertEqual(len(self.repo.search(min_avg=50, max_avg=100)), 2)

    def test_duplicate_student_no_rejected(self):
        self.repo.add(make_student())
        with self.assertRaises(Exception):
            self.repo.add(make_student())


if __name__ == "__main__":
    unittest.main()
