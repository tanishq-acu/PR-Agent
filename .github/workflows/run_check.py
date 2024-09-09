import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.memory import Memory
from metagpt.tools.libs.filesys_interact import ListPythonFiles, InferProgramPurpose, GenerateComments
import sys 
import os

REQ_PROMPT = """
Given the directory/file '{dir}', infer the program purpose of the python file(s), then generate feedback for the file given the purpose. Finally, write only the generated feedback to a file named 'feedback.txt'.
"""

async def run_check(paths: list[str]):
    role = DataInterpreter(tools=["ListPythonFiles", "InferProgramPurpose", "GenerateComments"], react_mode="react", max_react_loop=10)
    return await asyncio.gather(*[run_agent(role, directory) for directory in paths])

async def run_agent(agent, path: str):
    agent.rc.memory=Memory()
    if os.path.isdir(path):
        prompt = REQ_PROMPT.format(dir=path)
        await agent.run(prompt)
        if os.path.exists("feedback.txt"):
            file = open("feedback.txt", "r")
            ret = f"{path}:\n{file.read()}\n"
            file.close()
            return ret
        else:
            return None
    elif os.path.exists(path):
        if path.endswith(".py"):
            prompt = REQ_PROMPT.format(dir = path)
            await agent.run(prompt)
            if os.path.exists("feedback.txt"):
                file = open("feedback.txt", "r")
                ret= f"{path}:\n{file.read()}\n"
                file.close()
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
        res = asyncio.run(run_check(sys.argv[1:]))
        total = ""
        for item in res:
            if item is not None:
                total += item
        with open("feedback.txt", "w") as feedback:
            feedback.write(total)
            