# 1. Implement the following tools:
# o Weather Tool (Open-Meteo API)
# o Web Search Tool (DuckDuckGo)
# o Currency Converter Tool (Frankfurter API)

#pip3 install langchain-anthropic
#pip3 install python-dotenv
#pip3 install anthropic langchain langchain-anthropic
##pip3 install duckduckgo-search
#pip3 install langchain_google_genai

from agent import agent_with_mcp


def main():
    while True:
        _input = input("\n QQ: ").strip()

        if _input.lower() == 'quit':
            print("👋 Goodbye!")
            break
        if _input:
            try:
                response = agent_with_mcp(_input)
                print(f"\n✅ Answer: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("Please enter a valid question.")



if __name__ == "__main__":
    main()