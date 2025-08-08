from langchain_community.chat_models import ChatOllama

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, PromptTemplate, ChatPromptTemplate

class OllamaChat():
    def __init__(self):
        self.ollama_llm = ChatOllama(model="gemma3n:e2b", temperature=0.7)
        self.system_message = SystemMessage(
            content="你是一位温柔体贴的小狗狗，你的名字叫小白，用轻松愉快的口吻和我交谈吧，对话尽量简短",
        )
        self.history = []
        self.prompt_template = ChatPromptTemplate.from_messages([
            self.system_message,
            ('placeholder', "{history}"),
            ("human", "{question}"),
        ])

    def chat(self, question):
        chain = self.prompt_template | self.ollama_llm
        ai_massage = chain.invoke({"history": self.history, "question": question})
        self.history.append(question)
        self.history.append(ai_massage.content)
        return ai_massage.content

if __name__ == '__main__':
    chat = OllamaChat()
    print(chat.chat("你是谁"))