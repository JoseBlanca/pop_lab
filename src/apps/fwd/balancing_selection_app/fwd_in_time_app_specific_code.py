from shiny import module, ui, reactive, render
import matplotlib.pyplot as plt

from one_locus_two_alleles_simulator import OneLocusTwoAlleleSimulation, INF

TITLE = "Balancing selection"

MIN_POP_SIZE = 10
MAX_POP_SIZE = 1000
DEF_POP_SIZE = 100
MIN_NUM_GEN = 10
MAX_NUM_GEN = 500
DEF_NUM_GEN = 100
DEF_FREQ_A = 0.5

GENO_FREQS_PLOT_ID = "geno_freqs_plot"
FREQ_A_PLOT_ID = "freq_A_plot"
EXP_HET_PLOT_ID = "exp_het_plot"
SUMMARY_TABLE_ID = "summary_table"
RESULT_TABLE_ID = "result_table"
DEF_IMMIGRATION = 0.1


@module.ui
def fwd_in_time_ui():
    cards = []
    for pop in ("a", "b"):
        wAA = 1 if pop == "a" else 0
        waa = 1 if pop == "b" else 0
        card = ui.card(
            ui.card_header(f"Pop. {pop.upper()}"),
            ui.input_slider(
                f"pop_{pop}_freq_A_slider",
                label="Freq. A",
                min=0,
                max=1,
                value=DEF_FREQ_A,
                width="100%",
            ),
            ui.input_slider(
                f"pop_{pop}_wAA_slider",
                label="wAA",
                min=0,
                max=1,
                value=wAA,
                width="100%",
            ),
            ui.input_slider(
                f"pop_{pop}_wAa_slider",
                label="wAa",
                min=0,
                max=1,
                value=1,
                width="100%",
            ),
            ui.input_slider(
                f"pop_{pop}_waa_slider",
                label="waa",
                min=0,
                max=1,
                value=waa,
                width="100%",
            ),
            ui.input_slider(
                f"pop_{pop}_immigration_slider",
                label="Immigration",
                min=0,
                max=1,
                value=DEF_IMMIGRATION,
                width="100%",
            ),
        )
        cards.append(card)
    pops_panel = ui.layout_columns(*cards)

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
        ui.accordion_panel("Pop. parameters", pops_panel),
        ui.accordion_panel("Pop. size", pop_size_panel),
        ui.accordion_panel("Num. generations", num_gen_panel),
    ]

    inputs_panel = ui.accordion(
        *accordion_panels,
        id="inputs_panel",
    )

    run_button = ui.input_action_button("run_button", "Run simulation")

    input_card = ui.card(
        ui.card(inputs_panel),
        run_button,
    )

    output_panels = (
        ui.nav_panel(
            "Freqs A.",
            ui.output_plot(FREQ_A_PLOT_ID),
        ),
        ui.nav_panel(
            "Exp. hets.",
            ui.output_plot(EXP_HET_PLOT_ID),
        ),
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

    def calc_hw_freqs(freq_A):
        freq_a = 1 - freq_A
        freq_AA = freq_A**2
        freq_Aa = 2 * freq_A * freq_a
        freq_aa = freq_a**2
        return freq_AA, freq_Aa, freq_aa

    @reactive.calc
    @reactive.event(input.run_button)
    def do_simulation():
        pop_a_freq_A = input.pop_a_freq_A_slider()
        pop_b_freq_A = input.pop_b_freq_A_slider()
        pop_a_freq_AA, pop_a_freq_Aa, pop_a_freq_aa = calc_hw_freqs(pop_a_freq_A)
        pop_b_freq_AA, pop_b_freq_Aa, pop_b_freq_aa = calc_hw_freqs(pop_b_freq_A)

        pop_a_wAA = input.pop_a_wAA_slider()
        pop_a_wAa = input.pop_a_wAa_slider()
        pop_a_waa = input.pop_a_waa_slider()
        pop_b_wAA = input.pop_b_wAA_slider()
        pop_b_wAa = input.pop_b_wAa_slider()
        pop_b_waa = input.pop_b_waa_slider()

        pop_size = get_pop_size()
        num_generations = input.num_gen_slider()

        sim_params = {
            "pops": {
                "pop_a": {
                    "genotypic_freqs": (pop_a_freq_AA, pop_a_freq_Aa, pop_a_freq_aa),
                    "size": pop_size,
                },
                "pop_b": {
                    "genotypic_freqs": (pop_b_freq_AA, pop_b_freq_Aa, pop_b_freq_aa),
                    "size": pop_size,
                },
            },
            "num_generations": num_generations,
            "loggers": [
                "allelic_freqs_logger",
                "exp_het_logger",
            ],
        }

        sim_params["pops"]["pop_a"]["fitness"] = (
            pop_a_wAA,
            pop_a_wAa,
            pop_a_waa,
        )
        sim_params["pops"]["pop_b"]["fitness"] = (
            pop_b_wAA,
            pop_b_wAa,
            pop_b_waa,
        )

        migration_a_b = {
            "type": "migration_start",
            "from_pop": "pop_b",
            "to_pop": "pop_a",
            "inmigrant_rate": input.pop_a_immigration_slider(),
            "num_generation": 1,
        }
        migration_b_a = {
            "type": "migration_start",
            "from_pop": "pop_a",
            "to_pop": "pop_b",
            "inmigrant_rate": input.pop_b_immigration_slider(),
            "num_generation": 1,
        }
        sim_params["demographic_events"] = {
            "migration_pop_a_to_pop_b": migration_a_b,
            "migration_pop_b_to_pop_a": migration_b_a,
        }

        sim = OneLocusTwoAlleleSimulation(sim_params)
        return sim

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

    @render.plot(alt="Expected heterozygosities")
    def exp_het_plot():
        sim = do_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Expected heterozygosities")
        axes.set_xlabel("generation")
        axes.set_ylabel("exp. het.")

        freqs_series = sim.results["expected_hets"]
        axes.plot(freqs_series.index, freqs_series.values, label="Freq. A")
        axes.set_ylim((0, 1))
        return fig
