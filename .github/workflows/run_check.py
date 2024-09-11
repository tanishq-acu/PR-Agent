import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.memory import Memory
from metagpt.schema import MessageQueue
from metagpt.tools.libs.filesys_interact import ListPythonFiles, InferProgramPurpose, GenerateComments
import sys 
import os

# Constants:

REQ_PROMPT = """
Given the file '{dir}', infer the program purpose of the python file. Then, given the purpose, generate feedback for the program. Finally, write ONLY the generated feedback to a file named 'feedback.txt'.
"""

async def agent_process_dirs(paths: list[str]):
    """
    Run agent on given directories. 

    Params:
        paths: list[str] = List of directories as strings. 
    Returns:
        list[str] = List of responses. 
    """
    out = []
    for item in paths:
        role = DataInterpreter(tools=["ListPythonFiles", "InferProgramPurpose", "GenerateComments"], react_mode="react", max_react_loop=10)
        temp = await run_agent_directory(role,item)
        out.append(temp)
    return out

async def run_agent_directory(agent: DataInterpreter, path: str):
    """
    Run agent method. 

    Params:
        agent: DataInterpreter = The LLM-agent to utilize. 
        path: str = The path/directory to the python file.
    Returns:
        str | None: The agent's response for that particular directory as a formatted string.
    """
    if os.path.isdir(path):
        prompt = REQ_PROMPT.format(dir=path)
        await agent.run(prompt)
        if os.path.exists("feedback.txt"):
            with open("feedback.txt", "r") as file:
                ret = f"{path}:\n{file.read()}\n"
            return ret
        else:
            return None
    elif os.path.exists(path):
        if path.endswith(".py"):
            prompt = REQ_PROMPT.format(dir = path)
            await agent.run(prompt)
            if os.path.exists("feedback.txt"):
                with open("feedback.txt", "r") as file:
                    ret= f"{path}:\n{file.read()}\n"
                return ret
            else:
                return None
        else:
            return None
    else:
        return None

    
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        pass
    else:
        res = asyncio.run(agent_process_dirs(sys.argv[1:]))
        total = ""
        for item in res:
            if item is not None:
                total += item
        with open("feedback.txt", "w") as feedback:
            feedback.write(total)
            