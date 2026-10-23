"""受限的测试运行器。

安全边界说明：
- 仅允许测试代码导入 unittest 及常见纯计算标准库。
- 静态检查是风险筛查，不是真正的安全沙箱。
- 子进程超时限制可以防止部分意外死循环，但不能隔离操作系统权限。
- 仅运行自己信任并审查过的生成代码；更强隔离应使用容器/虚拟机。
"""
import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ALLOWED_IMPORTS = {
    "unittest", "generated_code", "math", "json", "datetime", "collections",
    "re", "statistics", "string", "itertools", "functools",
    "typing", "decimal", "enum", "dataclasses","hashlib",
}
FORBIDDEN_CALLS = {
    "eval", "exec", "compile", "__import__", "open",
    "input", "breakpoint",
}
FORBIDDEN_NAMES = {
    "os", "sys", "subprocess", "socket", "requests", "urllib",
    "shutil", "pathlib", "importlib", "ctypes", "multiprocessing",
}


class UnsafeCodeError(ValueError):
    pass


def _check_ast(source: str, label: str, is_test: bool = False):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError(f"{label}存在语法错误：{exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".")[0] for alias in node.names]
            else:
                modules = [(node.module or "").split(".")[0]]
            for module in modules:
                if module and module not in ALLOWED_IMPORTS:
                    raise UnsafeCodeError(
                        f"{label}包含不在允许列表中的导入：{module}"
                    )

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                raise UnsafeCodeError(
                    f"{label}包含受限调用：{node.func.id}"
                )

        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise UnsafeCodeError(
                f"{label}引用了受限模块/名称：{node.id}"
            )

        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise UnsafeCodeError(
                f"{label}包含双下划线属性访问，拒绝运行。"
            )

    if is_test:
        # 测试代码必须使用 unittest，避免执行任意脚本式测试。
        if not any(
            isinstance(node, ast.Import)
            and any(alias.name == "unittest" for alias in node.names)
            for node in ast.walk(tree)
        ) and not any(
            isinstance(node, ast.ImportFrom) and node.module == "unittest"
            for node in ast.walk(tree)
        ):
            raise UnsafeCodeError("测试代码必须使用 unittest。")

    return tree


def run_unittest(source_code: str, test_code: str, timeout: int = 10) -> dict:
    """检查并在临时目录中执行 unittest，返回结构化测试报告。"""
    _check_ast(source_code, "生成的应用代码")
    _check_ast(test_code, "生成的测试代码", is_test=True)

    with tempfile.TemporaryDirectory(prefix="mini_se_test_") as temp:
        workdir = Path(temp)
        (workdir / "generated_code.py").write_text(
            source_code, encoding="utf-8"
        )
        (workdir / "test_generated.py").write_text(
            test_code, encoding="utf-8"
        )

        # 使用干净环境并设置超时。此举不等同于 OS 级安全沙箱。
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        runner = (
            "import sys, unittest; "
            "sys.path.insert(0, '.'); "
            "suite = unittest.defaultTestLoader.discover('.', pattern='test_generated.py'); "
            "result = unittest.TextTestRunner(verbosity=2).run(suite); "
            "sys.exit(0 if result.wasSuccessful() else 1)"
        )

        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", runner],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            passed = completed.returncode == 0
            return {
                "status": "passed" if passed else "failed",
                "return_code": completed.returncode,
                "stdout": completed.stdout[-12000:],
                "stderr": completed.stderr[-12000:],
                "timeout_seconds": timeout,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "timeout",
                "return_code": None,
                "stdout": str(exc.stdout or "")[-4000:],
                "stderr": str(exc.stderr or "")[-4000:],
                "timeout_seconds": timeout,
            }
