from array import array

from shiny import ui, module, reactive, render

import numpy
import pandas
import demesdraw
import matplotlib.pyplot as plt
import statsmodels.api as sm

import shiny_module_sim_demography
import msprime_sim_utils
from style import COLOR_CYCLE, MARKER_CYCLE, LINESTYLES_CYCLE, COLORS
import pynei

PCA_MAX_MAF = 0.95
MIN_LD_R2 = 0.1
MIN_NUM_VARS_FOR_PCA = 10


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

    @classmethod
    def from_dict(cls, dict: list[str, pandas.Series]):
        table = cls([])
        table._cols = dict.copy()
        return table

    @property
    def df(self):
        return pandas.DataFrame(self._cols)


MIN_MUT_RATE = -8
DEF_MUT_RATE = -7
MAX_MUT_RATE = -6

MIN_SAMPLE_SIZE = 20
DEF_SAMPLE_SIZE = 50
MAX_SAMPLE_SIZE = 100

THIN_LINE = 1
BROAD_LINE = 2
UNUSED_STYLE = {
    "color": "grey",
    "marker": ".",
    "alpha": 0.1,
    "linewidth": THIN_LINE,
    "marker_filled": False,
    "linestyle": "solid",
}

######################################################################
# msprime parameters
######################################################################


@module.ui
def msprime_params_ui():
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
                    min=shiny_module_sim_demography.MIN_RECOMB_RATE,
                    max=shiny_module_sim_demography.MAX_RECOMB_RATE,
                    value=shiny_module_sim_demography.DEF_RECOMB_RATE,
                    width="100%",
                ),
            ),
            ui.input_checkbox(
                "no_recomb_checkbox", label="No recombination", value=False
            ),
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

    seq_len_panel = (
        (
            ui.input_slider(
                "seq_len_slider",
                label="",
                min=shiny_module_sim_demography.MIN_SEQ_LENGTH,
                max=shiny_module_sim_demography.MAX_SEQ_LENGTH,
                value=shiny_module_sim_demography.DEF_SEQ_LENGTH,
                width="100%",
            ),
        ),
    )
    msprime_accordions = [
        ui.accordion_panel(
            "Sample size (num. individuals to sample)", sample_size_panel
        ),
        ui.accordion_panel(
            "Recombination rate (per base pair and generation)", recomb_panel
        ),
        ui.accordion_panel("Mutation rate (per base pair and generation)", mut_panel),
        ui.accordion_panel("Sequence length (in pb)", seq_len_panel),
    ]
    return msprime_accordions


@module.server
def msprime_params_server(input, output, session):
    @reactive.calc
    def get_msprime_params():
        sample_size = input.sample_size_slider()
        seq_length_in_bp = input.seq_len_slider()
        mut_rate = 10 ** input.mut_rate_slider()
        if input.no_recomb_checkbox:
            recomb_rate = 0
        else:
            recomb_rate = 10 ** input.recomb_rate_slider()
        return {
            "sample_size": sample_size,
            "seq_length_in_bp": seq_length_in_bp,
            "mut_rate": mut_rate,
            "recomb_rate": recomb_rate,
        }

    return get_msprime_params


######################################################################
# input module
######################################################################


@module.ui
def input_params_tabs():
    demographic_plot = ui.output_plot("demographic_plot")
    input_params_table = ui.output_data_frame("input_params_table")
    card_tab = ui.navset_card_tab(
        ui.nav_panel("Demography", demographic_plot),
        ui.nav_panel("Input parameters summary", input_params_table),
    )
    return card_tab


@module.server
def input_params_server(input, output, session, get_demography, get_msprime_params):
    @render.plot(alt="Demographic plot")
    def demographic_plot():
        demography = get_demography()["demography"]
        fig, axes = plt.subplots()
        axes.plot([1, 1], [0, 0])
        demesdraw.tubes(demography.to_demes(), ax=axes)
        return fig

    @render.data_frame
    def input_params_table():
        table = Table(["Parameter", "Value"])
        demographic_params = get_demography()["params_for_table"]
        params = demographic_params.copy()
        params.update(get_msprime_params())

        nice_param_names = {
            "sample_size": "Sample size (num. individuals sampled at each time)",
            "seq_length_in_bp": "Sequence length (in bp)",
            "mut_rate": "Mutation rate (per base pair and generation)",
            "recomb_rate": "Recombination rate (per base pair and generation)",
        }

        for param, value in params.items():
            param = nice_param_names.get(param, param)
            table.add_row({"Parameter": param, "Value": value})

        return render.DataGrid(table.df, width="100%")


######################################################################
# simulation module
######################################################################

EXP_HET_PLOT_ID = "exp_het_plot"
EXP_HET_TABLE_ID = "exp_het_table"
POLY_MARKERS_PLOT_ID = "poly_markers_plot"
POLY_MARKERS_TABLE_ID = "poly_markers_table"

LD_PLOT_ID = "ld_vs_dist"
PCA_PLOT_ID = "pca"
AFS_PLOT_ID = "afs"
DIVERSITY_ALONG_GENOME_PLOT_ID = "diversity_along_genome"
PLOT_IDS = (AFS_PLOT_ID, PCA_PLOT_ID, LD_PLOT_ID, DIVERSITY_ALONG_GENOME_PLOT_ID)
PLOT_DESCRIPTIONS = {
    AFS_PLOT_ID: "Allele freq. spectrum",
    PCA_PLOT_ID: "PCA",
    LD_PLOT_ID: "LD",
    DIVERSITY_ALONG_GENOME_PLOT_ID: "Diversity along the genome",
    "dists": "Dest dists. between pops.",
}

PLOT_STRS = []
PLOT_IDS = []
for plot_id in shiny_module_sim_demography.DESIRED_PLOTS:
    PLOT_IDS.append(plot_id)
    PLOT_STRS.append(PLOT_DESCRIPTIONS[plot_id])


@module.ui
def run_simulation_ui():
    run_button = ui.input_action_button("run_button", "Run simulation")

    exp_het_result = ui.navset_tab(
        ui.nav_panel(
            "Plot",
            ui.output_plot(EXP_HET_PLOT_ID),
            value="exp_het_plot",
        ),
        ui.nav_panel(
            "Table",
            ui.output_data_frame(EXP_HET_TABLE_ID),
            value="exp_het_table",
        ),
        selected="exp_het_plot",
    )

    poly_ratio_result = ui.navset_tab(
        ui.nav_panel(
            "Plot",
            ui.output_plot("poly_ratio_over_variables_plot"),
            value="poly_ratio_over_variables_plot",
        ),
        ui.nav_panel(
            "Table",
            ui.output_data_frame("poly_ratio_over_variables_table"),
            value="poly_ratio_over_variables_table",
        ),
        selected="poly_ratio_over_variables_plot",
    )
    num_poly_result = ui.navset_tab(
        ui.nav_panel(
            "Plot",
            ui.output_plot("num_poly_plot"),
            value="num_poly_plot",
        ),
        ui.nav_panel(
            "Table",
            ui.output_data_frame("num_poly_table"),
            value="num_poly_table",
        ),
        selected="num_poly_plot",
    )
    num_variable_result = ui.navset_tab(
        ui.nav_panel(
            "Plot",
            ui.output_plot("num_variable_plot"),
            value="num_variable_plot",
        ),
        ui.nav_panel(
            "Table",
            ui.output_data_frame("num_variable_table"),
            value="num_variable_table",
        ),
        selected="num_variable_plot",
    )

    nav_panels = [
        ui.nav_panel(
            "Exp. Het.",
            exp_het_result,
        ),
        ui.nav_panel(
            "Polymorphic (95%) ratio over variable",
            poly_ratio_result,
        ),
        ui.nav_panel(
            "Num. polymorphic (95%) variants",
            num_poly_result,
        ),
        ui.nav_panel(
            "Num. variable variants",
            num_variable_result,
        ),
    ]

    for plot_str, plot_id in zip(
        PLOT_STRS,
        PLOT_IDS,
    ):
        plot = ui.output_plot(f"{plot_id}_plot")

        accordions = []
        if plot_id == "dists":
            nav_panels.append(ui.nav_panel(plot_str, plot))
        else:
            if len(shiny_module_sim_demography.POP_NAMES) > 1:
                pop_switches = [
                    ui.input_switch(f"{plot_id}_plot_swicth_pop_{pop}", pop, value=True)
                    for pop in shiny_module_sim_demography.POP_NAMES
                ]
                pops_accordion = ui.accordion(
                    ui.accordion_panel("Pops", pop_switches),
                    id=f"{plot_id}_pop_switches_accordion",
                )
                accordions.append(pops_accordion)
            times_accordion = ui.accordion(
                ui.accordion_panel("Times"),
                id=f"{plot_id}_time_switches_accordion",
            )
            accordions.append(times_accordion)
            sidebar = ui.sidebar(
                accordions,
                id=f"{plot_id}_sidebar",
            )
            sidebar_layout = ui.layout_sidebar(
                sidebar, plot, position="right", bg="#f8f8f8"
            )
            card = ui.card(sidebar_layout)
            nav_panels.append(ui.nav_panel(plot_str, card))

    output_card = ui.navset_card_tab(*nav_panels)

    return (run_button, output_card)


@module.server
def run_simulation_server(
    input, output, session, get_sample_sets, get_demography, get_msprime_params
):
    @reactive.calc()
    @reactive.event(input.run_button)
    def do_simulation():
        res = get_demography()
        demography = res["demography"]
        model = res.get("model", None)

        sample_sets = get_sample_sets()

        msprime_params = get_msprime_params()

        sim_res = msprime_sim_utils.simulate(
            sample_sets,
            demography=demography,
            model=model,
            seq_length_in_bp=msprime_params["seq_length_in_bp"],
            mutation_rate=msprime_params["mut_rate"],
            recomb_rate=msprime_params["recomb_rate"],
        )
        return sim_res

    @reactive.calc
    def get_sampling_times():
        sim_res = do_simulation()
        res = sim_res.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]
        sampling_times = {
            sample_info["sample_time"] for sample_info in pop_samples_info.values()
        }
        sampling_times = sorted(sampling_times)
        return sampling_times

    @reactive.effect
    @reactive.event(input.run_button)
    def update_time_swithes():
        sampling_times = get_sampling_times()
        for plot in PLOT_IDS:
            ui.remove_accordion_panel(
                id=f"{plot}_time_switches_accordion", target="Times"
            )
            switches = [
                ui.input_switch(
                    f"{plot}_plot_swicth_time_{time}", str(time), value=True
                )
                for time in sampling_times
            ]
            ui.insert_accordion_panel(
                id=f"{plot}_time_switches_accordion",
                # target="Pops",
                panel=ui.accordion_panel("Times", switches),
            )

    @reactive.calc
    def get_exp_hets():
        sim_res = do_simulation()
        return sim_res.calc_unbiased_exp_het()

    @reactive.calc
    def get_num_variants():
        sim_res = do_simulation()
        num_markers = sim_res.calc_num_variants()
        return num_markers

    @render.plot(alt="Expected heterozygosities")
    def exp_het_plot():
        fig, axes = plt.subplots()
        res = get_exp_hets()

        axes.set_title("Exp. het. over time")
        axes.set_xlabel("generation")
        axes.set_ylabel("Exp. het.")
        for pop, exp_het in res["exp_het_by_pop"].items():
            style = get_style_for_pop_and_time(pop=pop)
            axes.plot(
                list(-exp_het.index),
                exp_het.values,
                label=pop,
                color=style["color"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_ylim(0)
        axes.legend()
        return fig

    @render.data_frame
    def exp_het_table():
        res = get_exp_hets()
        return render.DataGrid(res["exp_het_dframe"].round(2))

    @render.plot(alt="Polymorphic (95%) ratio over variable")
    def poly_ratio_over_variables_plot():
        res = get_num_variants()
        param = "poly_ratio_over_variables"
        res = res[param]

        fig, axes = plt.subplots()
        axes.set_title("Polymorphic (95%) ratio over variable over time")
        axes.set_xlabel("generation")
        axes.set_ylabel("Polymorphic (95%) ratio over variable")
        for pop, series in res[f"{param}_by_pop"].items():
            style = get_style_for_pop_and_time(pop=pop)
            axes.plot(
                list(-series.index),
                series.values,
                label=pop,
                color=style["color"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_ylim(0)
        axes.legend()
        return fig

    @render.data_frame
    def poly_ratio_over_variables_table():
        res = get_num_variants()
        param = "poly_ratio_over_variables"
        res = res[param]

        return render.DataGrid(res[f"{param}_dframe"])

    @render.plot(alt="Num. polymorphic (95%) variants")
    def num_poly_plot():
        res = get_num_variants()
        param = "num_poly"
        res = res[param]

        fig, axes = plt.subplots()
        axes.set_title("Num. polymorphic (95%) variants over time")
        axes.set_xlabel("generation")
        axes.set_ylabel("Num. polymorphic (95%) variants")
        for pop, series in res[f"{param}_by_pop"].items():
            style = get_style_for_pop_and_time(pop=pop)
            axes.plot(
                list(-series.index),
                series.values,
                label=pop,
                color=style["color"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_ylim(0)
        axes.legend()
        return fig

    @render.data_frame
    def num_poly_table():
        res = get_num_variants()
        param = "num_poly"
        res = res[param]

        return render.DataGrid(res[f"{param}_dframe"])

    @render.plot(alt="Num. variants")
    def num_variable_plot():
        res = get_num_variants()
        param = "num_variable"
        res = res[param]

        fig, axes = plt.subplots()
        axes.set_title("Num. variable variants over time")
        axes.set_xlabel("generation")
        axes.set_ylabel("Num. variants")
        for pop, series in res[f"{param}_by_pop"].items():
            style = get_style_for_pop_and_time(pop=pop)
            axes.plot(
                list(-series.index),
                series.values,
                label=pop,
                color=style["color"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_ylim(0)
        axes.legend()
        return fig

    @render.data_frame
    def num_variable_table():
        res = get_num_variants()
        param = "num_variable"
        res = res[param]

        return render.DataGrid(res[f"{param}_dframe"])

    @render.plot(alt="Allele frequency spectrum")
    def afs_plot():
        sim_res = do_simulation()
        fig, axes = plt.subplots()
        res = sim_res.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]
        res = sim_res.calc_allele_freq_spectrum()
        bin_edges = res["bin_edges"]
        x_poss = (bin_edges[1:] + bin_edges[:-1]) / 2
        for pop_sample_name, counts in res["counts"].items():
            pop_sample_info = pop_samples_info[pop_sample_name]
            generation = pop_sample_info["sample_time"]
            pop = pop_sample_info["pop_name"]
            style = get_style(AFS_PLOT_ID, pop=pop, time=generation)
            axes.plot(
                x_poss,
                counts,
                label=f"{pop}-{generation}",
                color=style["color"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_xlim((0.5, 1))
        axes.set_xlabel("Allele frequency")
        axes.set_ylabel("Num. variants")
        axes.legend()
        return fig

    @reactive.calc
    def get_styles():
        color_cycle = COLOR_CYCLE
        marker_cycle = MARKER_CYCLE
        linestyle_cycle = LINESTYLES_CYCLE

        sim_res = do_simulation()
        res = sim_res.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]

        pop_names = set()
        sample_times = set()
        for sample_info in pop_samples_info.values():
            pop_names.add(sample_info["pop_name"])
            sample_times.add(sample_info["sample_time"])
        pop_names = sorted(pop_names)
        sample_times = sorted(sample_times)

        if len(sample_times) > 1:
            alpha_min = 0.3
            alpha_delta = (1 - alpha_min) / (len(sample_times) - 1)
        else:
            alpha_delta = None

        styles = {"time": {}, "pop": {}}
        styles["default"] = {
            "color": COLORS[-1],
            "alpha": 1,
            "marker": "o",
            "marker_filled": False,
            "linewidth": THIN_LINE,
            "linestyle": "solid",
        }

        for idx, time in enumerate(reversed(sample_times)):
            style = {"linewidth": BROAD_LINE}
            alpha = 1 if alpha_delta is None else alpha_delta * idx + alpha_min
            style["alpha"] = alpha
            style["color"] = next(color_cycle)
            styles["time"][time] = style

        for pop in pop_names:
            style = {"linewidth": BROAD_LINE}
            marker_and_fill = next(marker_cycle)
            style["marker"] = marker_and_fill[0]
            style["marker_filled"] = marker_and_fill[1]
            style["linestyle"] = next(linestyle_cycle)
            styles["pop"][pop] = style
        return styles

    def get_style_for_pop_and_time(pop=None, time=None):
        styles = get_styles()
        if pop is not None:
            style = styles["pop"][pop]
        if time is not None:
            style.update(styles["time"][time])
        complete_style = {}
        for trait in (
            "color",
            "marker",
            "alpha",
            "linewidth",
            "marker_filled",
            "linestyle",
        ):
            complete_style[trait] = style.get(trait, styles["default"][trait])
        return complete_style

    @reactive.calc
    def _do_pca():
        sim_res = do_simulation()

        pop_and_samples = sim_res.get_vars_and_pop_samples()
        vars = pop_and_samples["vars"]
        vars = pynei.filter_by_ld_and_maf(
            vars, min_allowed_r2=MIN_LD_R2, max_allowed_maf=PCA_MAX_MAF
        )

        try:
            pca_res = pynei.pca.do_pca_with_vars(vars, transform_to_biallelic=True)
        except Exception as error:
            if "DLASCL" in str(error):
                raise RuntimeError(
                    " PCA calculation failed, please rerun the simulation\n(This is a bug in OpenBLAS: On entry to DLASCL parameter number 4 had an illegal value)"
                )
            else:
                raise error
        return pop_and_samples, pca_res, vars

    @render.plot(alt="Principal Component Analysis")
    def pca_plot():
        pop_and_samples, pca_res, vars = _do_pca()
        pop_samples_info = pop_and_samples["pop_samples_info"]
        indis_by_pop_sample = pop_and_samples["indis_by_pop_sample"]

        fig, axes = plt.subplots()

        projections = pca_res["projections"]
        explained_variance = pca_res["explained_variance (%)"]

        filter_stats = pynei.gather_filtering_stats(vars)

        pop_sample_names = sorted(
            pop_samples_info.keys(),
            key=lambda pop: pop_samples_info[pop]["sample_time"],
        )

        indi_names = projections.index.to_numpy()

        vars_kept = filter_stats["ld_and_maf"]["vars_kept"]
        if vars_kept < MIN_NUM_VARS_FOR_PCA:
            raise RuntimeError(
                f"After filtering only {vars_kept} SNPs were kept, at leat {MIN_NUM_VARS_FOR_PCA} required to do PCA, you could rerun the simulation"
            )

        x_values = projections.iloc[:, 0].values
        y_values = projections.iloc[:, 1].values
        for pop_sample_name in pop_sample_names:
            mask = numpy.isin(indi_names, indis_by_pop_sample[pop_sample_name])
            pop_sample_info = pop_samples_info[pop_sample_name]

            time = pop_sample_info["sample_time"]
            pop = pop_sample_info["pop_name"]
            style = get_style(PCA_PLOT_ID, pop=pop, time=time)

            facecolor = style["color"] if style["marker_filled"] else "none"

            axes.scatter(
                x_values[mask],
                y_values[mask],
                label=f"{pop}-{time}",
                color=style["color"],
                marker=style["marker"],
                alpha=style["alpha"],
                facecolor=facecolor,
            )
        axes.set_title(
            f"PCA done with {filter_stats['ld_and_maf']['vars_kept']} polymorphic ({int(PCA_MAX_MAF*100)}%) and not in LD (r2={MIN_LD_R2}) variations"
        )
        axes.set_xlabel(f"PC1 ({explained_variance.iloc[0]:.2f}%)")
        axes.set_ylabel(f"PC2 ({explained_variance.iloc[1]:.2f}%)")
        axes.legend()
        return fig

    def get_style(plot_id, time, pop):
        time_switch_id = f"{plot_id}_plot_swicth_time_{time}"
        time_input_switch = getattr(input, time_switch_id)
        pop_input_switch_id = f"{plot_id}_plot_swicth_pop_{pop}"

        if len(shiny_module_sim_demography.POP_NAMES) > 1:
            pop_input_switch = getattr(input, pop_input_switch_id)
            pop_is_on = pop_input_switch()
        else:
            pop_is_on = True

        if pop_is_on and time_input_switch():
            style = get_style_for_pop_and_time(pop=pop, time=time)
        else:
            style = UNUSED_STYLE
        return style

    @reactive.calc
    def calc_ld_curves():
        sim_res = do_simulation()
        fig, axes = plt.subplots()

        res = sim_res.get_vars_and_pop_samples()
        vars = res["vars"]
        indis_by_pop_sample = res["indis_by_pop_sample"]
        pop_samples_info = res["pop_samples_info"]

        ld_curves = {}

        for pop_sample_name, lds_and_dists in pynei.get_ld_and_dist_for_pops(
            vars, indis_by_pop_sample, max_allowed_maf=0.90
        ).items():
            dists = array("f")
            r2s = array("f")
            for r2, dist in lds_and_dists:
                r2s.append(r2)
                dists.append(dist)
            r2s = numpy.array(r2s, dtype=float)
            dists = numpy.array(dists, dtype=float)

            dist_delta = 0.01 * (dists.max() - dists.min())

            lowess_dists_lds = sm.nonparametric.lowess(r2s, dists, delta=dist_delta)
            lowess_dists = lowess_dists_lds[:, 0]
            lowess_lds = lowess_dists_lds[:, 1]

            xs = numpy.linspace(0, dists.max(), 50)
            interpolated_r2 = numpy.interp(xs, lowess_dists, lowess_lds)

            pop_sample_info = pop_samples_info[pop_sample_name]
            time = pop_sample_info["sample_time"]
            pop = pop_sample_info["pop_name"]
            ld_curves[pop_sample_name] = {
                "dists": xs,
                "r2s": interpolated_r2,
                "time": time,
                "pop": pop,
            }
        return ld_curves

    @render.plot(alt="LD vs dist plot")
    def ld_vs_dist_plot():
        fig, axes = plt.subplots()
        for pop_sample_name, lds_and_dists in calc_ld_curves().items():
            time = lds_and_dists["time"]
            pop = lds_and_dists["pop"]
            dists = lds_and_dists["dists"]
            r2s = lds_and_dists["r2s"]
            style = get_style(LD_PLOT_ID, time, pop)
            axes.plot(
                dists,
                r2s,
                label=f"{pop}-{time}",
                color=style["color"],
                alpha=style["alpha"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_xlabel("Dist. between markers (bp.)")
        axes.set_ylabel("Rogers & Huff r2")
        axes.legend()
        return fig

    @render.plot(alt="Diversity along the genome plot")
    def diversity_along_genome_plot():
        sim_res = do_simulation()
        res = sim_res.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]
        exp_hets = sim_res.calc_exp_het_along_genome()

        fig, axes = plt.subplots()
        for sampling, sampling_exp_hets in exp_hets.iterrows():
            pop_sample_info = pop_samples_info[sampling]
            time = pop_sample_info["sample_time"]
            pop = pop_sample_info["pop_name"]
            style = get_style(DIVERSITY_ALONG_GENOME_PLOT_ID, time, pop)
            axes.plot(
                sampling_exp_hets.index,
                sampling_exp_hets.values,
                label=f"{pop}-{time}",
                color=style["color"],
                alpha=style["alpha"],
                linewidth=style["linewidth"],
                linestyle=style["linestyle"],
            )
        axes.set_ylim((0, axes.get_ylim()[1]))
        axes.set_xlabel("Genomic position (bp)")
        axes.set_ylabel("Mean unbiased exp. het.")
        return fig

    @render.plot(alt="Dest dists. between populations")
    def dists_plot():
        sim_res = do_simulation()

        res = sim_res.get_vars_and_pop_samples()
        vars = res["vars"]
        indis_by_pop_sample = res["indis_by_pop_sample"]

        vars = pynei.filter_by_maf(vars, max_allowed_maf=0.95)

        dists = pynei.calc_jost_dest_pop_dists(
            vars,
            pops=indis_by_pop_sample,
        )

        fig, axes = plt.subplots()
        square_dists = dists.square_dists

        pop_names = dists.names

        im = axes.imshow(square_dists, cmap="coolwarm")

        # Add colorbar
        fig.colorbar(im, ax=axes)

        # pop_names = list(reversed(pop_names))
        tick_positions = numpy.arange(0, len(pop_names))
        axes.set_xticks(tick_positions)
        axes.set_yticks(tick_positions)

        axes.set_xticklabels(pop_names)
        axes.set_yticklabels(pop_names)

        axes.tick_params(axis="x", rotation=90)
        return fig
