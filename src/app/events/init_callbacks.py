from pathlib import Path

from fastapi import FastAPI
import importlib


def init_module_callbacks(app: FastAPI) -> None:
    root = Path(__file__).parent.parent.joinpath('modules')
    for module_dir in root.iterdir():
        callbacks_file = module_dir.joinpath('callbacks.py')
        if callbacks_file.exists():
            import_path = f'app.modules.{module_dir.name}.{callbacks_file.stem}'
            importlib.import_module(import_path)