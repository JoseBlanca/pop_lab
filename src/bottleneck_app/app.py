from shiny import App, reactive, render, ui
import pandas

import ruamel.yaml
import msprime

recomb_panel = (
    ui.input_slider(
        "recomb_slider", label="Recombination rate", min=0, max=1e-6, value=1e-8
    ),
)

MIN_RECOMB_RATE = -10
DEF_RECOMB_RATE = -8
MAX_RECOMB_RATE = -6

MIN_MUT_RATE = -10
DEF_MUT_RATE = -8
MAX_MUT_RATE = -6

MIN_SAMPLE_SIZE = 20
DEF_SAMPLE_SIZE = 50
MAX_SAMPLE_SIZE = 100

SUMMARY_TABLE_ID = "summary_table"
RESULT_TABLE_ID = "results_table"

sample_size_panel = (
    (
        ui.input_slider(
            "sample_size_slider",
            label="",
            min=MIN_SAMPLE_SIZE,
            max=MAX_SAMPLE_SIZE,
            value=DEF_SAMPLE_SIZE,
            width="100%",
        ),
    ),
)

recomb_panel = (
    ui.layout_columns(
        ui.panel_conditional(
            "!input.no_recomb_checkbox",
            ui.input_slider(
                "recomb_rate_slider",
                label="Log. scale",
                min=MIN_RECOMB_RATE,
                max=MAX_RECOMB_RATE,
                value=DEF_RECOMB_RATE,
                width="100%",
            ),
        ),
        ui.input_checkbox("no_recomb_checkbox", label="No recombination", value=False),
        col_widths=(10, 2),
    ),
)

mut_panel = (
    (
        ui.input_slider(
            "mut_rate_slider",
            label="Log. scale",
            min=MIN_MUT_RATE,
            max=MAX_MUT_RATE,
            value=DEF_MUT_RATE,
            width="100%",
        ),
    ),
)


inputs_panel = ui.accordion(
    ui.accordion_panel("Sample size", sample_size_panel),
    ui.accordion_panel("Recombination", recomb_panel),
    ui.accordion_panel("Mutation", mut_panel),
    id="inputs_panel",
    open=[],
)

input_card = ui.card(
    ui.h1("Bottleneck"),
    ui.card(inputs_panel),
)

summary = ui.navset_tab(
    ui.nav_panel(
        "Parameters",
        ui.output_data_frame(SUMMARY_TABLE_ID),
    ),
    ui.nav_panel(
        "Results",
        ui.output_data_frame(RESULT_TABLE_ID),
    ),
    selected="Results",
)

output_panels = (ui.nav_panel("Summary", summary),)

output_card = ui.card(
    ui.navset_tab(
        *output_panels,
    )
)


app_ui = ui.page_fixed(
    input_card,
    output_card,
    ui.output_code("greeting"),
    lang="en",
)


def server(input, output, session):
    @render.code
    def greeting():
        return "Hola"

    @render.data_frame
    def summary_table():
        df = pandas.DataFrame({"Parameter": [], "Value": []})
        return render.DataGrid(df)


app = App(app_ui, server)
