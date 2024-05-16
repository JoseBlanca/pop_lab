from datetime import datetime
import math

from shiny import App, reactive, render, ui

# The UI section consists of a single (potentially very long and deeply nested) expression,
# stored as a variable named app_ui by convention. The object this produces is actually simply HTML,
# which is sent to the browser when it first loads the app.

# Broadly speaking, there are two kinds of UI components in Shiny: container components, which,
# as the name suggests, can contain other components, and non-container components, which cannot.
# (You can also think of the UI as a tree data structure: container components have children,
# while non-container components are leaf nodes in the tree.)
# some examples of container components:
#
#    ui.sidebar()
#    ui.card()
#    ui.layout_columns()
#    ui.div()
# some examples of non-container components:
#    ui.input_text()
#    ui.output_plot()
#
# to put a component inside of a container, you nest the function calls, like ui.sidebar(ui.input_text())

MIN_POP_SIZE = 10
MAX_POP_SIZE = 1000
DEF_POP_SIZE = 100
DEF_GENO_FREQS = (0.25, 0.75)
DEF_FREQ_Aa = DEF_GENO_FREQS[1] - DEF_GENO_FREQS[0]
DEF_FREQ_A = DEF_GENO_FREQS[0] + DEF_FREQ_Aa * 0.5

GENOMIC_FREQS_TAB_ID = "genomic_freqs"
ALLELIC_FREQS_TAB_ID = "allelic_freqs"

pop_size_widget = ui.row(
    ui.layout_columns(
        ui.panel_conditional(
            "!input.pop_is_inf_checkbox",
            ui.input_slider(
                "pop_size_slider",
                label="Pop. size:",
                min=MIN_POP_SIZE,
                max=MAX_POP_SIZE,
                value=DEF_POP_SIZE,
                width="100%",
            ),
        ),
        ui.input_checkbox("pop_is_inf_checkbox", label="Pop. is inf.", value=False),
        col_widths=(10, 2),
    ),
)

freq_A_Aa_widget = ui.row(
    ui.input_numeric(
        "freq_A_input", "Freq. A", DEF_FREQ_A, min=0.0, max=1.0, step=0.01
    ),
    ui.input_numeric(
        "freq_Aa_input", "Freq. Aa", DEF_FREQ_Aa, min=0.0, max=1.0, step=0.01
    ),
)

geno_freqs_slider = ui.row(
    ui.input_slider(
        "geno_freqs_slider",
        label="",
        min=0,
        max=1,
        value=DEF_GENO_FREQS,
        width="100%",
    ),
)

panels = [
    ui.nav_panel("Genomic freqs.", geno_freqs_slider, value=GENOMIC_FREQS_TAB_ID),
    ui.nav_panel("Allelic freqs.", freq_A_Aa_widget, value=ALLELIC_FREQS_TAB_ID),
]

freqs_tab = ui.navset_tab(
    *panels,
    id="freqs_tabs",
)

geno_freqs_widget = ui.row(
    freqs_tab,
    ui.row(
        ui.layout_columns(
            ui.value_box(
                title="Freq. AA",
                value=ui.output_ui("freq_AA_output"),
            ),
            ui.value_box(
                title="Freq. Aa",
                value=ui.output_ui("freq_Aa_output"),
            ),
            ui.value_box(
                title="Freq. aa",
                value=ui.output_ui("freq_aa_output"),
            ),
        )
    ),
)


app_ui = ui.page_fixed(
    ui.h1("Foward in time simulation"),
    ui.card(pop_size_widget, geno_freqs_widget),
    ui.output_code("greeting"),
    ui.card(ui.output_code("pop_size_output")),
)

# The server section is a function, named server by convention,
# that always takes the arguments input, output, and session.
# This function contains render functions and reactive functions, which are used to update the UI in
# response to user input.


def server(input, output, session):
    @reactive.calc
    def time():
        reactive.invalidate_later(1)
        return datetime.now()

    # The name of this rendering function should match the placeholder name in ui
    @render.code
    def greeting():
        return f"Hello, world!\nIt's currently {time()}."

    @render.code
    def pop_size_output():
        return f"Pop size is: {get_pop_size()}"

    def get_pop_size():
        pop_size = int(input.pop_size_slider())
        if input.pop_is_inf_checkbox():
            pop_size = math.inf
        return pop_size

    @reactive.calc
    def get_freq_AA():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_AA = input.geno_freqs_slider()[0]
        elif input.freqs_tabs() == ALLELIC_FREQS_TAB_ID:
            freq_Aa = input.freq_Aa_input()
            freq_A = input.freq_A_input()
            freq_AA = freq_A - (freq_Aa / 2)
        return freq_AA

    @reactive.calc
    def get_freq_aa():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_aa = 1 - input.geno_freqs_slider()[1]
        elif input.freqs_tabs() == ALLELIC_FREQS_TAB_ID:
            freq_Aa = input.freq_Aa_input()
            freq_A = input.freq_A_input()
            freq_aa = (1 - freq_A) - (freq_Aa / 2)
        return freq_aa

    @reactive.calc
    def get_freq_Aa():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_Aa = input.geno_freqs_slider()[1] - input.geno_freqs_slider()[0]
        elif input.freqs_tabs() == ALLELIC_FREQS_TAB_ID:
            freq_Aa = input.freq_Aa_input()
        return freq_Aa

    @reactive.calc
    def get_freq_A():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_A = get_freq_AA() + get_freq_Aa() * 0.5
        elif input.freqs_tabs() == ALLELIC_FREQS_TAB_ID:
            freq_A = input.freq_A_input()
        return freq_A

    @render.text
    def freq_AA_output():
        return f"{get_freq_AA():.2f}"

    @render.text
    def freq_Aa_output():
        return f"{get_freq_Aa():.2f}"

    @render.text
    def freq_aa_output():
        return f"{get_freq_aa():.2f}"


app = App(app_ui, server)
