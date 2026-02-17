from tools import tools_list


def mcp_layer(user_input: str) -> dict:
    query = user_input.lower()
    for tool in tools_list:
        if any(word.lower() in query for word in tool["keywords"]):
            return {
                "tool": tool["name"],
                "tool_input": user_input,
                "tool_func": tool["func"],
                "answer_direct": None
            }
    return {
        "tool": None,
        "tool_input": None,
        "tool_func": None,
        "answer_direct": f"I'm sorry, I don't have a specific tool for that. I can answer directly: {user_input}"
    }

