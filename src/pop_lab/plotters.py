import numpy
import matplotlib.pyplot as plt


class ResultPlotter:
    def __init__(
        self,
        output_widget,
        genotypic_freqs_logger,
        allelic_freqs_logger,
        exp_het_logger,
        plot_exp_het=True,
        plot_allelic_freqs=True,
        plot_genotypic_freqs=True,
    ):
        self.output_widget = output_widget
        self.genotypic_freqs_logger = genotypic_freqs_logger
        self.allelic_freqs_logger = allelic_freqs_logger
        self.exp_het_logger = exp_het_logger
        self.plot_exp_het = plot_exp_het
        self.plot_allelic_freqs = plot_allelic_freqs
        self.plot_genotypic_freqs = plot_genotypic_freqs

    def _plot_exp_het(self, axes):
        exp_het = self.exp_het_logger.values_per_generation
        axes.plot(exp_het.index, exp_het.values)
        axes.set_ylabel("Exp. het.")
        axes.set_ylim((0, 1))

    def _plot_allelic_freqs(self, axes):
        exp_het = self.allelic_freqs_logger.values_per_generation
        axes.plot(exp_het.index, exp_het.values)
        axes.set_ylabel("Freq. A")
        axes.set_ylim((0, 1))

    def _plot_genotypic_freqs(self, axes):
        geno_freqs = self.genotypic_freqs_logger.values_per_generation
        genotypes = sorted(geno_freqs.keys())
        for genotype in genotypes:
            freqs = geno_freqs[genotype]
            axes.plot(freqs.index, freqs.values, label=genotype)
        axes.legend()
        axes.set_ylabel("Geno. Freq.")
        axes.set_ylim((0, 1))

    def plot_output(self):
        # print(self.genotypic_freqs_logger.values_per_generation)
        # print(self.allelic_freqs_logger.values_per_generation)
        # print(self.exp_het_logger.values_per_generation)

        self.output_widget.clear_output(wait=True)

        num_plots = sum(
            (self.plot_allelic_freqs, self.plot_exp_het, self.plot_genotypic_freqs)
        )

        fig_size_y = 2.5 * num_plots

        fig, axess = plt.subplots(
            figsize=(5, fig_size_y), ncols=1, nrows=num_plots, sharex=True
        )
        if not isinstance(axess, (list, numpy.ndarray)):
            axess = [axess]
        axess = list(axess)
        axess_copy = axess[:]

        if self.plot_exp_het:
            exp_het_axes = axess_copy.pop(0)
            self._plot_exp_het(exp_het_axes)
        if self.plot_allelic_freqs:
            axes = axess_copy.pop(0)
            self._plot_allelic_freqs(axes)
        if self.plot_genotypic_freqs:
            axes = axess_copy.pop(0)
            self._plot_genotypic_freqs(axes)

        axess[-1].set_xlabel("generation")

        plt.show()
