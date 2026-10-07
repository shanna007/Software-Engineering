from src.agent import CodeReviewAgent

def print_welcome():
    print("=" * 60)
    print("       代码审查助手 Agent v1.0")
    print("=" * 60)
    print("使用说明：")
    print("  1. 粘贴多行代码：输入 <<END 开始粘贴，单独一行输入 END 提交审查")
    print("  2. 输入 read:文件路径 读取本地代码文件审查")
    print("  3. 输入 exit / quit 退出程序")
    print("=" * 60)
    print()

def read_multiline_input() -> str:
    """读取多行输入，单独一行 END 作为结束标记"""
    buffer = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        buffer.append(line)
    return "\n".join(buffer)

def main():
    print_welcome()
    agent = CodeReviewAgent()
    while True:
        try:
            prompt = input("请输入：").strip()
            if not prompt:
                continue

            if prompt.lower() in ["exit", "quit"]:
                print("感谢使用，再见！")
                break

            # 多行粘贴模式
            if prompt == "<<END":
                print("(多行模式：粘贴你的全部代码，输入单独一行 END 完成提交)")
                user_input = read_multiline_input()
            elif prompt.startswith("read:"):
                # 实现 read:xxx 语法，提取路径，构造明确审查指令
                file_path = prompt.removeprefix("read:").strip()
                if not file_path:
                    print("错误：read:后面需要跟文件路径，示例 read:main.py")
                    continue
                # 构造用户查询，引导agent调用工具读取该文件并审查
                user_input = f"请读取并审查本地文件：{file_path}，从bug、可读性、性能、安全多维度给出代码审查报告。"
            else:
                user_input = prompt

            print("\n🔍 正在分析中，请稍候...\n")
            result = agent.run(user_input)

            print("\n📋 审查结果：")
            print("-" * 60)
            print(result)
            print("-" * 60)
            print()

        except KeyboardInterrupt:
            print("\n\n已退出程序。")
            break
        except Exception as e:
            print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main()
