from shiny import App, reactive, render, ui
import matplotlib.pyplot as plt

from one_locus_two_alleles_simulator import OneLocusTwoAlleleSimulation, INF

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
MIN_NUM_GEN = 10
MAX_NUM_GEN = 500
DEF_NUM_GEN = 100

GENOMIC_FREQS_TAB_ID = "genotypic_freqs"
ALLELIC_FREQS_TAB_ID = "allelic_freqs"
GENO_FREQS_PLOT_ID = "geno_freqs_plot"
FREQ_A_PLOT_ID = "freq_A_plot"
EXP_HET_PLOT_ID = "exp_het_plot"

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

num_gen_widget = ui.row(
    ui.input_slider(
        "num_gen_slider",
        label="Num. generations",
        min=MIN_NUM_GEN,
        max=MAX_NUM_GEN,
        value=DEF_NUM_GEN,
        width="100%",
    ),
)

run_button = ui.input_action_button("run_button", "Run simulation")

input_card = ui.card(
    ui.h1("One locus foward in time simulation"),
    ui.card(pop_size_widget, geno_freqs_widget, num_gen_widget),
    run_button,
)

output_panels = (
    ui.nav_panel(
        "Genotypic freqs.",
        ui.output_plot(GENO_FREQS_PLOT_ID),
    ),
    ui.nav_panel(
        "Freq A.",
        ui.output_plot(FREQ_A_PLOT_ID),
    ),
    ui.nav_panel(
        "Exp. Het.",
        ui.output_plot(EXP_HET_PLOT_ID),
    ),
)

output_card = ui.card(
    ui.navset_tab(
        *output_panels,
    )
)


app_ui = ui.page_fixed(
    input_card,
    output_card,
)

# The server section is a function, named server by convention,
# that always takes the arguments input, output, and session.
# This function contains render functions and reactive functions, which are used to update the UI in
# response to user input.


def server(input, output, session):
    def get_pop_size():
        pop_size = int(input.pop_size_slider())
        if input.pop_is_inf_checkbox():
            pop_size = INF
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
    def get_num_generations():
        return input.num_gen_slider()

    @reactive.calc
    def get_freq_A():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_A = get_freq_AA() + get_freq_Aa() * 0.5
        elif input.freqs_tabs() == ALLELIC_FREQS_TAB_ID:
            freq_A = input.freq_A_input()
        return freq_A

    @reactive.effect
    @reactive.event(input.freq_Aa_input)
    def _():
        freq_Aa = input.freq_Aa_input()
        min_ = round(freq_Aa, ndigits=2)
        max_ = 1 - freq_Aa
        current_value = input.freq_A_input()
        if current_value < min_:
            current_value = min_
        elif current_value > max_:
            current_value = max_
        ui.update_numeric("freq_A_input", min=min_, max=max_, value=current_value)

    @reactive.effect
    @reactive.event(input.freq_A_input)
    def _():
        freq_A = input.freq_A_input()
        freq_a = 1 - freq_A
        max_ = round(min((freq_A, freq_a)), ndigits=2)
        current_value = input.freq_Aa_input()
        if current_value > max_:
            current_value = max_
        ui.update_numeric("freq_Aa_input", min=0, max=max_, value=current_value)

    @render.text
    def freq_AA_output():
        return f"{get_freq_AA():.2f}"

    @render.text
    def freq_Aa_output():
        return f"{get_freq_Aa():.2f}"

    @render.text
    def freq_aa_output():
        return f"{get_freq_aa():.2f}"

    @reactive.calc
    @reactive.event(input.run_button)
    def do_simulation():
        sim_params = {
            "pops": {
                "pop1": {
                    "genotypic_freqs": (get_freq_AA(), get_freq_Aa(), get_freq_aa()),
                    "size": get_pop_size(),
                },
            },
            "num_generations": get_num_generations(),
            "loggers": [
                "allelic_freqs_logger",
                "genotypic_freqs_logger",
                "exp_het_logger",
            ],
        }

        sim = OneLocusTwoAlleleSimulation(sim_params)
        return sim

    @render.plot(alt="Genotypic freqs.")
    def geno_freqs_plot():
        sim = do_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Genotypic freqs.")
        axes.set_xlabel("generation")
        axes.set_ylabel("freq")

        genotypic_freqs = sim.results["genotypic_freqs"]
        geno_freqs_labels = sorted(genotypic_freqs.keys())
        for geno_freq_label in geno_freqs_labels:
            geno_freqs_series = genotypic_freqs[geno_freq_label]
            axes.plot(
                geno_freqs_series.index, geno_freqs_series.values, label=geno_freq_label
            )
        axes.legend()
        axes.set_ylim((0, 1))
        return fig

    @render.plot(alt="Freq. A")
    def freq_A_plot():
        sim = do_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Freq. A")
        axes.set_xlabel("generation")
        axes.set_ylabel("freq")

        freqs_series = sim.results["allelic_freqs"]
        axes.plot(freqs_series.index, freqs_series.values, label="Freq. A")
        axes.set_ylim((0, 1))
        return fig

    @render.plot(alt="Exp. Het.")
    def exp_het_plot():
        sim = do_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Expected Het.")
        axes.set_xlabel("generation")
        axes.set_ylabel("Exp. Het.")

        freqs_series = sim.results["expected_hets"]
        axes.plot(freqs_series.index, freqs_series.values, label="Exp. Het.")
        axes.set_ylim((0, 1))
        return fig


app = App(app_ui, server)
