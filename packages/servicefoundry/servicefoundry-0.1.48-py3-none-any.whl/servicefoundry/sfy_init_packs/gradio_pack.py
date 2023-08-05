from servicefoundry.sfy_init.pack import Pack

webapp_file_content = """
import gradio as gr

def greet(name):
    return "Hello " + name + "!!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0", server_port=8000)
"""

requirements_txt_content = """
gradio
servicefoundry
protobuf==3.20.1
"""


class GradioPack(Pack):
    def get_default_service_name(self):
        return "gradio-webapp"

    def get_description(self):
        return "gradio - Create demo using gradio framework."

    def get_files(self):
        return {
            "webapp.py": webapp_file_content,
            "requirements.txt": requirements_txt_content,
            "Procfile": "web: python webapp.py",
        }
