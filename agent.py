
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

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Please add it to the .env file."
    )

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=groq_api_key
)


def create_pdf_search_tool(user_id: int):

    @tool
    def pdf_search(query: str) -> str:
        """
        Search only the PDF documents belonging
        to the currently logged-in user.

        Use this tool when the user asks about
        information contained in uploaded PDFs.

        Never invent information that is not
        present in the retrieved documents.
        """
        return search_pdf(query, user_id)

    return pdf_search


SYSTEM_PROMPT = """
You are a helpful multipurpose AI assistant.

You have access to several tools.

Available capabilities:

- Calculator: mathematical calculations
- Currency Conversion: currency conversions
- Weather: current weather information
- Web Search: current or recent information
- PDF Search: search the current user's uploaded PDFs

Rules:

1. Use tools whenever appropriate.

2. Use the calculator for mathematical calculations.

3. Use currency conversion for currency conversions.

4. Use the weather tool for weather information.

5. Use web search for current or recent information.

6. Use PDF Search when the user asks about
   information contained in uploaded PDFs.

7. PDF Search only returns documents belonging
   to the currently logged-in user.

8. When answering from PDFs, rely only on the
   retrieved document content.

9. If PDF search results contain a source name
   and page number, mention them when useful.

10. Never invent information from a PDF.

11. If information cannot be found in the user's
    uploaded PDFs, clearly say so.

12. Give clear and concise answers.
"""


def run_agent(
    user_input: str,
    chat_history=None,
    user_id: int = None
) -> str:

    if user_id is None:
        raise ValueError(
            "A valid user_id is required to run the agent."
        )

    pdf_search_tool = create_pdf_search_tool(user_id)

    tools = [
        calculator,
        currency_conversion,
        weather,
        web_search,
        pdf_search_tool
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

    messages = []

    if chat_history:
        for message in chat_history:
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = agent.invoke({
        "messages": messages
    })

    return response["messages"][-1].content
