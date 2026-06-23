from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GOOGLE_AI_KEY,
)