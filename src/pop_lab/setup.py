import importlib
import asyncio
import time

REQUIRED_PACKAGES = ["ipywidgets", "numpy", "pandas", "matplotlib"]


def _create_install_task(library, piplite, loop):
    try:
        importlib.import_module(library)
        task = None
    except ModuleNotFoundError:
        if piplite is None:
            raise RuntimeError(
                f"Package missing: {library}, and piplite not available to install it"
            )
        task = piplite.install(library)
        task.set_name(library)
        loop.run_until_complete(task)

    return task


def install_libraries():
    libraries = REQUIRED_PACKAGES

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        piplite = importlib.import_module("piplite")
    except ModuleNotFoundError:
        piplite = None

    for library in libraries:
        _create_install_task(library, piplite, loop)

    for i in range(20):
        running_install_tasks = []
        for task in asyncio.all_tasks():
            if task.done():
                continue
            if hasattr(task, "get_name"):
                if task.get_name() not in libraries:
                    continue
            running_install_tasks.append(task)

        if not running_install_tasks:
            break
        print(running_install_tasks[0])
        print(dir(running_install_tasks[0]))
        print([task.done() for task in running_install_tasks])
        print([task.get_name() for task in running_install_tasks])
        time.sleep(1)


install_libraries()
