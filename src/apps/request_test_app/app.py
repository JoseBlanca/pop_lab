[bug]: starlette request object does not have ther query parameters in shinylive

# I have followed this method
# https://github.com/posit-dev/py-shiny/issues/323#issuecomment-1712438276

# VSC
# url: http://localhost:32997/?param=hi
# ouput
# request: <starlette.requests.Request object at 0x7f7d26702600>
# url_query: param=hi&vscodeBrowserReqId=1733558209861
# param: hi

# rm -r tmp_shiny_site;  uv run shinylive export src/apps/request_test_app/ tmp_shiny_site/; uv run python -m http.server --directory tmp_shiny_site --bind localhost 8008
# http://[::1]:8008/?param=hi
# request: <starlette.requests.Request object at 0x104e330>
# url_query:
# param: None

# uv run uvicorn app:app
# http://127.0.0.1:8000/?param=hi
# request: <starlette.requests.Request object at 0x7fe7578c7770>
# url_query: param=hi
# param: hi

from shiny import App, ui, render


def app_ui(request):
    ui_elements = []
    ui_elements.append(ui.p(f"request: {request}"))

    url_query = request.url.query
    ui_elements.append(ui.p(f"url_query: {url_query}"))

    greeting = request.query_params.get("param")
    ui_elements.append(f"param: {greeting}")

    return ui.page_fixed(ui_elements)


def server(inputs, outputs, sessions):
    @render.code
    def greeting():
        return "Hi!."


app = App(app_ui, server)
