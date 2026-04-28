from dotenv import load_dotenv  # 关键：加载.env
from langchain_openai import ChatOpenAI
import os
from langchain.messages import SystemMessage, HumanMessage, AIMessage

def main():
    # 加载环境变量
    load_dotenv()

    # message可以是字符串/列表/字典, 这里使用列表
    messages = [
        SystemMessage("You are a poetry expert"),
        HumanMessage("Write a haiku about spring"),
        AIMessage("Cherry blossoms bloom...")
    ]

    model = ChatOpenAI(
        temperature=0.6,
        model="glm-4.7-flash",
        openai_api_key=os.getenv("ZAI_API_KEY"),
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
        )
    
    # 查看ai message的元数据, 包括token使用情况
    # response = model.invoke(messages)
    # print(response.usage_metadata)

    # 流式传输,ai message chunk可以组合成完整的ai message
    # chunks = []
    # full_message = None
    # for chunk in model.stream("Hi"):
    #     chunks.append(chunk)
    #     print(chunk.text)
    #     full_message = chunk if full_message is None else full_message + chunk
    # print(full_message)

if __name__ == "__main__":
    main()