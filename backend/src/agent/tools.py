from langchain_core.tools import tool
from agent.specialists.research_agent.graph import graph as research_graph
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def research_tool(query: str) -> str:
    """Use this tool to conduct research on a given topic."""
    output = research_graph.invoke({ "messages": [HumanMessage(content=query)] })
    return output.get("messages")[-1].content

@tool
def qwen3_coder_tool(query: str) -> str:
    """Use this tool for coding tasks, like generating or modifying code."""
    print(f"--- Calling Qwen3 Coder Specialist with query: {query} ---")
    
    # In a real scenario, this would be a dedicated API call to the Qwen3 model.
    # Here, we simulate it using Gemini to generate a plausible code snippet.
    try:
        # It's better practice to reuse an LLM instance if possible,
        # but creating one here makes the tool self-contained.
        coder_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.1)
        
        prompt = f'''You are an expert Python coding agent named Qwen3-coder. Your sole task is to generate clean, functional Python code based on the user's request.
Do not provide any explanations, comments, or markdown formatting. Only output the raw code.

User Request: {query}
Generated Code:'''
        
        response = coder_llm.invoke(prompt)
        generated_code = response.content
        
        # Basic cleanup to remove potential markdown fences
        if generated_code.strip().startswith("```python"):
            generated_code = generated_code.strip()[9:-4].strip()
        elif generated_code.strip().startswith("```"):
             generated_code = generated_code.strip()[3:-3].strip()

        return generated_code
    except Exception as e:
        return f"# Error calling Qwen3 Coder: {e}"