from shiny import App, reactive, render, ui
import pandas

import ruamel.yaml
import msprime

import msprime_utils


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

MIN_POP_SIZE = 10
MAX_POP_SIZE = 100000
DEF_POP_SIZE = 10000
DEF_BOTTLENECK_SIZE = 100

MIN_NUM_GENERATIONS_AGO = -1000
MAX_NUM_GENERATIONS_AGO = -10
DEF_NUM_GENERATIONS_AGO = [-100, -50]

SUMMARY_TABLE_ID = "summary_table"
RESULT_TABLE_ID = "results_table"

pop_size_panel = (
    (
        ui.input_slider(
            "pop_size_before_slider",
            label="Before",
            min=MIN_POP_SIZE,
            max=MAX_POP_SIZE,
            value=DEF_POP_SIZE,
            width="100%",
        ),
        ui.input_slider(
            "pop_size_during_slider",
            label="During the bottleneck",
            min=MIN_POP_SIZE,
            max=MAX_POP_SIZE,
            value=DEF_BOTTLENECK_SIZE,
            width="100%",
        ),
        ui.input_slider(
            "pop_size_after_slider",
            label="After",
            min=MIN_POP_SIZE,
            max=MAX_POP_SIZE,
            value=DEF_POP_SIZE,
            width="100%",
        ),
    ),
)

bottleneck_duration_panel = (
    (
        ui.input_slider(
            "bottleneck_duration",
            label="Bottleneck duration (Num. generations ago)",
            min=MIN_NUM_GENERATIONS_AGO,
            max=MAX_NUM_GENERATIONS_AGO,
            value=DEF_NUM_GENERATIONS_AGO,
            width="100%",
        ),
    ),
)

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
    ui.accordion_panel("Bottleneck duration", bottleneck_duration_panel),
    ui.accordion_panel("Population size", pop_size_panel),
    ui.accordion_panel("Sample size (num. individuals to sample)", sample_size_panel),
    ui.accordion_panel(
        "Recombination rate (per base pair and generation)", recomb_panel
    ),
    ui.accordion_panel("Mutation rate (per base pair and generation)", mut_panel),
    id="inputs_panel",
    open=["Bottleneck duration", "Population size"],
)

run_button = ui.input_action_button("run_button", "Run simulation")

input_card = ui.card(
    ui.h1("Bottleneck"),
    ui.card(inputs_panel),
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

output_panels = (ui.nav_panel("Summary", summary),)

output_card = ui.card(
    ui.navset_tab(
        *output_panels,
    )
)

app_ui = ui.page_fixed(
    input_card,
    output_card,
    lang="en",
)


def server(input, output, session):

    @reactive.calc
    def get_sample_size():
        return input.sample_size_slider()

    @reactive.calc
    def get_pop_size_before():
        return input.pop_size_before_slider()

    @reactive.calc
    def get_pop_size_during():
        return input.pop_size_during_slider()

    @reactive.calc
    def get_pop_size_after():
        return input.pop_size_after_slider()

    @reactive.calc
    def get_bottleneck_start():
        return -input.bottleneck_duration()[1]

    @reactive.calc
    def get_bottleneck_end():
        return -input.bottleneck_duration()[0]

    @reactive.calc
    @reactive.event(input.run_button)
    def do_simulation():
        demography = msprime.Demography()
        pop_name = "pop"
        start_time = get_bottleneck_start()
        end_time = get_bottleneck_end()
        demography.add_population(
            name=pop_name, initial_size=get_pop_size_before(), initially_active=True
        )
        demography.add_population_parameters_change(
            time=start_time, initial_size=get_pop_size_during()
        )
        demography.add_population_parameters_change(
            time=end_time, initial_size=get_pop_size_after()
        )

        sampling_times = [
            start_time - 10,
            start_time + 1,
            start_time - 1,
            int((end_time + start_time) / 2),
            end_time + 1,
            end_time - 1,
            0,
        ]

        num_indis_to_sample = get_sample_size()
        samplings = []
        for time in sampling_times:
            sampling = msprime_utils.create_msprime_sampling(
                num_samples=num_indis_to_sample, ploidy=2, pop_name=pop_name, time=time
            )
            samplings.append(sampling)

        sim_res = msprime_utils.simulate(
            samplings, demography=demography, seq_length_in_bp=1e4, random_seed=42
        )
        return sim_res

    @render.data_frame
    def summary_table():
        parameters = ["hola"]
        values = ["caracola"]
        df = pandas.DataFrame({"Parameter": parameters, "Value": values})
        return render.DataGrid(df)

    @reactive.calc
    def get_exp_hets():
        sim_res = do_simulation()
        exp_hets = sim_res.calc_unbiased_exp_het()
        samplings = sim_res.sampling_info
        times = [
            -samplings[sampling_name]["sampling_time"]
            for sampling_name in exp_hets.index
        ]
        exp_hets.index = times
        exp_hets.sort_index(inplace=True)

        return exp_hets

    @render.data_frame
    def results_table():

        exp_hets = get_exp_hets()
        results_table = Table.from_series(
            exp_hets, index_name="Generation", col_name="Exp. Het."
        )

        return render.DataGrid(results_table.df)


class Table:
    def __init__(self, col_names: list[str]):
        self.col_names = col_names
        self._cols = {col: [] for col in col_names}

    def add_row(self, row: dict):
        for col_name, col in self._cols.items():
            col.append(row[col_name])

    @classmethod
    def from_series(cls, series: pandas.Series, index_name: str, col_name: str):
        table = cls([index_name, col_name])
        for index, value in series.items():
            table.add_row({index_name: index, col_name: value})
        return table

    @property
    def df(self):
        return pandas.DataFrame(self._cols)


app = App(app_ui, server)
