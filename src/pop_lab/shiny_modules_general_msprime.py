from shiny import ui, module, reactive, render

import numpy
import pandas
import demesdraw
import matplotlib.pyplot as plt

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

    poly_markers_result = ui.navset_tab(
        ui.nav_panel(
            "Plot",
            ui.output_plot(POLY_MARKERS_PLOT_ID),
            value="poly_markers_plot",
        ),
        ui.nav_panel(
            "Table",
            ui.output_data_frame(POLY_MARKERS_TABLE_ID),
            value="poly_markers_table",
        ),
        selected="poly_markers_plot",
    )

    afs_result = ui.output_plot(AFS_PLOT_ID)

    pca_result = ui.output_plot(PCA_PLOT_ID)

    output_card = ui.navset_card_tab(
        ui.nav_panel(
            "Exp. Het.",
            exp_het_result,
        ),
        ui.nav_panel(
            "Polymorphic variants",
            poly_markers_result,
        ),
        ui.nav_panel(
            "Allele frequency spectrum",
            afs_result,
        ),
        ui.nav_panel(
            "PCA",
            pca_result,
        ),
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
        axes.plot(list(res["exp_het"].index), res["exp_het"].values)
        return fig

    @render.data_frame
    def exp_het_table():
        res = get_exp_hets()
        results_table = Table.from_dict(
            {
                "Exp. het.": res["exp_het"].values,
                "Generation": list(res["exp_het"].index),
            }
        )
        return render.DataGrid(results_table.df)

    @render.plot(alt="Number of variants")
    def poly_markers_plot():
        res = get_num_variants()

        fig, axess = plt.subplots(nrows=2)
        axes = axess[0]
        axes.set_title("Ratio poly. (95%) var over time")
        axes.set_xlabel("generation")
        axes.set_ylabel("Num. variants.")
        axes.plot(
            list(res["Poly. ratio over variables"].index),
            res["Poly. ratio over variables"].values,
        )
        axes.set_ylim(0, 1)

        axes = axess[1]
        axes.set_xlabel("generation")
        axes.set_ylabel("Num. variants")
        axes.plot(
            list(res["Num. variables"].index),
            res["Num. variables"].values,
            label="Num. variable",
        )
        axes.plot(
            list(res["Num. polymorphic"].index),
            res["Num. polymorphic"].values,
            label="Num. poly.",
        )
        axes.legend()
        return fig

    @render.data_frame
    def poly_markers_table():
        res = get_num_variants()
        return render.DataGrid(Table.from_dict(res).df)

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
            generation = pop_samples_info[pop_sample_name]["sample_time"]
            axes.plot(x_poss, counts, label=generation)
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

        pop_sample_names = sorted(
            pop_samples_info.keys(),
            key=lambda pop: pop_samples_info[pop]["sample_time"],
        )

        indi_names = projections.index.to_numpy()
        x_values = projections.iloc[:, 0].values
        y_values = projections.iloc[:, 1].values
        for pop_sample_name in pop_sample_names:
            mask = numpy.isin(indi_names, indis_by_pop_sample[pop_sample_name])
            time = pop_samples_info[pop_sample_name]["sample_time"]
            axes.scatter(x_values[mask], y_values[mask], label=f"Generation: {time}")

        axes.set_xlabel(f"PC1 ({explained_variance[0]:.2f}%)")
        axes.set_ylabel(f"PC2 ({explained_variance[1]:.2f}%)")
        axes.legend()
        return fig