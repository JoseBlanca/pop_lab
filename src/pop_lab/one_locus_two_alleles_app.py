import setup

from IPython.display import display
import ipywidgets

from widgets import GenoFreqsWidget, PopSizeWidget, NumGenerationsWidget
from one_locus_two_alleles_simulator import simulate_one_locus_two_alleles_one_pop
from plotters import ResultPlotter


class OneLocusSimApp:
    def __init__(self):
        self.app_title = "One locus simulator"

    def _generate_layout(self):
        children_widgets = []
        self.pop_size_widget = PopSizeWidget(default_size=100, max_size=1000)
        self.geno_freqs_widget = GenoFreqsWidget(0.3, 0.3)
        self.num_gen_widget = NumGenerationsWidget(
            min_num=10, max_num=100, default_num=20
        )
        children_widgets.extend(
            [self.geno_freqs_widget, self.pop_size_widget, self.num_gen_widget]
        )

        self.output_widget = ipywidgets.Output()
        children_widgets.append(self.output_widget)

        self.run_button = ipywidgets.Button(description="Run")
        self.run_button.on_click(self.update_output)
        children_widgets.append(self.run_button)

        return ipywidgets.VBox(children_widgets)

    def run_application(self):
        display(self._generate_layout())

    def get_sim_params(self):
        params = {}
        params["pop_size"] = self.pop_size_widget.size
        params["num_generations"] = self.num_gen_widget.num_generations
        geno_freqs = self.geno_freqs_widget.geno_freqs
        params["freq_AA"] = geno_freqs.AA
        params["freq_Aa"] = geno_freqs.Aa
        params["freq_aa"] = geno_freqs.aa
        return params

    def run_simulation(self, sim_params):
        return simulate_one_locus_two_alleles_one_pop(**sim_params)

    def update_output(self, *_):
        ipywidgets.interaction.show_inline_matplotlib_plots()

        sim_params = self.get_sim_params()
        sim_result = self.run_simulation(sim_params)

        with self.output_widget:
            plotter = ResultPlotter(
                output_widget=self.output_widget,
                genotypic_freqs_logger=sim_result["genotypic_freqs_logger"],
                allelic_freqs_logger=sim_result["allelic_freqs_logger"],
                exp_het_logger=sim_result["exp_het_logger"],
            )
            plotter.plot_output()
            ipywidgets.interaction.show_inline_matplotlib_plots()
