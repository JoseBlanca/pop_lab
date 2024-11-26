from shiny import ui, module, reactive

import msprime
import msprime_sim_utils

MIN_POP_SIZE = 10
MAX_POP_SIZE = 100000
DEF_POP_SIZE = 10000
DEF_BOTTLENECK_SIZE = 100

MIN_NUM_GENERATIONS_AGO = -1000
MAX_NUM_GENERATIONS_AGO = -10
DEF_NUM_GENERATIONS_AGO = [-100, -50]
BOTTLENECK_ACCORDION_ID = "Bottleneck duration"
POP_SIZE_ACCORDION_ID = "Population size"

POP_NAME = "pop"
POP_NAMES = [POP_NAME]


@module.ui
def demography_input_accordions():
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
    accordion_panels = [
        ui.accordion_panel(BOTTLENECK_ACCORDION_ID, bottleneck_duration_panel),
        ui.accordion_panel(POP_SIZE_ACCORDION_ID, pop_size_panel),
    ]
    return accordion_panels


open_accordion_panels = [BOTTLENECK_ACCORDION_ID, POP_SIZE_ACCORDION_ID]


@module.server
def demography_server(input, output, session, get_msprime_params):
    def get_pop_name():
        return POP_NAME

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
    def get_demography():
        demography = msprime.Demography()
        pop_name = get_pop_name()
        start_time = get_bottleneck_start()
        end_time = get_bottleneck_end()
        demography.add_population(
            name=pop_name, initial_size=get_pop_size_after(), initially_active=True
        )
        demography.add_population_parameters_change(
            time=start_time, initial_size=get_pop_size_during()
        )
        demography.add_population_parameters_change(
            time=end_time, initial_size=get_pop_size_before()
        )
        params = {
            "Pop. size before bottleneck": get_pop_size_before(),
            "Pop. size during bottleneck": get_pop_size_during(),
            "Pop. size after bottleneck": get_pop_size_after(),
            "Bottleneck start (generations ago)": get_bottleneck_end(),
            "Bottleneck end (generations ago)": get_bottleneck_start(),
        }

        return {"demography": demography, "params_for_table": params}

    @reactive.calc
    def get_sample_sets():
        pop_name = get_pop_name()
        start_time = get_bottleneck_start()
        end_time = get_bottleneck_end()

        sampling_times = [
            start_time - 10,
            start_time + 1,
            start_time - 1,
            int((end_time + start_time) / 2),
            end_time + 1,
            end_time - 1,
            0,
        ]

        num_indis_to_sample = get_msprime_params()["sample_size"]
        sample_sets = []
        for time in sampling_times:
            sample_set = msprime_sim_utils.create_msprime_sample_set(
                num_samples=num_indis_to_sample, ploidy=2, pop_name=pop_name, time=time
            )
            sample_sets.append(sample_set)
        return sample_sets

    return get_demography, get_sample_sets
