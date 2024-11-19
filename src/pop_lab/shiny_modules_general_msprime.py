import itertools
from array import array

from shiny import ui, module, reactive, render

import numpy
import pandas
import demesdraw
import matplotlib.pyplot as plt
import statsmodels.api as sm

import msprime_sim_utils
import pynei


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


MIN_SEQ_LENGTH = 5e5
MAX_SEQ_LENGTH = 10e6
DEF_SEQ_LENGTH = 2e6

MIN_RECOMB_RATE = -10
DEF_RECOMB_RATE = -8
MAX_RECOMB_RATE = -6

MIN_MUT_RATE = -10
DEF_MUT_RATE = -8
MAX_MUT_RATE = -6

MIN_SAMPLE_SIZE = 20
DEF_SAMPLE_SIZE = 50
MAX_SAMPLE_SIZE = 100

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
                    min=MIN_RECOMB_RATE,
                    max=MAX_RECOMB_RATE,
                    value=DEF_RECOMB_RATE,
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
                min=MIN_SEQ_LENGTH,
                max=MAX_SEQ_LENGTH,
                value=DEF_SEQ_LENGTH,
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
AFS_PLOT_ID = "afs_plot"
PCA_PLOT_ID = "pca_plot"


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

    afs_result = ui.output_plot(AFS_PLOT_ID)

    pca_result = ui.output_plot(PCA_PLOT_ID)

    ld_vs_dist_plot = ui.output_plot("ld_vs_dist_plot")

    output_card = ui.navset_card_tab(
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
        ui.nav_panel(
            "Allele frequency spectrum",
            afs_result,
        ),
        ui.nav_panel(
            "PCA",
            pca_result,
        ),
        ui.nav_panel("LD", ld_vs_dist_plot),
    )
    return (run_button, output_card)


@module.server
def run_simulation_server(
    input, output, session, get_sample_sets, get_demography, get_msprime_params
):
    @reactive.calc
    @reactive.event(input.run_button)
    def do_simulation():
        demography = get_demography()["demography"]
        sample_sets = get_sample_sets()

        msprime_params = get_msprime_params()

        sim_res = msprime_sim_utils.simulate(
            sample_sets,
            demography=demography,
            seq_length_in_bp=msprime_params["seq_length_in_bp"],
            mutation_rate=msprime_params["mut_rate"],
            recomb_rate=msprime_params["recomb_rate"],
        )
        return sim_res

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
            axes.plot(list(-exp_het.index), exp_het.values, label=pop)
        axes.set_ylim(0)
        axes.legend()
        return fig

    @render.data_frame
    def exp_het_table():
        res = get_exp_hets()
        return render.DataGrid(res["exp_het_dframe"])

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
            axes.plot(list(-series.index), series.values, label=pop)
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
            axes.plot(list(-series.index), series.values, label=pop)
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
            axes.plot(list(-series.index), series.values, label=pop)
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
            if generation > 0:
                continue
            pop = pop_sample_info["pop_name"]
            axes.plot(x_poss, counts, label=f"{pop}-{generation}")
        axes.set_xlim((0.5, 1))
        axes.set_xlabel("Allele frequency")
        axes.set_ylabel("Num. variants")
        axes.legend()
        return fig

    @render.plot(alt="Principal Component Analysis")
    def pca_plot():
        sim_res = do_simulation()
        fig, axes = plt.subplots()

        res = sim_res.get_vars_and_pop_samples()
        vars = res["vars"]
        vars = pynei.filter_by_maf(vars, max_allowed_maf=0.95)
        pop_samples_info = res["pop_samples_info"]
        indis_by_pop_sample = res["indis_by_pop_sample"]

        try:
            pca_res = pynei.pca.do_pca_with_vars(vars, transform_to_biallelic=True)
        except Exception as error:
            if "DLASCL" in str(error):
                raise RuntimeError(
                    " PCA calculation failed, please rerun the simulation\n(This is a bug in OpenBLAS: On entry to DLASCL parameter number 4 had an illegal value)"
                )
            else:
                raise error
        projections = pca_res["projections"]
        explained_variance = pca_res["explained_variance (%)"]

        filter_stats = pynei.gather_filtering_stats(vars)

        pop_sample_names = sorted(
            pop_samples_info.keys(),
            key=lambda pop: pop_samples_info[pop]["sample_time"],
        )

        color_cycle = itertools.cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        markers = ["o", "s", "v", "^", "<", ">", "p", "*", "h", "H", "D", "d"]
        marker_cycle = itertools.cycle(markers)

        alpha_min = 0.3
        times = list(
            reversed(
                sorted({info["sample_time"] for info in pop_samples_info.values()})
            )
        )
        alpha_delta = (1 - alpha_min) / (len(times) - 1)
        alphas = {time: alpha_delta * idx + alpha_min for idx, time in enumerate(times)}

        indi_names = projections.index.to_numpy()
        x_values = projections.iloc[:, 0].values
        y_values = projections.iloc[:, 1].values
        colors = {}
        markers = {}
        for pop_sample_name in pop_sample_names:
            mask = numpy.isin(indi_names, indis_by_pop_sample[pop_sample_name])
            pop_sample_info = pop_samples_info[pop_sample_name]

            time = pop_sample_info["sample_time"]
            if time in markers:
                marker = markers[time]
            else:
                marker = next(marker_cycle)
                markers[time] = marker

            pop = pop_sample_info["pop_name"]
            if pop in colors:
                color = colors[pop]
            else:
                color = next(color_cycle)
                colors[pop] = color
            axes.scatter(
                x_values[mask],
                y_values[mask],
                label=f"{pop}-{time}",
                color=color,
                marker=marker,
                alpha=alphas[time],
            )
        axes.set_title(f"PCA done with {filter_stats['maf']['vars_kept']} variations")
        axes.set_xlabel(f"PC1 ({explained_variance.iloc[0]:.2f}%)")
        axes.set_ylabel(f"PC2 ({explained_variance.iloc[1]:.2f}%)")
        axes.legend()
        return fig

    @render.plot(alt="LD vs dist plot")
    def ld_vs_dist_plot():
        sim_res = do_simulation()
        fig, axes = plt.subplots()

        res = sim_res.get_vars_and_pop_samples()
        vars = res["vars"]
        indis_by_pop_sample = res["indis_by_pop_sample"]
        pop_samples_info = res["pop_samples_info"]

        alpha_min = 0.3
        times = list(
            reversed(
                sorted({info["sample_time"] for info in pop_samples_info.values()})
            )
        )
        alpha_delta = (1 - alpha_min) / (len(times) - 1)
        alphas = {time: alpha_delta * idx + alpha_min for idx, time in enumerate(times)}

        color_cycle = itertools.cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        colors = {}

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
            if pop in colors:
                color = colors[pop]
            else:
                color = next(color_cycle)
                colors[pop] = color
            axes.plot(
                xs,
                interpolated_r2,
                label=f"{pop}-{time}",
                color=color,
                alpha=alphas[time],
            )

        axes.legend()
        return fig
