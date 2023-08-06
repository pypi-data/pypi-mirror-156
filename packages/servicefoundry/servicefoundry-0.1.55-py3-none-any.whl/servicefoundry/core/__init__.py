from servicefoundry.core.login import login
from servicefoundry.core.logout import logout
from servicefoundry.core.notebook.notebook_util import is_notebook
from servicefoundry.internal.predictor import Predictor

load_predictor = Predictor.load_predictor

if is_notebook():
    try:
        import ipywidgets
    except ImportError:
        print("Run `pip install ipywidgets` to use notebook features.")
