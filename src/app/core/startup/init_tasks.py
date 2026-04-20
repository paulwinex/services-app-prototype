import logging
from pathlib import Path

from fastapi import FastAPI
import importlib


def init_task_modules(app: FastAPI) -> None:
    root = Path(__file__).parent.parent.parent.joinpath('modules')
    for module_dir in root.iterdir():
        tasks_file = module_dir.joinpath('tasks.py')
        if tasks_file.exists():
            import_path = f'app.modules.{module_dir.name}.{tasks_file.stem}'
            logging.info(f'Importing {import_path}')
            importlib.import_module(import_path)
        tasks_package = module_dir.joinpath('tasks')
        if tasks_package.exists():
            for py_file in tasks_package.glob('*.py'):
                relative_path = py_file.relative_to(tasks_package)
                module_name = relative_path.as_posix().replace('/', '.').split('.', 1)[0]
                import_path = f'app.modules.{module_dir.name}.{tasks_package.name}.{module_name}'
                logging.info(f'Importing {import_path}')
                importlib.import_module(import_path)