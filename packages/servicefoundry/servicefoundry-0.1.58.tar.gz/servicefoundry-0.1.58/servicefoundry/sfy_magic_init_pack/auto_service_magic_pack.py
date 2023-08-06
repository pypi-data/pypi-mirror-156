from mako.template import Template

from servicefoundry.requirements.python_requirements import PythonRequirements
from servicefoundry.sfy_magic_init_pack.magic_pack import MagicPack
from servicefoundry.sfy_magic_init_pack.util import get_module_name_from_python_file

main_file_content = """
import logging
from fastapi.responses import HTMLResponse
from servicefoundry.service import fastapi

logger = logging.getLogger(__name__)

app = fastapi.app()


@app.get("/", response_class=HTMLResponse)
def root():
    html_content = "<html><body>Open <a href='/docs'>Docs</a></body></html>"
    return HTMLResponse(content=html_content, status_code=200)

try:
    import ${module_name}
% for function in functions:
app.add_api_route("/${function}", ${module_name}.${function}, methods=["POST"])
% endfor
except ImportError as error:
    print("Failed to import function ${function}: " + error.message)
    raise error
"""

requirements_txt_content = """
gradio
protobuf==3.20.1
"""


class AutoServiceMagicPack(MagicPack):
    def get_files(self):
        main_file_rendered_content = Template(main_file_content).render(
            module_name=get_module_name_from_python_file(self.python_file)
        )
        requirements = PythonRequirements(requirements_txt_content)
        requirements.update_requirements_txt(self.additional_requirements)
        return {
            "main.py": main_file_rendered_content,
            "requirements.txt": requirements.get_requirements_txt(),
            "Procfile": "web: python main.py",
        }
