from argparse import ArgumentParser
from pathlib import Path
from tempfile import mkdtemp

from jupyterlab import galata
from notebook.app import main as notebook


def main():
    args = _parser.parse_args()
    opt1 = _minispot_options()
    opt2 = _playwright_options() if args.playwright else []
    return notebook([*opt1, *opt2])


def _minispot_options():
    return ["--ServerApp.jpserver_extensions=minispot=true"]


def _playwright_options():
    return [
        "--ServerApp.password=",
        "--IdentityProvider.token=",
        "--ServerApp.disable_check_xsrf=true",
        "--LabApp.expose_app_in_browser=true",
        "--JupyterNotebookApp.expose_app_in_browser=true",
        f"--ServerApp.root_dir={mkdtemp()}",
        f"--LabApp.workspaces_dir={mkdtemp()}",
        f"--LabServerApp.extra_labextensions_path={_galata}",
    ]


_galata = str(Path(galata.__file__).parent)

_parser = ArgumentParser()

_parser.add_argument(
    "--playwright",
    action="store_true",
    help="configure jupyter for playwright tests",
)
