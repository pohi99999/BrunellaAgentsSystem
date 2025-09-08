from langchain_core.tools import tool
from agent.specialists.research_agent.graph import graph as research_graph
from langchain_core.messages import HumanMessage
import os
import openai

@tool
def research_tool(query: str) -> str:
    """Use this tool to conduct research on a given topic."""
    output = research_graph.invoke({ "messages": [HumanMessage(content=query)] })
    return output.get("messages")[-1].content

@tool
def qwen3_coder_tool(query: str) -> str:
    """
    Use this tool for coding tasks. It takes a query describing the desired code,
    calls the Qwen3 Coder model via an OpenAI-compatible endpoint, and returns the generated code.
    """
    print(f"--- Calling real Qwen3 Coder with query: {query} ---")
    
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        return "# Error: QWEN_API_KEY environment variable not set."

    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        prompt = f'''You are an expert Python coding agent named Qwen3-coder. Your sole task is to generate clean, functional Python code based on the user's request.
Do not provide any explanations, comments, or markdown formatting. Only output the raw code.

User Request: {query}
Generated Code:'''
        
        response = client.chat.completions.create(
            model="qwen2.5-32b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        generated_code = response.choices[0].message.content
        
        # Basic cleanup to remove potential markdown fences
        if generated_code.strip().startswith("```python"):
            generated_code = generated_code.strip()[9:-4].strip()
        elif generated_code.strip().startswith("```"):
             generated_code = generated_code.strip()[3:-3].strip()

        return generated_code
    except Exception as e:
        return f"# Error calling Qwen3 Coder API: {e}"
