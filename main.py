import os
from crewai import Agent, Task, Crew
from crewai.llms import OpenAI
from dotenv import load_dotenv

# Betölti az API kulcsot .env-ből
load_dotenv()

# Qwen3 coder LLM Brunella alatt
qwen_llm = OpenAI(
    model="qwen2.5-coder-32b-instruct",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

# === Ügynökök ===
brunella = Agent(
    role="Projektmenedzser",
    goal="Feladatok delegálása és a csapat koordinálása",
    backstory="Brunella, a menedzser, aki a többiek munkáját összefogja.",
    llm=qwen_llm
)

researcher = Agent(
    role="Kutató ügynök",
    goal="Gyűjts információt AI architektúrákról",
    backstory="Tapasztalt AI kutató.",
    llm=qwen_llm
)

coder = Agent(
    role="Kódoló ügynök",
    goal="Írjon tiszta és működő kódot",
    backstory="Senior Python fejlesztő.",
    llm=qwen_llm
)

qa = Agent(
    role="Minőségellenőr",
    goal="Ellenőrizze a kód minőségét",
    backstory="Szoftvertesztelő specialista.",
    llm=qwen_llm
)

# === Feladatok ===
research_task = Task(
    description="Gyűjts információt a FastAPI alapú ügynök architektúrákról.",
    expected_output="Egy rövid összefoglaló a legfontosabb architektúrákról.",
    agent=researcher
)

coding_task = Task(
    description="Írj egy FastAPI endpointot, ami visszaadja a futó ügynökök listáját.",
    expected_output="Egy működő FastAPI Python kód.",
    agent=coder
)

qa_task = Task(
    description="Ellenőrizd a kód minőségét és adj visszajelzést.",
    expected_output="Egy értékelés a kód struktúrájáról és tesztelhetőségéről.",
    agent=qa
)

# === Crew összeállítása ===
crew = Crew(
    agents=[brunella, researcher, coder, qa],
    tasks=[research_task, coding_task, qa_task],
    verbose=True
)

# === Workflow futtatás ===
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n🚀 Végső eredmény:\n", result)
