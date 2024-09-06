import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.libs.filesys_interact import ListPythonFiles, InferProgramPurpose, GenerateComments
import sys 
import os
REQ_PROMPT = """
Given the directory/file '{dir}', infer the intended purpose of the python file(s) and then use that to generate feedback for the file using your provided tools. Write only the generated feedback to a file named 'feedback.txt'.
"""
async def run_check(paths: list[str]):
    role = DataInterpreter(tools=["ListPythonFiles", "InferProgramPurpose", "GenerateComments"], react_mode="react", max_react_loop=10)
    return await asyncio.gather(*[run_agent(role, directory) for directory in paths])
async def run_agent(agent, path: str):
    if os.path.isdir(path):
        prompt = REQ_PROMPT.format(dir=path)
        await agent.run(prompt)
        if os.path.exists("feedback.txt"):
            file= open("feedback.txt", "r")
            return f"{path}:\n{file.read()}\n"
        else:
            return None
    elif os.path.exists(path):
        if path.endswith(".py"):
            prompt = REQ_PROMPT.format(dir = path)
            await agent.run(prompt)
            if os.path.exists("feedback.txt"):
                file = open("feedback.txt", "r")
                return f"{path}:\n{file.read()}\n"
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
        print(total)