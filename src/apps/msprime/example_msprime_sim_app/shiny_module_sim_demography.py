from shiny import ui, module, reactive

import msprime
import msprime_sim_utils

MIN_POP_SIZE = 10
MAX_POP_SIZE = 100000
DEF_POP_SIZE = 10000

POP_SIZE_ACCORDION_ID = "Population size"


@module.ui
def demography_input_accordions():
    pop_size_panel = (
        ui.input_slider(
            "pop_size",
            label="Population size",
            min=MIN_POP_SIZE,
            max=MAX_POP_SIZE,
            value=DEF_POP_SIZE,
            width="100%",
        ),
    )

    accordion_panels = [
        ui.accordion_panel(POP_SIZE_ACCORDION_ID, pop_size_panel),
    ]
    return accordion_panels


open_accordion_panels = [POP_SIZE_ACCORDION_ID]


@module.server
def demography_server(input, output, session, get_msprime_params):
    def get_pop_name():
        return "pop"

    @reactive.calc
    def get_pop_size():
        return input.pop_size()

    @reactive.calc
    def get_demography():
        demography = msprime.Demography()
        pop_name = get_pop_name()
        demography.add_population(
            name=pop_name, initial_size=get_pop_size(), initially_active=True
        )
        params = {
            "Pop. size": get_pop_size(),
        }

        return {"demography": demography, "params_for_table": params}

    @reactive.calc
    def get_sample_sets():
        pop_name = get_pop_name()

        sampling_times = [
            100,
            50,
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
