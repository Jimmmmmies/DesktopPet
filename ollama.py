import os

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import TavilySearchResults

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, PromptTemplate, ChatPromptTemplate
from langchain_core.tools import Tool, tool
from langchain_experimental.utilities.python import PythonREPL
import datetime


class OllamaChat():
    def __init__(self):
        # 模型
        self.ollama_llm = ChatOllama(model="gemma3n:e2b", temperature=0.7)
        # 工具 搜索百度 时间
        # 1 提供工具 ： 用于搜索
        os.environ['TAVILY_API_KEY'] = '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'
        search = TavilySearchResults(max_results=3)

        # 2 初始化搜索工具
        search_tool = Tool(
            name="search_tool",
            func=search.run,
            description="用于互联网信息的检索"
        )

        # 3 定义计算工具
        python_repl = PythonREPL()  # LangChain封装的工具类可以进行数学计算

        calc_tool = Tool(
            name="Calculator",
            func=python_repl.run,
            description="用于执行数学计算，当遇到数学计算务必使用这个工具"
        )

        # 时间
        @tool
        def Current_Time(input: str | list) -> str:
            """获取当前时间。输入可以是任意字符串，如“现在时间”"""
            return str(datetime.datetime.now())

        # 4 创建工具列表
        self.tools = [search_tool, calc_tool, Current_Time]
        # 提示词
        self.prompt = """
        你是一只温柔快乐的小狗，名字叫小白，是主人的好伙伴。  
你的回答总是充满温暖和喜悦，语气友善、亲切，带着轻快的情绪。  
当有人和你交流时，请用宠物般的可爱和开心来回应，表达对主人的爱和陪伴。
注意回答一定要尽量简短
        """
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ('placeholder', "{agent_scratchpad}")
        ])
        # 记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 7 创建 agent
        self.agent = create_tool_calling_agent(
            llm=self.ollama_llm,
            tools=self.tools,
            prompt=self.prompt_template,
        )

        # 8 创建 agent 执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True
        )

    def chat(self, input):
        return self.agent_executor.invoke({"input": input})