import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取环境变量
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 验证 API key
if OPENAI_API_KEY:
    print("API key loaded successfully")
    print(f"API key starts with: {OPENAI_API_KEY[:10]}...")  # 只显示前10个字符
    if OPENAI_API_KEY == 'your-api-key-here':
        print("Warning: Using default API key value!")
else:
    print("Warning: OPENAI_API_KEY not found in environment variables") 