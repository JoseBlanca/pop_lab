from ipywidgets import VBox, HBox, Layout
import ipywidgets as widgets

from one_locus_two_alleles_simulator import GenotypicFreqs


def _calculate_het_range_from_A(freq_A):
    freq_a = 1 - freq_A
    range_ = 0, min(freq_A, freq_a)
    return range_


def _calculate_A_range_from_Aa(desired_Aa):

    range_ = 0.5 * desired_Aa, 1 - (0.5 * desired_Aa)
    return range_


FREQ_A_LABEL = "Freq A:"
OBS_HET_LABEL = "Obs het:"
HW_LABEL = "HW freqs."


class GenoFreqsWidget(widgets.Box):

    def __init__(
        self,
        freq_AA: float,
        freq_Aa: float,
        freq_aa: float | None = None,
        *args,
        **kwargs
    ):
        self.geno_freqs = GenotypicFreqs(freq_AA, freq_Aa, freq_aa)

        self._set_up_children()

        self.ongoing_change = None

        super().__init__(children=[self.freqs_box], *args, **kwargs)

    def _set_up_children(self):
        self.text_AA = widgets.FloatText(
            value=round(self.geno_freqs.AA, 2), description="Freq AA:", disabled=True
        )
        self.text_Aa = widgets.FloatText(
            value=round(self.geno_freqs.Aa, 2), description="Freq Aa:", disabled=True
        )
        self.text_aa = widgets.FloatText(
            value=round(self.geno_freqs.aa, 2), description="Freq aa:", disabled=True
        )
        self.freqs_slider = widgets.FloatRangeSlider(
            value=(self.geno_freqs.AA, self.geno_freqs.AA + self.geno_freqs.Aa),
            min=0.0,
            max=1.0,
            step=0.01,
            readout=False,
        )
        self.freqs_slider.layout = Layout(width="auto", flex="1 1 auto")

        self.text_A = widgets.FloatText(
            value=round(self.geno_freqs.A, 2),
            description=FREQ_A_LABEL,
            disabled=False,
            min=0.0,
            max=1.0,
            step=0.01,
        )
        self.text_obs_het = widgets.FloatText(
            value=round(self.geno_freqs.Aa, 2),
            description=OBS_HET_LABEL,
            disabled=False,
            min=0.0,
            max=1.0,
            step=0.01,
        )
        self.hw_freqs_checkbox = widgets.Checkbox(value=False, description=HW_LABEL)

        self.text_A.observe(self._update_freqs, names="value")
        self.text_obs_het.observe(self._update_freqs, names="value")
        self.freqs_slider.observe(self._update_freqs, names="value")
        self.hw_freqs_checkbox.observe(self._update_freqs, names="value")

        self.freqs_box = VBox(
            [
                HBox([self.text_A, self.text_obs_het, self.hw_freqs_checkbox]),
                HBox([self.text_AA, self.text_Aa, self.text_aa]),
                HBox([self.freqs_slider]),
            ]
        )

    def _update_from_A(self, desired_A):

        if desired_A > 1.0:
            desired_A = 1.0
        if desired_A < 0.0:
            desired_A = 0.0

        possible_het_range = _calculate_het_range_from_A(desired_A)
        current_het = self.geno_freqs.Aa
        if current_het > possible_het_range[1]:
            new_het = possible_het_range[1]
        elif current_het < possible_het_range[0]:
            new_het = possible_het_range[0]
        else:
            new_het = current_het

        Aa = new_het
        AA = desired_A - 0.5 * Aa
        return GenotypicFreqs(AA, Aa)

    def _update_from_Aa(self, desired_Aa):
        if desired_Aa > 1.0:
            desired_Aa = 1.0
        if desired_Aa < 0.0:
            desired_Aa = 0.0

        possible_A_range = _calculate_A_range_from_Aa(desired_Aa)
        currrent_A = self.geno_freqs.A
        if currrent_A > possible_A_range[1]:
            new_A = possible_A_range[1]
        elif currrent_A < possible_A_range[0]:
            new_A = possible_A_range[0]
        else:
            new_A = currrent_A
        AA = new_A - 0.5 * desired_Aa

        return GenotypicFreqs(AA, desired_Aa)

    def _update_from_hw(self, hw_freqs):

        if hw_freqs:
            self.text_obs_het.disabled = True
            self.freqs_slider.disabled = True
            A = self.geno_freqs.A
            AA = A**2
            Aa = 2 * A * (1 - A)
        else:
            self.text_obs_het.disabled = False
            self.freqs_slider.disabled = False
            AA = self.geno_freqs.AA
            Aa = self.geno_freqs.Aa

        return GenotypicFreqs(AA, Aa)

    def _update_freqs(self, change):
        if change["owner"].description == FREQ_A_LABEL:
            required_change = "freq_A"
        elif change["owner"].description == OBS_HET_LABEL:
            required_change = "obs_het"
        elif change["owner"].description == HW_LABEL:
            required_change = "hw"
        elif isinstance(change["new"], tuple):
            required_change = "geno_freqs_slider"

        if self.ongoing_change is None:
            self.ongoing_change = required_change
        else:
            return

        if required_change == "freq_A":
            desired_freq_A = change["new"]
            new_geno_freqs = self._update_from_A(desired_freq_A)
        elif required_change == "obs_het":
            desired_Aa = change["new"]
            new_geno_freqs = self._update_from_Aa(desired_Aa)
        elif required_change == "geno_freqs_slider":
            AA, AA_Aa = change["new"]
            Aa = AA_Aa - AA
            new_geno_freqs = GenotypicFreqs(AA, Aa)
        elif required_change == "hw":
            new_geno_freqs = self._update_from_hw(change["new"])

        self.geno_freqs = new_geno_freqs
        self.text_A.value = round(new_geno_freqs.A, 2)
        self.text_obs_het.value = round(new_geno_freqs.Aa, 2)
        self.text_AA.value = round(new_geno_freqs.AA, 2)
        self.text_Aa.value = round(new_geno_freqs.Aa, 2)
        self.text_aa.value = round(new_geno_freqs.aa, 2)
        self.freqs_slider.value = round(new_geno_freqs.AA, 2), round(
            new_geno_freqs.AA, 2
        ) + round(new_geno_freqs.Aa, 2)

        self.ongoing_change = None
