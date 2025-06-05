from common.fallback import fallback_match_agents
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage

def main():

    llm = ChatOllama(model="llama3.2")  # You can also use "mistral", "phi", etc.

    response = llm([
        HumanMessage(content="List 3 applications of multi-agent systems in finance.")
    ])

    print(response.content)

if __name__ == "__main__":
    main()
