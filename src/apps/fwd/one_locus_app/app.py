import math

from shiny import App, reactive, render, ui, module
import matplotlib.pyplot as plt

from one_locus_two_alleles_simulator import OneLocusTwoAlleleSimulation, INF

APP_ID = "one_locus_app"
MAX_MUTATION_RATE = 0.1


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


def create_exp_het_panel():
    plot = ui.output_plot("exp_het_plot")
    panel = ui.nav_panel("Expected het.", plot)
    return panel


def create_geno_freqs_plot_id(pop_name):
    return f"genotypic_freqs_plot_{pop_name}"


@module.ui
def genotypic_plot_ui():
    return ui.output_plot("genotypic_plot")


@module.server
def genotypic_plot_server(input, output, session, geno_freqs: dict):
    @render.plot
    def genotypic_plot():
        fig, axes = plt.subplots()
        axes.set_title("Genotypic freqs.")
        axes.set_xlabel("generation")
        axes.set_ylabel("freq")

        for geno_freq_label, geno_freqs_series in geno_freqs.items():
            axes.plot(
                geno_freqs_series.index, geno_freqs_series.values, label=geno_freq_label
            )
        axes.legend()
        axes.set_ylim((0, 1))
        return fig


def create_geno_freqs_module_plot_id(pop_name):
    return f"geno_freqs_plot_{pop_name}"


def create_genotypic_freqs_panel(config):
    panel_content = ui.output_ui("genotypic_plots")
    return ui.nav_panel("Genotypic Freqs.", panel_content)


def create_simulation_output_card(config):
    loggers = config["loggers"]
    panels = []
    if "allelic_freqs_logger" in loggers:
        panels.append(create_allelic_freqs_panel())
    if "genotypic_freqs_logger" in loggers:
        panels.append(create_genotypic_freqs_panel(config))
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
        freqs_ui = geno_freqs_slider
    elif "allelic" in ui_options:
        freqs_ui = freq_a_slider
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
            class_=pop_config["name"],
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

    check_value = math.isinf(pop_config["size"]["value"])
    inf_size_checkbox = (
        ui.input_checkbox("inf_size_checkbox", "Inf. size", check_value),
    )
    conditional_panel = (
        ui.panel_conditional(
            "!input.inf_size_checkbox",
            size_slider,
        ),
    )
    panel = ui.accordion_panel("Size", inf_size_checkbox, conditional_panel)
    return panel


def create_selection_panel(pop_config):
    fitness = pop_config["fitness"]
    wAA_slider = ui.input_slider(
        id="wAA_slider",
        label="wAA",
        min=0,
        max=1,
        value=fitness[0],
        width="100%",
    )
    wAa_slider = ui.input_slider(
        id="wAa_slider",
        label="wAa",
        min=0,
        max=1,
        value=fitness[1],
        width="100%",
    )
    waa_slider = ui.input_slider(
        id="waa_slider",
        label="waa",
        min=0,
        max=1,
        value=fitness[2],
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


def create_immigration_slider_id(from_pop, to_pop):
    return f"immigration_slider_from_{from_pop}_to_{to_pop}"


def create_immigration_panel(pop_config):
    config = pop_config["immigration"]
    slider_id = create_immigration_slider_id(config["from_pop"], pop_config["name"])
    slider = ui.input_slider(
        id=slider_id,
        label="",
        min=config["rate"]["min"],
        max=config["rate"]["max"],
        value=config["rate"]["value"],
        width="100%",
    )
    panel = ui.accordion_panel(f"Immigration from {config['from_pop']}", slider)
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
    if "immigration" in pop_config:
        immigration_panel = create_immigration_panel(pop_config)
        panels.append(immigration_panel)

    pop_accordion = ui.accordion(
        *panels,
        id="pop_accordion",
        title=pop_config["name"],
    )
    return pop_accordion


sim_config = reactive.value(None)


@module.server
def pop_input_server(input, output, session, pop_name, config):
    @reactive.calc
    def calc_geno_allelic_freqs():
        if "freqs_tabs" in input:
            selected_tab = input.freqs_tabs.get()
            use_geno_freqs_slider = selected_tab != "With HW"
        else:
            use_geno_freqs_slider = "geno_freqs_slider" in input

        if use_geno_freqs_slider:
            freq_AA, freq_AA_Aa = input.geno_freqs_slider()
            freq_Aa = freq_AA_Aa - freq_AA
            freq_aa = 1 - freq_AA_Aa
            freq_A = freq_AA + freq_Aa * 0.5
        else:
            freq_A = input.freq_a_slider()
            freq_a = 1 - freq_A
            freq_AA = freq_A**2
            freq_aa = freq_a**2
            freq_Aa = 1 - freq_AA - freq_aa

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

    def get_size():
        if input.inf_size_checkbox():
            size = INF
        else:
            size = input.size_slider()
        return size

    def calc_pop_values():
        freq_AA, freq_Aa, freq_aa, freq_A = calc_geno_allelic_freqs()
        values = {"genotypic_freqs": (freq_AA, freq_Aa, freq_aa)}
        values["size"] = get_size()
        if "wAA_slider" in input:
            values["fitness"] = (
                input.wAA_slider(),
                input.wAa_slider(),
                input.waa_slider(),
            )
        if "A2a_slider" in input:
            values["mut_rates"] = (input.A2a_slider(), input.a2A_slider())
        if "selfing_slider" in input:
            values["selfing_rate"] = input.selfing_slider()

        demographic_events = {}
        for pop_config in config["pops"].values():
            this_pop_name = pop_config["name"]
            if this_pop_name != pop_name:
                continue
            if "immigration" in pop_config:
                from_pop = pop_config["immigration"]["from_pop"]
                slider_id = create_immigration_slider_id(from_pop, pop_name)
                immigration_rate = getattr(input, slider_id)()
                event = {
                    "type": "migration_start",
                    "from_pop": from_pop,
                    "to_pop": pop_name,
                    "inmigrant_rate": immigration_rate,
                    "num_generation": 1,
                }
                id = f"migration_{from_pop}_to_{pop_name}"
                demographic_events[id] = event
        return values, demographic_events

    return calc_pop_values()


def get_pop_ids(config):
    idss = []
    for pop_id in sorted(config["pops"].keys()):
        pop_module_id = f"module_pop_{pop_id}"
        ids = {"id": pop_id, "module_id": pop_module_id}
        idss.append(ids)
    return idss


def create_pops_panel(config):
    tabs = []
    for pop_ids in get_pop_ids(config):
        pop_id = pop_ids["id"]
        module_id = pop_ids["module_id"]
        pop_config = config["pops"][pop_id]
        pop_accordion = create_pop_accordion(module_id, pop_config)
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
            and "genotypic_freqs" in config["pops"][pop_name]
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
        if "size" in config["pops"][pop_name]:
            pop_config["size"] = config["pops"][pop_name]["size"]
        else:
            pop_config.setdefault("size", {"min": 10, "max": 200, "value": 100})
        if pop_config["size"]["value"] in ("inf", "inf."):
            pop_config["size"]["value"] = INF

        for param in ("fitness", "mutation", "selfing_rate", "immigration"):
            if param in config["pops"][pop_name]:
                pop_config[param] = config["pops"][pop_name][param]

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


def app_ui(request):
    from urllib.parse import unquote
    import json

    config = None
    if False and config is None:
        config = {}
    elif False:
        # All options
        config = {
            "title": "One locus two alleles simulation",
            "pops": {
                "pop": {
                    "freq_A": 0.5,
                    "ui_freq_options": ("allelic", "genotypic"),
                    "fitness": (1, 1, 1),
                    "mutation": {"a2A": 0.0, "A2a": 0.0},
                    "selfing_rate": 0,
                },
            },
            "loggers": (
                "allelic_freqs_logger",
                "genotypic_freqs_logger",
                "exp_het_logger",
            ),
        }
    elif False:
        # Simple selection
        config = {
            "title": "Selection",
            "pops": {
                "pop": {
                    "freq_A": 0,
                    "ui_freq_options": ("allelic", "genotypic"),
                    "fitness": (1, 0.8, 0.8),
                    "mutation": {"a2A": 0.01, "A2a": 0},
                },
            },
            "loggers": (
                "allelic_freqs_logger",
                "genotypic_freqs_logger",
            ),
        }
    elif False:
        # Simple drift
        config = {
            "title": "Drift",
            "pops": {
                "pop": {
                    "freq_A": 0.5,
                    "ui_freq_options": ("allelic",),
                },
            },
            "loggers": (
                "allelic_freqs_logger",
                "exp_het_logger",
            ),
        }
    elif True:
        # balancing selection
        config = {
            "title": "Balancing selection",
            "pops": {
                "pop_a": {
                    "freq_A": 0.5,
                    "fitness": (1, 1, 0),
                    "ui_freq_options": ("allelic",),
                    "immigration": {
                        "rate": {"min": 0, "max": 0.2, "value": 0.1},
                        "from_pop": "pop_b",
                    },
                },
                "pop_b": {
                    "freq_A": 0.5,
                    "fitness": (0, 1, 1),
                    "ui_freq_options": ("allelic",),
                    "immigration": {
                        "rate": {"min": 0, "max": 0.2, "value": 0.1},
                        "from_pop": "pop_a",
                    },
                },
            },
            "loggers": (
                "allelic_freqs_logger",
                "exp_het_logger",
            ),
        }

    else:
        print("request", request)
        url_query = request.url.query

        print("url_query", url_query)
        config = request.query_params.get("app_config")

        print("str_config", config)

        # howto encode
        # from urllib.parse import urlencode
        # import json
        # app_config = {"pops": {"pop_a": {"freq_A": 0.9}, "pop_b": {"freq_A": 0.1}}}
        # encoded = urlencode({"app_config": json.dumps(app_config, separators=(',', ':'))})
        # app_config=%7B%22pops%22%3A%7B%22pop_a%22%3A%7B%22freq_A%22%3A0.9%7D%2C%22pop_b%22%3A%7B%22freq_A%22%3A0.1%7D%7D%7D
        # app_config = {'title': 'One locus two alleles simulation', 'pops': {'pop_0': {'name': 'pop_0', 'freq_A': 0.5, 'ui_freq_options': ('genotypic', 'allelic'), 'size': {'min': 10, 'max': 200, 'value': 100}}}, 'num_generations': {'min': 10, 'max': 200, 'value': 100}, 'loggers': ('allelic_freqs_logger', 'genotypic_freqs_logger', 'exp_het_logger')}
        # encoded
        # app_config=%7B%22title%22%3A%22One+locus+two+alleles+simulation%22%2C%22pops%22%3A%7B%22pop_0%22%3A%7B%22name%22%3A%22pop_0%22%2C%22freq_A%22%3A0.5%2C%22ui_freq_options%22%3A%5B%22genotypic%22%2C%22allelic%22%5D%2C%22size%22%3A%7B%22min%22%3A10%2C%22max%22%3A200%2C%22value%22%3A100%7D%7D%7D%2C%22num_generations%22%3A%7B%22min%22%3A10%2C%22max%22%3A200%2C%22value%22%3A100%7D%2C%22loggers%22%3A%5B%22allelic_freqs_logger%22%2C%22genotypic_freqs_logger%22%2C%22exp_het_logger%22%5D%7D
        import json

        config = json.loads(config)

    set_config_defaults(config)

    sim_config.set(config)
    # print(config)

    input_card = create_simulation_input_card(config)
    output_card = create_simulation_output_card(config)

    page = ui.page_fixed(ui.h1(config["title"]), input_card, output_card)
    return page


def server(input, output, session):
    @reactive.calc
    def get_sim_params():
        config = sim_config.get()
        pops_params = {}
        demographic_events = {}
        for pop_ids in get_pop_ids(config):
            pop_id = pop_ids["id"]
            pop_name = config["pops"][pop_id]["name"]
            module_id = pop_ids["module_id"]
            pops_params[pop_name], pop_demographic_events = pop_input_server(
                module_id, pop_name, config
            )
            demographic_events.update(pop_demographic_events)

        sim_params = {"pops": pops_params}
        sim_params["num_generations"] = input.num_gen_slider()
        sim_params["loggers"] = config["loggers"]
        if demographic_events:
            sim_params["demographic_events"] = demographic_events
        return sim_params

    @reactive.calc
    @reactive.event(input.run_button, ignore_none=False)
    def run_simulation():
        sim_params = get_sim_params()

        sim = OneLocusTwoAlleleSimulation(sim_params)
        return sim

    @render.plot(alt="Freq. A plot")
    def allelic_freqs_plot():
        sim = run_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Freq. A")
        axes.set_xlabel("generation")
        axes.set_ylabel("freq")

        freqs_dframe = sim.results["allelic_freqs"]
        for pop, pop_allelic_freqs in freqs_dframe.items():
            axes.plot(pop_allelic_freqs.index, pop_allelic_freqs.values, label=pop)

        num_pops = freqs_dframe.shape[1]
        if num_pops > 1:
            axes.legend()

        axes.set_ylim((0, 1))
        return fig

    @render.ui
    def genotypic_plots():
        sim = run_simulation()

        genotypic_freqs = sim.results["genotypic_freqs"]

        geno_freqs_labels = sorted(genotypic_freqs.keys())
        first_label = geno_freqs_labels[0]
        pop_names = genotypic_freqs[first_label].columns

        plots = {}
        for pop in pop_names:
            module_id = f"geno_freqs_plot_{pop}"
            # Dynamically create UI components for each plot
            plot = genotypic_plot_ui(module_id)
            plots[pop] = plot

            geno_freqs = {
                geno_freq_label: genotypic_freqs[geno_freq_label][pop]
                for geno_freq_label in geno_freqs_labels
            }
            # Dynamically create server-side functions for each plot
            genotypic_plot_server(module_id, geno_freqs=geno_freqs)

        if len(plots) == 1:
            output_content = plot
        else:
            panels = [ui.nav_panel(pop_name, plot) for pop_name, plot in plots.items()]
            navset_tab = ui.navset_tab(*panels, id="geno_freqs_navset")
            output_content = navset_tab

        return output_content

    @render.plot(alt="Exp. Het.")
    def exp_het_plot():
        sim = run_simulation()

        fig, axes = plt.subplots()
        axes.set_title("Expected Het.")
        axes.set_xlabel("generation")
        axes.set_ylabel("Exp. Het.")

        exp_hets_dframe = sim.results["expected_hets"]

        for pop, pop_exp_hets in exp_hets_dframe.items():
            axes.plot(pop_exp_hets.index, pop_exp_hets.values, label=pop)

        num_pops = exp_hets_dframe.shape[1]
        if num_pops > 1:
            axes.legend()

        axes.set_ylim((0, 1))
        return fig


app = App(app_ui, server)
