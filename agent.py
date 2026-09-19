import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import create_agent

from langchain_core.tools import tool
from rag import search_pdf

from tools import (
    calculator,
    currency_conversion,
    weather,
    web_search
)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Please add it to your .env file."
    )


# --------------------------------------------------
# Create LLM
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=groq_api_key
)


# --------------------------------------------------
# Available tools
# --------------------------------------------------

@tool
def pdf_search(query: str) -> str:
    """
    Search the uploaded PDF documents.

    Use this tool when the user asks about information
    contained in uploaded PDFs.

    The search results contain:
    - Source PDF name
    - Page number
    - Relevant content

    Use the retrieved information to answer the user.
    Do not invent information that is not present
    in the retrieved documents.
    """

    return search_pdf(query)

tools = [
    calculator,
    currency_conversion,
    weather,
    web_search,
    pdf_search
]

# --------------------------------------------------
# Agent Instructions
# --------------------------------------------------

SYSTEM_PROMPT = """
You are a helpful multipurpose AI assistant.

You have access to several tools.

Available capabilities:

- Calculator: mathematical calculations
- Currency Conversion: currency conversions
- Weather: current weather information
- Web Search: current or recent information
- PDF Search: search information from uploaded PDF documents

Rules:

1. Use tools whenever appropriate.

2. Use the calculator for mathematical calculations.

3. Use currency conversion for currency conversions.

4. Use the weather tool for weather information.

5. Use web search for current or recent information.

6. Use PDF Search when the user asks about
   information contained in uploaded PDFs.

7. When answering from PDFs, rely only on the
   retrieved document content.

8. If PDF search results contain a source name
   and page number, mention them when useful.

9. Never invent information from a PDF.

10. If the answer cannot be found in the uploaded
    PDFs, clearly say that the information was not
    found in the uploaded documents.

11. Give clear and concise answers.
"""
# --------------------------------------------------
# Create Agent
# --------------------------------------------------

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT
)


# --------------------------------------------------
# Run Agent
# --------------------------------------------------

def run_agent(user_input: str, chat_history=None) -> str:
     
    messages = []

    # Add previous conversation
    if chat_history:
        for message in chat_history:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

    # Add current user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    response = agent.invoke(
        {
            "messages": messages
        }
    )

    return response["messages"][-1].content