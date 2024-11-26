import math

from shiny import module, reactive, render, ui
import matplotlib.pyplot as plt
import pandas

from one_locus_two_alleles_simulator import (
    OneLocusTwoAlleleSimulation,
    INF,
    MutRates,
)
from fwd_in_time_app_specific_code import (
    SELECT_FITNESS,
    SELECT_MUTATION,
    SELECT_SELFING,
)


MIN_POP_SIZE = 10
MAX_POP_SIZE = 1000
DEF_POP_SIZE = 100
DEF_GENO_FREQS = (0.25, 0.75)
DEF_FREQ_Aa = DEF_GENO_FREQS[1] - DEF_GENO_FREQS[0]
DEF_FREQ_A = DEF_GENO_FREQS[0] + DEF_FREQ_Aa * 0.5
MIN_NUM_GEN = 10
MAX_NUM_GEN = 500
DEF_NUM_GEN = 100

HW_FREQS_TAB_ID = "hw_freq_A_tab"
GENOMIC_FREQS_TAB_ID = "genomic_freqs_tab"
GENO_FREQS_PLOT_ID = "geno_freqs_plot"
FREQ_A_PLOT_ID = "freq_A_plot"
EXP_HET_PLOT_ID = "exp_het_plot"
SUMMARY_TABLE_ID = "summary_table"
RESULT_TABLE_ID = "result_table"


@module.ui
def fwd_in_time_ui():
    freq_A_slider = ui.row(
        ui.input_slider(
            "freq_A_slider",
            label="Freq. A",
            min=0,
            max=1,
            value=DEF_FREQ_A,
            width="100%",
        ),
    )

    geno_freqs_slider = ui.row(
        ui.input_slider(
            "geno_freqs_slider",
            label="Genomic freqs.: AA • Aa • aa",
            min=0,
            max=1,
            value=DEF_GENO_FREQS,
            width="100%",
        ),
    )

    freqs_tab = ui.navset_card_tab(
        ui.nav_panel("With Hardy-Weinberg eq.", freq_A_slider, value=HW_FREQS_TAB_ID),
        ui.nav_panel(
            "Without Hardy-Weinberg eq.", geno_freqs_slider, value=GENOMIC_FREQS_TAB_ID
        ),
        id="freqs_tabs",
    )

    pop_size_panel = (
        ui.layout_columns(
            ui.panel_conditional(
                "!input.pop_is_inf_checkbox",
                ui.input_slider(
                    "pop_size_slider",
                    label="",
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

    num_gen_panel = (
        ui.input_slider(
            "num_gen_slider",
            label="",
            min=MIN_NUM_GEN,
            max=MAX_NUM_GEN,
            value=DEF_NUM_GEN,
            width="100%",
        ),
    )

    accordion_panels = [
        ui.accordion_panel("Initial freqs.", freqs_tab),
        ui.accordion_panel("Pop. size", pop_size_panel),
        ui.accordion_panel("Num. generations", num_gen_panel),
    ]

    extra_open_panels = []
    if SELECT_FITNESS:
        fitness_panel = (
            ui.input_slider("wAA_slider", label="wAA", min=0, max=1, value=1),
            ui.input_slider("wAa_slider", label="wAa", min=0, max=1, value=1),
            ui.input_slider("waa_slider", label="waa", min=0, max=1, value=1),
        )
        accordion = ui.accordion_panel("Selection", fitness_panel)
        accordion_panels.append(accordion)
        extra_open_panels.append("Selection")
    if SELECT_MUTATION:
        mutation_panel = (
            ui.input_slider("A2a_slider", label="A2a", min=0, max=0.1, value=0),
            ui.input_slider("a2A_slider", label="a2A", min=0, max=0.1, value=0),
        )
        accordion = ui.accordion_panel("Mutation", mutation_panel)
        accordion_panels.append(accordion)
        extra_open_panels.append("Mutation")
    if SELECT_SELFING:
        selfing_slider = ui.input_slider(
            "selfing_slider", label="", min=0, max=1, value=0
        )
        accordion = ui.accordion_panel("Selfing rate", selfing_slider)
        accordion_panels.append(accordion)
        extra_open_panels.append("Selfing")

    open_panels = ["Initial freqs.", "Pop. size", "Num. generations"]
    if len(extra_open_panels) == 1:
        open_panels.extend(extra_open_panels)

    inputs_panel = ui.accordion(
        *accordion_panels,
        id="inputs_panel",
        open=open_panels,
    )

    sim_params_widget = ui.layout_columns(
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

    run_button = ui.input_action_button("run_button", "Run simulation")

    input_card = ui.card(
        ui.card(inputs_panel, sim_params_widget),
        run_button,
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
        ui.nav_panel("Summary", summary),
    )

    output_card = ui.card(
        ui.navset_tab(
            *output_panels,
        )
    )
    return input_card, output_card


@module.server
def fwd_in_time_server(input, output, session):
    def get_pop_size():
        pop_size = int(input.pop_size_slider())
        if input.pop_is_inf_checkbox():
            pop_size = INF
        return pop_size

    @reactive.calc
    def get_freq_AA():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_AA = input.geno_freqs_slider()[0]
        elif input.freqs_tabs() == HW_FREQS_TAB_ID:
            freq_A = input.freq_A_slider()
            freq_AA = freq_A**2
        return freq_AA

    @reactive.calc
    def get_freq_aa():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_aa = 1 - input.geno_freqs_slider()[1]
        elif input.freqs_tabs() == HW_FREQS_TAB_ID:
            freq_A = input.freq_A_slider()
            freq_aa = (1 - freq_A) ** 2
        return freq_aa

    @reactive.calc
    def get_freq_Aa():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_Aa = input.geno_freqs_slider()[1] - input.geno_freqs_slider()[0]
        elif input.freqs_tabs() == HW_FREQS_TAB_ID:
            freq_A = input.freq_A_slider()
            freq_Aa = 1 - freq_A**2 - (1 - freq_A) ** 2
        return freq_Aa

    @reactive.calc
    def get_num_generations():
        return input.num_gen_slider()

    @reactive.calc
    def get_freq_A():
        if input.freqs_tabs() == GENOMIC_FREQS_TAB_ID:
            freq_A = get_freq_AA() + get_freq_Aa() * 0.5
        elif input.freqs_tabs() == HW_FREQS_TAB_ID:
            freq_A = input.freq_A_slider()
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
    def get_fitness_rates():
        if SELECT_FITNESS:
            wAA = input.wAA_slider()
            wAa = input.wAa_slider()
            waa = input.waa_slider()
        else:
            wAA, wAa, waa = 1.0, 1.0, 1.0
        return wAA, wAa, waa

    @reactive.calc
    def get_mutation_rates():
        if SELECT_MUTATION:
            A2a = input.A2a_slider()
            a2A = input.a2A_slider()
        else:
            A2a, a2A = 0.0, 0.0
        return A2a, a2A

    @reactive.calc
    def get_selfing_rate():
        if SELECT_SELFING:
            selfing_rate = input.selfing_slider()
        else:
            selfing_rate = 0.0
        return selfing_rate

    @reactive.calc
    @reactive.event(input.run_button)
    def do_simulation():
        sim_params = {
            "pops": {
                "pop1": {
                    "genotypic_freqs": (get_freq_AA(), get_freq_Aa(), get_freq_aa()),
                    "size": get_pop_size(),
                    "selfing_rate": get_selfing_rate(),
                },
            },
            "num_generations": get_num_generations(),
            "loggers": [
                "allelic_freqs_logger",
                "genotypic_freqs_logger",
                "exp_het_logger",
            ],
        }

        wAA, wAa, waa = get_fitness_rates()
        if (
            not math.isclose(wAA, 1)
            or not math.isclose(wAa, 1)
            or not math.isclose(waa, 1)
        ):
            sim_params["pops"]["pop1"]["fitness"] = (wAA, wAa, waa)

        A2a, a2A = get_mutation_rates()
        if not math.isclose(A2a, 0) or not math.isclose(a2A, 0):
            sim_params["pops"]["pop1"]["mut_rates"] = MutRates(A2a, a2A)

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

    @render.data_frame
    def summary_table():
        parameters = []
        values = []
        parameters.append("Freq. AA (init)")
        values.append(get_freq_AA())
        parameters.append("Freq. Aa (init)")
        values.append(get_freq_Aa())
        parameters.append("Freq. aa (init)")
        values.append(get_freq_aa())

        if SELECT_FITNESS:
            wAA, wAa, waa = get_fitness_rates()
            parameters.append("wAA")
            values.append(wAA)
            parameters.append("wAa")
            values.append(wAa)
            parameters.append("waa")
            values.append(waa)

        if SELECT_MUTATION:
            mutA2a, muta2A = get_mutation_rates()
            parameters.append("mut. A -> a")
            values.append(mutA2a)
            parameters.append("mut. a -> A")
            values.append(muta2A)

        if SELECT_SELFING:
            selfing_rate = get_selfing_rate()
            parameters.append("Selfing rate")
            values.append(selfing_rate)

        parameters.append("Pop. size")
        values.append(get_pop_size())

        parameters.append("Num. generations")
        values.append(get_num_generations())

        df = pandas.DataFrame({"Parameter": parameters, "Value": values})
        return render.DataGrid(df)

    @render.data_frame
    def result_table():
        parameters = []
        values = []

        sim = do_simulation()
        genotypic_freqs = sim.results["genotypic_freqs"]
        parameters.append("Freq. AA (final)")
        values.append(round(genotypic_freqs["freqs_AA"].iloc[-1, 0], ndigits=2))
        parameters.append("Freq. Aa (final)")
        values.append(round(genotypic_freqs["freqs_Aa"].iloc[-1, 0], 2))
        parameters.append("Freq. aa (final)")
        values.append(round(genotypic_freqs["freqs_aa"].iloc[-1, 0], 2))

        parameters.append("Exp. het. (final)")
        values.append(round(sim.results["expected_hets"].iloc[-1, 0], 2))

        df = pandas.DataFrame({"Parameter": parameters, "Value": values})
        return render.DataGrid(df)
