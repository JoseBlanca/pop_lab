from shiny import App, ui
import fwd_in_time_app_specific_code

APP_ID = "balancing_selection_app"

input_card, output_card = fwd_in_time_app_specific_code.fwd_in_time_ui(APP_ID)


app_ui = ui.page_fixed(
    ui.panel_title(fwd_in_time_app_specific_code.TITLE),
    input_card,
    output_card,
    title="Pop Lab",
    lang="en",
)


def server(input, output, session):
    fwd_in_time_app_specific_code.fwd_in_time_server(APP_ID)


app = App(app_ui, server)