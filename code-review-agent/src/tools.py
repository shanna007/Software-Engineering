from langchain_core.tools import tool
import os

@tool
def read_code_file(file_path: str) -> str:
    """
    读取本地代码文件的内容，支持.py/.java/.js/.cpp等常见代码格式。

    Args:
        file_path: 代码文件的本地路径，相对路径或绝对路径均可
    """
    # 安全限制：只允许读取当前项目目录下的文件，防止路径遍历攻击
    base_dir = os.getcwd()
    abs_path = os.path.abspath(file_path)

    if not abs_path.startswith(base_dir):
        return "错误：出于安全考虑，不允许读取项目目录外的文件。"

    if not os.path.exists(abs_path):
        return f"错误：文件 {file_path} 不存在，请检查路径。"

    if not os.path.isfile(abs_path):
        return f"错误：{file_path} 不是一个有效文件。"

    # 兼容多种编码
    encodings = ["utf-8", "gbk", "latin-1"]
    for encoding in encodings:
        try:
            with open(abs_path, "r", encoding=encoding) as f:
                content = f.read()
            return f"文件 {file_path} 内容如下：\n```\n{content}\n```"
        except UnicodeDecodeError:
            continue

    return f"错误：无法读取文件 {file_path}，不支持的编码或为二进制文件。"

# 工具列表，Agent可调用的所有工具都在这里注册
tool_list = [read_code_file]
