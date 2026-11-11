"""控制器层：接收界面事件，校验参数后调用 Model，并把结果反馈给 View。"""
from models.student import Student, StudentRepository

SCORE_FIELDS = (("chinese", "语文"), ("math", "数学"), ("english", "英语"))


class StudentController:
    def __init__(self, repo: StudentRepository):
        self._repo = repo

    # ---------------- 查询 ----------------
    def list_students(self, name: str = "", major: str = "",
                      min_avg=None, max_avg=None):
        """列表查询，参数均为可选筛选条件。"""
        return self._repo.search(name=name, major=major,
                                 min_avg=min_avg, max_avg=max_avg)

    # ---------------- 增删改 ----------------
    def add_student(self, form: dict):
        ok, msg = self._validate(form)
        if not ok:
            return False, msg
        try:
            self._repo.add(self._build(form))
            return True, "添加成功"
        except Exception as exc:  # 主要是学号唯一约束冲突
            return False, f"添加失败：{exc}"

    def update_student(self, student_id: int, form: dict):
        ok, msg = self._validate(form)
        if not ok:
            return False, msg
        try:
            student = self._build(form)
            student.id = student_id
            self._repo.update(student)
            return True, "更新成功"
        except Exception as exc:
            return False, f"更新失败：{exc}"

    def delete_student(self, student_id: int):
        self._repo.delete(student_id)
        return True, "删除成功"

    # ---------------- 内部 ----------------
    @staticmethod
    def _validate(form: dict):
        """表单校验：学号姓名必填，成绩为 0~100 的数字，年级为整数。"""
        if not str(form.get("student_no", "")).strip():
            return False, "学号不能为空"
        if not str(form.get("name", "")).strip():
            return False, "姓名不能为空"
        for key, label in SCORE_FIELDS:
            try:
                score = float(form.get(key) or 0)
            except (TypeError, ValueError):
                return False, f"{label}成绩必须是数字"
            if not 0 <= score <= 100:
                return False, f"{label}成绩必须在 0~100 之间"
            form[key] = score
        try:
            form["grade"] = int(form.get("grade") or 0)
        except (TypeError, ValueError):
            return False, "年级必须是整数"
        return True, ""

    @staticmethod
    def _build(form: dict) -> Student:
        return Student(
            student_no=str(form["student_no"]).strip(),
            name=str(form["name"]).strip(),
            gender=str(form.get("gender", "")).strip(),
            major=str(form.get("major", "")).strip(),
            grade=form["grade"],
            chinese=form["chinese"],
            math=form["math"],
            english=form["english"],
        )
