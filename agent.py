from langchain.agents import  AgentExecutor, create_react_agent
from llm import llm
from prompts import react_prompt
from tools import tools
weather_tool, websearch_tool,currency_tool=tools
from mcp import mcp_layer


def create_agent():
    # === Create ReAct Agent ===
    agent = create_react_agent(
        llm=llm,
        tools=[weather_tool,websearch_tool, currency_tool],
        prompt=react_prompt
    )
    return agent

agent=create_agent()

# === Create Agent Executor ===
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)


#Python does NOT have block scope for if, for, while, etc.
# routed_input is available outside the if block because Python only has:
# Function scope, Class scope, Module scope
# In JS block scope will be created if the variable declared with let or const
def agent_with_mcp(user_input: str ):
    decision = mcp_layer(user_input)
    if decision["tool"]:
       #[] Not Python syntax, Not creating a list, Not special to f-strings, Just literal characters included in the output string
       # Why Use Square Brackets? They are just being used as a marker or tag.
       #It’s likely your agent is designed to detect something like: "[Use search] Find weather"
        routed_input = f"[Use {decision['tool']}] {user_input}"
    else:
        routed_input = user_input
    # Use invoke instead of run
    result = agent_executor.invoke({"input": routed_input})
    return result.get("output", "")





