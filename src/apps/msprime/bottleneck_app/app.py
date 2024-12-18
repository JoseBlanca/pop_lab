from shiny import App, ui

from shiny_modules_general_msprime import (
    msprime_params_ui,
    msprime_params_server,
    input_params_tabs,
    run_simulation_ui,
    input_params_server,
    run_simulation_server,
)
from shiny_module_sim_demography import (
    demography_input_accordions,
    demography_server,
    open_accordion_panels,
)

TITLE = "Bottleneck"
MSPRIME_MODULE_ID = "msprime"
DEMOGRAPHY_MODULE_ID = "demography"
INPUT_PARAMS_MODULE_ID = "input_params"
RUM_SIM_ID = "run_sim"

inputs_accordions = []
inputs_accordions.extend(demography_input_accordions(DEMOGRAPHY_MODULE_ID))
inputs_accordions.extend(msprime_params_ui(MSPRIME_MODULE_ID))
input_accordion = ui.accordion(
    *inputs_accordions,
    id="inputs_panel",
    open=open_accordion_panels,
)

page_elements = [ui.h1(TITLE), input_accordion]
page_elements.append(input_params_tabs(INPUT_PARAMS_MODULE_ID))
run_sim_elements = run_simulation_ui(RUM_SIM_ID)
page_elements.extend(run_sim_elements)
app_ui = ui.page_fixed(
    *page_elements,
    lang="en",
)


def server(input, output, session):
    get_msprime_params = msprime_params_server(MSPRIME_MODULE_ID)
    get_demography, get_sample_sets = demography_server(
        DEMOGRAPHY_MODULE_ID, get_msprime_params=get_msprime_params
    )
    input_params_server(
        INPUT_PARAMS_MODULE_ID,
        get_demography=get_demography,
        get_msprime_params=get_msprime_params,
    )
    run_simulation_server(
        RUM_SIM_ID,
        get_sample_sets=get_sample_sets,
        get_demography=get_demography,
        get_msprime_params=get_msprime_params,
    )


app = App(app_ui, server)
