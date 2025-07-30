
import re
import io
import contextlib
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

# Initialise le modèle local
llm = ChatOllama(model="codellama:python", temperature=0.5)

AGENT_PROMPT = """
You are a Python agent. When asked a question, you must always respond only with executable Python code, without any comments or explanations.

Do not include any text outside the code.
The code must be enclosed in a Markdown block like the one below:

```python
# Your code here
```
Make sure to finish the code with \"\"\"

This is the question:
{question}
"""

def extract_python_code(text):
    """Extract Python code from various possible formats."""
    # Bloc ```python ... ```
    code_block = re.search(r"```python(.*?)```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()

    # Bloc ``` ... ```
    code_block = re.search(r"```(.*?)```", text, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()

    # Bloc """ ... """
    triple_quote_block = re.search(r'"""(.*?)"""', text, re.DOTALL)
    if triple_quote_block:
        return triple_quote_block.group(1).strip()

    # Fallback : texte entier si ça ressemble à du code
    if "def " in text or "import " in text:
        return text.strip()

    return None

def run_python_code(code):
    """Safely execute Python code and capture the output."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {}, {})
        return buffer.getvalue().strip()
    except Exception as e:
        return f"Execution error: {e}"
    
def run_python_code(code):
    """Safely execute Python code and capture the output or error."""
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {}, {})
        return buffer.getvalue().strip(), None
    except Exception as e:
        print(e)
        return "", f"{type(e).__name__}: {e}"


def agent_loop(prompt, max_steps=3):
    formatted_prompt = AGENT_PROMPT.format(question=prompt)
    messages = [HumanMessage(content=formatted_prompt)]

    for step in range(max_steps):
        print(f"\n🧠 Step {step + 1}:\n")

        response = llm.invoke(messages)
        content = response.content.strip()
        print("🗨️ LLM:", content)

        code = extract_python_code(content)

        if code:
            print("\n💻 Code detected, executing...\n")
            output, error = run_python_code(code)

            if error:
                print("❌ Execution error:", error)
                messages.append(HumanMessage(
                    content=f"The code raised the following error during execution:\n{error}"
                ))
            else:
                print("🧾 Output:", output)
                messages.append(HumanMessage(
                    content=f"Here is the output of your code:\n{output}"
                ))
        else:
            print("✅ No code to execute, stopping.")
            break


# Exemple d'utilisation
if __name__ == "__main__":
    user_prompt = (
    "Write a Python script that scrapes the titles of the top 5 articles from the Hacker News homepage "
    "(https://news.ycombinator.com), saves them in a file named 'top_hn_titles.txt', then reads this file and prints its content."
)
    agent_loop(user_prompt)
