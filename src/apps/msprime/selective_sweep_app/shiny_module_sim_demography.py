from shiny import ui, module, reactive

import msprime
import msprime_sim_utils

MIN_POP_SIZE = 10
MAX_POP_SIZE = 10000
DEF_POP_SIZE = 500

MAX_ANCESTRAL_SPLIT_GENERATION = 3000
MIN_ANCESTRAL_SPLIT_GENERATION = 200
DEF_ANCESTRAL_SPLIT_GENERATION = 2500

MAX_ADMIX_GENERATION = MIN_ANCESTRAL_SPLIT_GENERATION - 50
MIN_ADMIX_GENERATION = 10
DEF_ADMIX_GENERATION = 10

MIN_POP_A_PROPORTION = 0
MAX_POP_A_PROPORTION = 1
DEF_POP_A_PROPORTION = 0.5

NUM_POPS = 3
POP_NAMES = ["pop"]

ORIG_POP_SIZE_ACCORDION_ID = "Orig population size"
NUM_SPLIT_GENERATION_AGO_ID = "Times"
POP_SIZE_ACCORDION_ID = "Split population sizes"
NUM_POPS_ACCORDION_ID = "Num. populations"


@module.ui
def demography_input_accordions():
    pop_a_proportion_slider = ui.input_slider(
        "pop_a_proportion_slider",
        label="Proportion of pop. A in the admixture",
        min=MIN_POP_A_PROPORTION,
        max=MAX_POP_A_PROPORTION,
        value=DEF_POP_A_PROPORTION,
        width="100%",
    )

    admix_generation_slider = ui.input_slider(
        "admix_generation_slider",
        label="Admix. pop. creation time",
        min=MIN_ADMIX_GENERATION,
        max=MAX_ADMIX_GENERATION,
        value=DEF_ADMIX_GENERATION,
        width="100%",
    )

    ancestral_split_generation_slider = ui.input_slider(
        "ancestral_split_generation_slider",
        label="Pop. A and Pop. B split time",
        min=MIN_ANCESTRAL_SPLIT_GENERATION,
        max=MAX_ANCESTRAL_SPLIT_GENERATION,
        value=DEF_ANCESTRAL_SPLIT_GENERATION,
        width="100%",
    )

    pop_size_slider = ui.input_slider(
        "pop_size_slider",
        label="population sizes",
        min=MIN_POP_SIZE,
        max=MAX_POP_SIZE,
        value=DEF_POP_SIZE,
        width="100%",
    )

    accordion_panels = [
        ui.accordion_panel(
            "Simulation parameters",
            pop_a_proportion_slider,
            admix_generation_slider,
            ancestral_split_generation_slider,
            pop_size_slider,
        ),
    ]
    return accordion_panels


open_accordion_panels = [POP_SIZE_ACCORDION_ID, NUM_SPLIT_GENERATION_AGO_ID]


@module.server
def demography_server(input, output, session, get_msprime_params):
    @reactive.calc
    def get_demography():
        pop_size = input.pop_size_slider()
        sweep_mod_time = 200
        seq_length = 2e6

        demography = msprime.Demography()
        demography.add_population(name="pop", initial_size=pop_size)

        start_frequency = 1.0 / (2 * pop_size)
        end_frequency = 1.0 - (1.0 / (2 * pop_size))
        s = 1
        # dt is the small increment of time for stepping through the sweep phase of the model.
        # a good rule of thumb is for this to be approximately or smaller
        dt = 1e-6

        # The strength of selection during the sweep is determined by the parameter s
        # Here we define s such that the fitness of the three genotypes at our beneficial locus are
        # wBB = 1, wBb = 1 + s/2, wbb = 1+s
        mod = msprime.SweepGenicSelection(
            position=int(seq_length * 0.5),
            start_frequency=start_frequency,
            end_frequency=end_frequency,
            s=s,
            dt=dt,
        )
        mod_list = [mod, msprime.StandardCoalescent(duration=sweep_mod_time)]
        # append final model
        mod_list.append("hudson")

        return {"demography": demography, "model": mod_list}

    @reactive.calc
    def get_sample_sets():
        admix_generation = input.admix_generation_slider()
        sampling_times = [0]

        num_indis_to_sample = get_msprime_params()["sample_size"]
        sample_sets = []
        for time in sampling_times:
            for pop in ["pop"]:
                sample_set = msprime_sim_utils.create_msprime_sample_set(
                    num_samples=num_indis_to_sample,
                    ploidy=2,
                    pop_name=pop,
                    time=time,
                )
                sample_sets.append(sample_set)
        return sample_sets

    return get_demography, get_sample_sets
