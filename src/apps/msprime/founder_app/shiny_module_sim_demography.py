from shiny import ui, module, reactive

import msprime
import msprime_sim_utils

MIN_POP_SIZE = 10
MAX_POP_SIZE = 10000
DEF_POP_SIZE = 500

MIN_GENERATION_POP_SPLIT = 100
MAX_GENERATION_POP_SPLIT = 1000
DEF_GENERATION_POP_SPLIT = 400

MIN_NUM_FOUNDER_INDIS = 10
MAX_NUM_FOUNDER_INDIS = 1000
DEF_NUM_FOUNDER_INDIS = 50

MIN_BOTTLENECK_DURATION = 0
MAX_BOTTLENECK_DURATION = MIN_GENERATION_POP_SPLIT
DEF_BOTTLENECK_DURATION = 10

NUM_POPS = 2
POP_NAMES = ["orig_pop", "split_pop"]

ORIG_POP_SIZE_ACCORDION_ID = "Orig population size"
NUM_SPLIT_GENERATION_AGO_ID = "Times"
POP_SIZE_ACCORDION_ID = "Split population sizes"
NUM_POPS_ACCORDION_ID = "Num. populations"


@module.ui
def demography_input_accordions():
    orig_pop_size_slider = ui.input_slider(
        "original_pop_size_slider",
        label="Original population size",
        min=MIN_POP_SIZE,
        max=MAX_POP_SIZE,
        value=DEF_POP_SIZE,
        width="100%",
    )

    num_founder_indis_slider = ui.input_slider(
        "num_founder_indis_slider",
        label="Num. founder individuals",
        min=MIN_NUM_FOUNDER_INDIS,
        max=MAX_NUM_FOUNDER_INDIS,
        value=DEF_NUM_FOUNDER_INDIS,
        width="100%",
    )

    split_pop_size_slider = ui.input_slider(
        "split_pop_size_slider",
        label="Split population final size",
        min=MIN_POP_SIZE,
        max=MAX_POP_SIZE,
        value=DEF_POP_SIZE,
        width="100%",
    )

    pop_size_panel = [
        orig_pop_size_slider,
        num_founder_indis_slider,
        split_pop_size_slider,
    ]

    num_generation_ago_split_slider = ui.input_slider(
        "num_generations_ago_split",
        label="Num. generations ago pop. split",
        min=MIN_GENERATION_POP_SPLIT,
        max=MAX_GENERATION_POP_SPLIT,
        value=DEF_GENERATION_POP_SPLIT,
        width="100%",
    )

    bottleneck_duration_slider = ui.input_slider(
        "bottleneck_duration_slider",
        label="Bottleneck duration",
        min=MIN_BOTTLENECK_DURATION,
        max=MAX_BOTTLENECK_DURATION,
        value=DEF_BOTTLENECK_DURATION,
        width="100%",
    )

    accordion_panels = [
        ui.accordion_panel(POP_SIZE_ACCORDION_ID, pop_size_panel),
        ui.accordion_panel(
            NUM_SPLIT_GENERATION_AGO_ID,
            num_generation_ago_split_slider,
            bottleneck_duration_slider,
        ),
    ]
    return accordion_panels


open_accordion_panels = [POP_SIZE_ACCORDION_ID, NUM_SPLIT_GENERATION_AGO_ID]


@module.server
def demography_server(input, output, session, get_msprime_params):
    @reactive.calc
    def get_demography():
        orig_pop_size = input.original_pop_size_slider()
        num_founders = input.num_founder_indis_slider()
        split_pop_size = input.split_pop_size_slider()
        founding_time = input.num_generations_ago_split()
        bottleneck_time = input.bottleneck_duration_slider()

        demography = msprime.Demography()
        demography.add_population(
            name="orig_pop", initial_size=orig_pop_size, initially_active=True
        )
        demography.add_population(
            name="split_pop", initial_size=split_pop_size, initially_active=True
        )

        time_full_size = founding_time - bottleneck_time
        demography.add_population_parameters_change(
            time=time_full_size,
            initial_size=num_founders,
            population="split_pop",
        )
        demography.add_population_split(
            founding_time,
            derived=["split_pop"],
            ancestral="orig_pop",
        )

        return {"demography": demography}

    @reactive.calc
    def get_sample_sets():
        bottleneck_duration = input.bottleneck_duration_slider()
        founding_time = input.num_generations_ago_split()
        time_full_size = founding_time - bottleneck_duration
        sampling_times = [
            founding_time - 1,
            time_full_size + 1,
            time_full_size - 1,
            0,
        ]

        num_indis_to_sample = get_msprime_params()["sample_size"]
        sample_sets = []
        for time in sampling_times:
            for pop in ["orig_pop", "split_pop"]:
                sample_set = msprime_sim_utils.create_msprime_sample_set(
                    num_samples=num_indis_to_sample,
                    ploidy=2,
                    pop_name=pop,
                    time=time,
                )
                sample_sets.append(sample_set)
        return sample_sets

    return get_demography, get_sample_sets
