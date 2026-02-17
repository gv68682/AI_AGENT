#from langchain_anthropic import ChatAnthropic
#from langchain.llms import AmazonBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

#model="claude-3-sonnet-20240229",
#Ilgmars/deepseek-ai-DeepSeek-R1-0528
# model="aws-prototyping/MegaBeam-Mistral-7B-512k"
load_dotenv()
api_key=os.getenv("GOOGLE_APIKEY")
os.environ["GOOGLE_API_KEY"] = api_key

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", #gemini-2.5-pro
    temperature=0.3,
    convert_system_message_to_human=True
)



# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
