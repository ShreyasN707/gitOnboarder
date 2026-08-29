import asyncio
from langchain_core.messages import HumanMessage

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from app.config import GOOGLE_API_KEY
from app.rag_tool import search_repository
from app.prompt import SYSTEM_PROMPT
from app.memory_tools import store_repository_memory, get_repository_memory


async def main():

    model = init_chat_model(
        "google_genai:gemini-3.6-flash",
        temperature=0,
        max_output_tokens=2096,
    )

    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "stdio",
                "command": "python",
                "args": [
                    "mcp_server/github_server.py"
                ],
            }
        }
    )

    tools = await client.get_tools()
    
    # Add our local tools to the tools list
    tools.append(search_repository)
    tools.append(store_repository_memory)
    tools.append(get_repository_memory)

    print("Available tools:")
    for tool in tools:
        print("-", tool.name)

    # Add short-term conversational memory using LangGraph's MemorySaver
    memory = MemorySaver()
    
    agent = create_agent(
        model,
        tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory
    )

    # We use a static thread_id for the session to persist short-term memory
    config = {"configurable": {"thread_id": "session_1"}}

    print("\\nGitHub Repository Intelligence Agent Ready!")
    print("Type 'exit' or 'quit' to end the session.\\n")

    while True:
        try:
            user_input = input("User:\\n> ")
            if user_input.strip().lower() in ['exit', 'quit']:
                break
                
            if not user_input.strip():
                continue

            response = await agent.ainvoke({
                "messages": [
                    HumanMessage(content=user_input)
                ]
            }, config=config)
            
            # The agent returns the full message list, so we grab the last message
            last_message = response["messages"][-1]
            
            print("\\nAgent:")
            if isinstance(last_message.content, list):
                # Sometimes complex messages return a list of content blocks
                for block in last_message.content:
                    if isinstance(block, dict) and 'text' in block:
                        print(block['text'])
                    elif isinstance(block, str):
                        print(block)
            else:
                print(last_message.content)
            print("\\n" + "-"*50 + "\\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\\nError: {e}\\n")

if __name__ == "__main__":
    asyncio.run(main())