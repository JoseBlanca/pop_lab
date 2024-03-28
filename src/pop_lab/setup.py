import importlib
import asyncio

REQUIRED_PACKAGES = ["ipywidgets", "numpy", "pandas", "matplotlib"]


async def install_packages():
    packages = REQUIRED_PACKAGES

    try:
        piplite = importlib.import_module("piplite")
    except ModuleNotFoundError:
        piplite = None

    for package in packages:
        try:
            importlib.import_module(package)
        except ModuleNotFoundError:
            if piplite is None:
                raise RuntimeError(
                    f"Package missing: {package}, and piplite not available to install it"
                )
            await piplite.install(package)


def run_async_function(async_func):
    try:
        # Attempt to get the current event loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(async_func())
    else:
        # No running event loop, so run a new one
        asyncio.run(async_func())


run_async_function(install_packages)
