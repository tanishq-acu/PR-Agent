from collections import defaultdict
from metagpt.actions import Action
from metagpt.roles.role import Role, RoleReactMode
from metagpt.logs import logger
from metagpt.schema import Message
from typing import Any, Callable, Optional, Union
from pydantic import model_validator, BaseModel
from metagpt.utils.text import generate_prompt_chunk
from metagpt.const import USE_CONFIG_TIMEOUT
import os 
INFER_PROMPT = """
##### PREV SUMMARY ABOVE 
Given the above summary of a python program up to this point and the below python code snippet, create a summary that infers the purpose of the program so far. 

Constraints:
1. The summary must be a maximum of 3 sentences.
2. Ensure that your summary incorporates both the content of the python code snippet and the previous summary. 
3. Ensure that you clearly and concisely state what the program/its functions likely do.
4. Reference important functions or lines if needed in your explanation. 
4. Respond only with your summary. 

###### CODE SNIPPET:
{content}
######
"""

class InferProgramPurpose(Action):
    name: str = "InferProgramPurpose"
    i_context: Optional[str] = None
    desc: str = "Given a directory or file, infer the purpose of each python program."
    async def run(self, directory: str, isFile: bool):
        dirs = set()
        if not isFile:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(".py"):
                        dirs.add((filename, directory + f"/{filename}"))
        else:
            dirs.add(("Summary", directory))
        purposes_to = []
        for name,item in dirs:
            with open(item) as file:
                contents = file.read()
            prompt_template = INFER_PROMPT.format(content="{}")
            sys_text = "You are an AI that is an expert at deducing the purpose of a program. Your sole purpose is to deduce the purpose of a program given some supporting information."
            chunks = generate_prompt_chunk(contents, prompt_template, "gpt-3.5-turbo-0613", system_text = sys_text)
            prev_summary = "# This is the start of the program."
            for prompt in chunks:
                prompt = prev_summary + prompt
                prev_summary = await self._aask(prompt, [sys_text])
            purposes_to.append(name + f": {prev_summary}\n\n")
        return "".join(purposes_to) 

class GenerateCommentsByFile(Action):
    name: str = "GenerateCommentsByFile"
    i_context: Optional[str] = None
    desc: str = "Given a directory or file, generate comments about any possible issues with functionality, "
class PR_Agent(Role):
    name: str = "John"
    profile: str = "Code Review Agent"
    goal: str = "Given a directory containing some Python files, infer the intended purpose of the program and then generate comments on any possible logical errors or code standards using your tools."
    constraints: str = "Ensure that your responses are concise and accurate."
    language: str = "en-us"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([InferProgramPurpose, GenerateCommentsByFile])
        self._set_react_mode(RoleReactMode.REACT.value, 2)
    async def _act(self) -> Message:
        if(self.rc.todo is not None):
            logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.rc.memory.get(k=1)[0]
        if self.rc.todo is None:
            ret = Message(content = msg.content, role =self.profile, cause_by=todo)
        elif isinstance(todo, InferProgramPurpose):
            if os.path.isdir(msg.content):
                result = await todo.run(msg.content, False)
            else:
                result = await todo.run(msg.content, True)
            ret = Message(content=result, role = self.profile, cause_by=todo)
        elif isinstance(todo, GenerateCommentsByFile):
            result = await todo.run(msg.content)
            ret = Message(content= result, role= self.profile, cause_by=todo)
        self.rc.memory.add(ret)
        return ret
import asyncio
print(asyncio.run(InferProgramPurpose().run("/Users/tanishq/Documents/MetaGPT/WebSummarizer/app.py", True)))





import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.memory import Memory
from metagpt.schema import MessageQueue
from metagpt.tools.libs.filesys_interact import ListPythonFiles, InferProgramPurpose, GenerateComments
import sys 
import os
# Run check file

REQ_PROMPT = """
Given the file '{dir}', infer the program purpose of the python file. Then, given the purpose, generate feedback for the program. Finally, write ONLY the generated feedback to a file named 'feedback.txt'.
"""

async def run_check(paths: list[str]):
    """
    Run agent on given directories. 

    Params:
        paths: list[str] = List of directories as strings. 
    Returns:
        list[str] = List of responses. 
    """
    out = []
    for dir in paths:
        role = DataInterpreter(tools=["ListPythonFiles", "InferProgramPurpose", "GenerateComments"], react_mode="react", max_react_loop=10)
        temp = await run_agent(role,dir)
        out.append(temp)
    return out

async def run_agent(agent: DataInterpreter, path: str):
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
def minNumberOfFrogs(self, croakOfFrogs):
    c=r=o=a=k=curr=max_croaks=0
    for i in range(len(croakOfFrogs)):
        if croakOfFrogs[i] == 'c':
            curr +=1
            c += 1
        elif croakOfFrogs[i] == 'r':
            r +=1
        elif croakOfFrogs[i] == 'o':
            o += 1
        elif croakOfFrogs[i] == 'a':
            a +=1
        elif croakOfFrogs[i] == "k":
            k +=1
            curr -=1
        if curr > max_croaks:
            max_croaks = curr
        if c < r or r < o or o < a or a < k:
            return -1
    if curr == 0 and c == r and r == o and o == a and a == k:
        return max_croaks  
    else:
        return -1

