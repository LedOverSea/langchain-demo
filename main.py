from dotenv import load_dotenv  # 关键：加载.env
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os

# 加载环境变量
load_dotenv()

model = ChatOpenAI(
    temperature=0.6,
    model="glm-4.7-flash",
    openai_api_key=os.getenv("ZAI_API_KEY"),
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )