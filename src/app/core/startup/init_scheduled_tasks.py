import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def init_scheduler_tasks(app):
    root = Path(__file__).parent.parent.parent.joinpath('modules')
    for module_dir in root.iterdir():
        tasks_file = module_dir.joinpath('scheduler.py')
        if tasks_file.exists():
            import_path = f'app.modules.{module_dir.name}.{tasks_file.stem}'
            logging.info(f'Importing {import_path}')
            mod = importlib.import_module(import_path)
            func = getattr(mod, 'schedule')
            if func and callable(func):
                func()
