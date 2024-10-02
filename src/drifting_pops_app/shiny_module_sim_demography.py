from shiny import ui, module, reactive

import msprime
import msprime_sim_utils

MIN_POP_SIZE = 10
MAX_POP_SIZE = 100000
DEF_POP_SIZE = 100

MIN_GENERATION_POP_SPLIT = 10
MAX_GENERATION_POP_SPLIT = 1000
DEF_GENERATION_POP_SPLIT = 400

NUM_POPS = 3

ORIG_POP_SIZE_ACCORDION_ID = "Orig population size"
NUM_SPLIT_GENERATION_AGO_ID = "Num. generations ago pop. split"
POP_SIZE_ACCORDION_ID = "Split population sizes"
NUM_POPS_ACCORDION_ID = "Num. populations"


def create_pop_size_sliders(num_pops):
    pop_size_sliders = [
        ui.input_slider(
            f"pop_{pop_idx}_size",
            label=f"Population {pop_idx} size",
            min=MIN_POP_SIZE,
            max=MAX_POP_SIZE,
            value=DEF_POP_SIZE,
            width="100%",
        )
        for pop_idx in range(1, num_pops + 1)
    ]
    return pop_size_sliders


@module.ui
def demography_input_accordions():
    orig_pop_size_slider = ui.input_slider(
        "ancestral_pop_size_slider",
        label="Population size before split",
        min=MIN_POP_SIZE,
        max=MAX_POP_SIZE,
        value=DEF_POP_SIZE,
        width="100%",
    )

    pop_size_sliders = create_pop_size_sliders(NUM_POPS)
    pop_size_panel = [orig_pop_size_slider] + pop_size_sliders

    num_generation_ago_split_slider = ui.input_slider(
        "num_generations_ago_split",
        label="Num. generations ago split",
        min=MIN_GENERATION_POP_SPLIT,
        max=MAX_GENERATION_POP_SPLIT,
        value=DEF_GENERATION_POP_SPLIT,
        width="100%",
    )

    accordion_panels = [
        ui.accordion_panel(POP_SIZE_ACCORDION_ID, pop_size_panel),
        ui.accordion_panel(
            NUM_SPLIT_GENERATION_AGO_ID, num_generation_ago_split_slider
        ),
    ]
    return accordion_panels


open_accordion_panels = [POP_SIZE_ACCORDION_ID, NUM_SPLIT_GENERATION_AGO_ID]


@module.server
def demography_server(input, output, session, get_msprime_params):
    @reactive.calc
    def get_pop_sizes():
        pop_sizes_getters = {
            1: input.pop_1_size,
            2: input.pop_2_size,
            3: input.pop_3_size,
            4: input.pop_4_size,
            5: input.pop_5_size,
            6: input.pop_6_size,
            7: input.pop_7_size,
            8: input.pop_8_size,
            9: input.pop_9_size,
            10: input.pop_10_size,
        }

        pop_sizes = {
            f"pop_{pop_idx}": pop_sizes_getters[pop_idx]()
            for pop_idx in range(1, NUM_POPS + 1)
        }
        return pop_sizes

    @reactive.calc
    def get_demography():
        demography = msprime.Demography()
        pop_sizes = get_pop_sizes()
        pops = sorted(pop_sizes.keys())
        params = {}
        for pop_name in pops:
            size = pop_sizes[pop_name]
            demography.add_population(
                name=pop_name, initial_size=size, initially_active=True
            )
            params[f"{pop_name} size"] = size

        ancestral_pop = pops.pop(0)
        derived_pops = pops
        num_generations_ago_when_split_happened = input.num_generations_ago_split()
        demography.add_population_split(
            num_generations_ago_when_split_happened,
            derived=derived_pops,
            ancestral=ancestral_pop,
        )
        demography.add_population_parameters_change(
            time=num_generations_ago_when_split_happened,
            initial_size=input.ancestral_pop_size_slider(),
            population="pop_1",
        )

        return {"demography": demography, "params_for_table": params}

    @reactive.calc
    def get_sample_sets():
        split_time = input.num_generations_ago_split()

        sampling_times = [
            split_time - 1,
            split_time // 2,
            0,
        ]

        pop_names = sorted(get_pop_sizes().keys())

        num_indis_to_sample = get_msprime_params()["sample_size"]
        sample_sets = []
        for time in sampling_times:
            for pop_name in pop_names:
                sample_set = msprime_sim_utils.create_msprime_sample_set(
                    num_samples=num_indis_to_sample,
                    ploidy=2,
                    pop_name=pop_name,
                    time=time,
                )
                sample_sets.append(sample_set)
        return sample_sets

    return get_demography, get_sample_sets
