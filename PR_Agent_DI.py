import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.libs.filesys_interact import ListPythonFiles, InferProgramPurpose, GenerateComments
import gradio as gr
# This is a title 2
async def main(requirement: str):
    role = DataInterpreter(tools=["ListPythonFiles", "InferProgramPurpose", "GenerateComments"], react_mode="react", max_react_loop=10)
    await role.run(requirement)
    file= open("feedback.txt", "r")
    return file.read()
def start(dir: str):
    req = f"Given the directory/file '{dir}', infer the intended purpose of the python file(s) and then use that to generate comments on the file using your provided tools. Write the generated comments to a file named 'feedback.txt'."
    return asyncio.run(main(req))
def build():
    with gr.Blocks() as demo:
        file_input = gr.File(label="Select a file")
        
        output = gr.Textbox(label="Output")
        
        process_button = gr.Button("Process File")
    
        process_button.click(fn=start, inputs=file_input, outputs=output)
    demo.launch()
    

# build()

if __name__ == "__main__":
    dir = "/Users/tanishq/Documents/MetaGPT/Testers/app.py"
    req = f"Given the directory/file '{dir}', infer the intended purpose of the python file(s) and then use that to generate comments on the file using your provided tools. Write the generated comments to a file named 'feedback.txt'."
    print(asyncio.run(main(req)))