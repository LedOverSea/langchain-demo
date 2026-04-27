import langchain
from langchain.agents import create_agent
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv  # 关键：加载.env
from langchain.tools import tool
from pydantic import BaseModel
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
import langchain.chat_models.ChatZhipuAI


def main():
    # print(langchain.__version__)

    # 加载环境变量
    load_dotenv()

    """ model = ChatOpenAI(
        temperature=0.6,
        model="glm-4.7-flash",
        openai_api_key=os.getenv("ZAI_API_KEY"),
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    ) """
    model = init_chat_model("glm-4.7-flash", model_provider="ZhipuAI")

    
    

if __name__ == "__main__":
    main()
