from shiny import App, reactive, render, ui, module

APP_ID = "one_locus_app"
MAX_MUTATION_RATE = 0.1


def set_config_defaults(config: dict):
    config.setdefault("title", "One locus two alleles simulation")

    if "pops" not in config:
        config["pops"] = {"pop": {}}

    pops_config = {}
    for idx, pop_name in enumerate(config["pops"].keys()):
        pop_id = f"pop_{idx}"
        pop_config = {}
        pop_config["name"] = pop_name
        if (
            "freq_A" in config["pops"][pop_name]
            and "genotypic_freqs" in config["pops"][pop_id]
        ):
            raise ValueError(
                'Either "freq_A" or "genotypic_freqs" can be set, but not both'
            )
        elif "freq_A" in config["pops"][pop_name]:
            pop_config["freq_A"] = config["pops"][pop_name]["freq_A"]
        elif "genotypic_freqs" in config["pops"][pop_name]:
            pop_config["genotypic_freqs"] = config["pops"][pop_name]["genotypic_freqs"]
        else:
            pop_config["freq_A"] = 0.5
        pop_config["ui_freq_options"] = config["pops"][pop_name].get(
            "ui_freq_options", ("genotypic", "allelic")
        )
        pop_config.setdefault("size", {"min": 10, "max": 200, "value": 100})
        pops_config[pop_id] = pop_config

    config["pops"] = pops_config

    config.setdefault("num_generations", {"min": 10, "max": 200, "value": 100})
    # the panels shown will be the loggers chosen
    config.setdefault(
        "loggers",
        (
            "allelic_freqs_logger",
            "genotypic_freqs_logger",
            "exp_het_logger",
        ),
    )


def create_num_gen_panel(config):
    slider = ui.input_slider(
        id="num_gen_slider",
        label="",
        min=config["num_generations"]["min"],
        max=config["num_generations"]["max"],
        value=config["num_generations"]["value"],
        width="100%",
    )
    panel = ui.accordion_panel("Num. generations", slider)
    return panel


def create_allelic_freqs_panel():
    plot = ui.output_plot("allelic_freqs_plot")
    panel = ui.nav_panel("Allelic Freqs.", plot)
    return panel


def create_genotypic_freqs_panel():
    plot = ui.output_plot("genotypic_freqs_plot")
    panel = ui.nav_panel("Genotypic Freqs.", plot)
    return panel


def create_exp_het_panel():
    plot = ui.output_plot("exp_het_plot")
    panel = ui.nav_panel("Expected het.", plot)
    return panel


def create_simulation_output_card(config):
    loggers = config["loggers"]
    panels = []
    if "allelic_freqs_logger" in loggers:
        panels.append(create_allelic_freqs_panel())
    if "allelic_freqs_logger" in loggers:
        panels.append(create_genotypic_freqs_panel())
    if "exp_het_logger" in loggers:
        panels.append(create_exp_het_panel())

    navset_tab = ui.navset_tab(*panels, id="output_navset")
    card = ui.card(navset_tab)
    return card


def create_freqs_panel(pop_config):
    if "genotypic_freqs" in pop_config:
        geno_freqs = pop_config["genotypic_freqs"]
        freq_AA, freq_Aa, freq_aa = geno_freqs
        freq_A = freq_AA + freq_Aa * 0.5
    elif "freq_A" in pop_config:
        freq_A = pop_config["freq_A"]
        freq_AA = freq_A**2
        freq_a = 1 - freq_A
        freq_aa = freq_a**2
        freq_Aa = 1 - freq_AA - freq_aa
        geno_freqs = (freq_AA, freq_Aa, freq_aa)
    else:
        raise ValueError(
            "Either genotypic_freqs or freq_A should be defined in the pop config"
        )

    ui_options = pop_config["ui_freq_options"]

    freq_a_slider = ui.input_slider(
        id="freq_a_slider",
        label="Freq. A",
        min=0,
        max=1,
        value=freq_A,
        width="100%",
    )

    geno_freqs_slider = ui.input_slider(
        id="geno_freqs_slider",
        label="Geno. freqs. (AA, Aa, aa)",
        min=0,
        max=1,
        value=[freq_AA, freq_AA + freq_Aa],
        width="100%",
    )

    if "genotypic" in ui_options and "allelic" in ui_options:
        allelic_panel = ui.nav_panel("With HW", freq_a_slider)
        genotypic_panel = ui.nav_panel("No HW", geno_freqs_slider)
        freqs_ui = ui.navset_tab(
            allelic_panel,
            genotypic_panel,
            id="freqs_tabs",
        )
    elif "genotypic" in ui_options:
        freqs_ui = freq_a_slider
    elif "allelic" in ui_options:
        freqs_ui = geno_freqs_slider
    else:
        raise ValueError(
            f"Either genotypic, allelic or both should be in the pop {pop_config['name']} ui_options"
        )

    genotypic_freqs = ui.layout_columns(
        ui.value_box(
            title="Freq. AA",
            value=ui.output_ui("freq_AA_output"),
            id="freq_AA_value_box",
        ),
        ui.value_box(
            "Freq. Aa",
            ui.output_ui("freq_Aa_output"),
            id="freq_Aa_value_box",
        ),
        ui.value_box(
            "Freq. aa",
            ui.output_ui("freq_aa_output"),
            id="freq_aa_value_box",
        ),
    )

    panel = ui.accordion_panel("Initial freqs.", freqs_ui, genotypic_freqs)
    return panel


def create_pop_size_panel(pop_config):
    size_slider = ui.input_slider(
        id="size_slider",
        label="",
        min=pop_config["size"]["min"],
        max=pop_config["size"]["max"],
        value=pop_config["size"]["value"],
        width="100%",
    )
    panel = ui.accordion_panel("Size", size_slider)
    return panel


def create_selection_panel(pop_config):
    fitness = pop_config["fitness"]
    wAA_slider = ui.input_slider(
        id="wAA_slider",
        label="wAA",
        min=0,
        max=1,
        value=fitness["wAA"],
        width="100%",
    )
    wAa_slider = ui.input_slider(
        id="wAa_slider",
        label="wAa",
        min=0,
        max=1,
        value=fitness["wAa"],
        width="100%",
    )
    waa_slider = ui.input_slider(
        id="waa_slider",
        label="waa",
        min=0,
        max=1,
        value=fitness["waa"],
        width="100%",
    )
    panel = ui.accordion_panel(
        "Selection (Fitness)", wAA_slider, wAa_slider, waa_slider
    )
    return panel


def create_mutation_panel(pop_config):
    mutation = pop_config["mutation"]
    A2a_slider = ui.input_slider(
        id="A2a_slider",
        label="A2a rate",
        min=0,
        max=MAX_MUTATION_RATE,
        value=mutation["A2a"],
        width="100%",
    )
    a2A_slider = ui.input_slider(
        id="a2A_slider",
        label="a2A rate",
        min=0,
        max=MAX_MUTATION_RATE,
        value=mutation["a2A"],
        width="100%",
    )
    panel = ui.accordion_panel("Mutation", A2a_slider, a2A_slider)
    return panel


def create_selfing_rate_panel(pop_config):
    slider = ui.input_slider(
        id="selfing_slider",
        label="",
        min=0,
        max=1,
        value=pop_config["selfing_rate"],
        width="100%",
    )
    panel = ui.accordion_panel("Selfing rate", slider)
    return panel


@module.ui
def create_pop_accordion(pop_config):
    freqs_panel = create_freqs_panel(pop_config)
    size_panel = create_pop_size_panel(pop_config)
    panels = [freqs_panel, size_panel]
    if "fitness" in pop_config:
        selection_panel = create_selection_panel(pop_config)
        panels.append(selection_panel)
    if "mutation" in pop_config:
        mutation_panel = create_mutation_panel(pop_config)
        panels.append(mutation_panel)
    if "selfing_rate" in pop_config:
        selfing_rate_panel = create_selfing_rate_panel(pop_config)
        panels.append(selfing_rate_panel)

    pop_accordion = ui.accordion(
        *panels,
        id="pop_accordion",
        title=pop_config["name"],
    )
    return pop_accordion


@module.server
def pop_input_server(input, output, session):
    @reactive.calc
    def calc_geno_allelic_freqs():
        selected_tab = input.freqs_tabs.get()
        if selected_tab == "With HW":
            freq_A = input.freq_a_slider()
            freq_a = 1 - freq_A
            freq_AA = freq_A**2
            freq_aa = freq_a**2
            freq_Aa = 1 - freq_AA - freq_aa
        else:
            freq_AA, freq_AA_Aa = input.geno_freqs_slider()
            freq_Aa = freq_AA_Aa - freq_AA
            freq_aa = 1 - freq_AA_Aa
            freq_A = freq_AA + freq_Aa * 0.5
        return freq_AA, freq_Aa, freq_aa, freq_A

    @render.text
    def freq_AA_output():
        freq = calc_geno_allelic_freqs()[0]
        return f"{freq:.2f}"

    @render.text
    def freq_Aa_output():
        freq = calc_geno_allelic_freqs()[1]
        return f"{freq:.2f}"

    @render.text
    def freq_aa_output():
        freq = calc_geno_allelic_freqs()[2]
        return f"{freq:.2f}"


def create_pops_panel(config):
    tabs = []
    for pop_idx in sorted(config["pops"].keys()):
        pop_config = config["pops"][pop_idx]
        pop_module_id = f"module_pop_{pop_idx}"
        print(pop_module_id)
        pop_accordion = create_pop_accordion(pop_module_id, pop_config)
        pop_name = pop_config["name"]
        tab = ui.nav_panel(pop_name, pop_accordion)
        tabs.append(tab)

    if len(tabs) > 1:
        nav_panel = ui.navset_tab(*tabs, id="Populations")
        accordion_panel = ui.accordion_panel("Populations", nav_panel)
    else:
        accordion_panel = ui.accordion_panel(pop_name, pop_accordion)

    return accordion_panel


def create_simulation_input_card(config):
    pops_panel = create_pops_panel(config)
    num_gen_panel = create_num_gen_panel(config)
    input_accordion = ui.accordion(
        pops_panel, num_gen_panel, id="num_generations_accordion"
    )
    run_button = ui.input_action_button("run_button", "Run simulation")

    card = ui.card(input_accordion, run_button)
    return card


def app_ui(request):
    print(request)
    config = {}
    set_config_defaults(config)
    if True:
        # if selfing rate is given the selfing rate accordion will be shown
        config["pops"]["pop_0"]["selfing_rate"] = 0
    if True:
        # if fitness is given the selection accordion will be shown
        config["pops"]["pop_0"]["fitness"] = {"wAA": 1, "wAa": 1, "waa": 0.5}
    if True:
        config["pops"]["pop_0"]["mutation"] = {"a2A": 0.01, "A2a": 0.01}

    print(config)

    input_card = create_simulation_input_card(config)
    output_card = create_simulation_output_card(config)

    page = ui.page_fixed(ui.h1(config["title"]), input_card, output_card)
    return page


def server(input, output, session):
    pop_id = "pop_0"
    module_id = f"module_pop_{pop_id}"
    print(module_id)
    pop_input_server(module_id)


app = App(app_ui, server)