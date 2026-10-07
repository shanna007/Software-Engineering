import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI兼容接口配置
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
LLM_MODEL = os.getenv("LLM_MODEL", "ep-20261006190540-2vq7z")
TEMPERATURE = 0.3

# Agent运行参数
MAX_ITERATIONS = 15       # Agent最大图递归步数
MAX_RETRY = 3            # LLM接口最大重试次数
