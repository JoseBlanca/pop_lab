import numpy
import pandas
import msprime

import pynei


class SimulationResult:
    def __init__(
        self, tree_seqs, sample_sets: list[msprime.SampleSet], demography, ploidy
    ):
        self.tree_seqs = tree_seqs
        self._sample_sets = sample_sets
        self.demography = demography
        self.ploidy = ploidy

    def _get_pop_ids_and_names(self):
        tree_seqs = self.tree_seqs

        pop_ids_by_pop_name_in_tseq = {}
        pop_names_by_pop_id_in_tseq = {}
        for pop in tree_seqs.populations():
            pop_name = pop.metadata["name"]
            pop_id = pop.id
            pop_ids_by_pop_name_in_tseq[pop_name] = pop_id
            pop_names_by_pop_id_in_tseq[pop_id] = pop_name
        return pop_ids_by_pop_name_in_tseq, pop_names_by_pop_id_in_tseq

    def _create_indi_names(self, pop_samples):
        for pop_sample_name, sample_info in pop_samples.items():
            sample_info["indi_names"] = [
                f"{pop_sample_name}-indi_{node_id}"
                for node_id in sample_info["sample_node_ids"]
            ]

    def _get_pop_samples_info(self):
        samples = {}
        tree_seqs = self.tree_seqs
        pop_ids_by_pop_name_in_tseq, _ = self._get_pop_ids_and_names()
        for sample in self._sample_sets:
            pop_name = sample.population
            sampling_time = sample.time
            pop_id = pop_ids_by_pop_name_in_tseq[pop_name]
            sample_name = f"{pop_name}_{sampling_time}"
            sample = {
                "sample_node_ids": tree_seqs.samples(
                    population=pop_id, time=sampling_time
                ),
                "sample_time": sampling_time,
                "pop_name": pop_name,
            }
            if sample["sample_node_ids"].size == 0:
                continue
            samples[sample_name] = sample
        return samples

    def get_vars_and_pop_samples(self):
        pop_samples_info = self._get_pop_samples_info()

        pop_sample_by_node_id = {}
        for pop_sample_name, sample_info in pop_samples_info.items():
            for node_id in sample_info["sample_node_ids"]:
                pop_sample_by_node_id[node_id] = pop_sample_name

        tree_seqs = self.tree_seqs
        haplotype_array = tree_seqs.genotype_matrix()
        node_ids = tree_seqs.samples()
        new_shape = (haplotype_array.shape[0], -1, self.ploidy)
        gt_array = haplotype_array.reshape(new_shape)
        one_node_id_per_indi = node_ids[:: self.ploidy]

        poss = tree_seqs.tables.sites.position

        vars_info = pandas.DataFrame(
            {
                pynei.VAR_TABLE_POS_COL: poss,
                pynei.VAR_TABLE_CHROM_COL: numpy.full((poss.size,), 1),
            }
        )

        indi_names = []
        indis_by_pop_sample = {
            pop_sample: [] for pop_sample in set(pop_sample_by_node_id.values())
        }
        for node_id in one_node_id_per_indi:
            pop_sample_name = pop_sample_by_node_id[node_id]
            indi_name = f"{node_id}-{pop_sample_name}"
            indi_names.append(indi_name)
            indis_by_pop_sample[pop_sample_name].append(indi_name)
        vars = pynei.Variants.from_gt_array(
            gt_array, samples=indi_names, vars_info=vars_info
        )
        return {
            "vars": vars,
            "indis_by_pop_sample": indis_by_pop_sample,
            "pop_samples_info": pop_samples_info,
        }

    @staticmethod
    def _sort_series_by_sampling_time(series, pop_samples_info):
        return series.sort_index(
            key=lambda pop_samples: [
                -pop_samples_info[pop_sample]["sample_time"]
                for pop_sample in pop_samples
            ],
        )

    def _create_series_per_pop_and_dframe(
        self, series_indexed_by_pop_sample, param, pop_samples_info
    ):
        pops = []
        for pop_sample_name in series_indexed_by_pop_sample.index:
            pops.append(pop_samples_info[pop_sample_name]["pop_name"])
        dframe = pandas.DataFrame(
            {
                param: series_indexed_by_pop_sample,
                "pop": pops,
            }
        )
        series_for_pops = {}
        for pop, group in dframe.groupby("pop"):
            values_for_pop = group[param]
            values_for_pop.index = [
                pop_samples_info[pop_sample_name]["sample_time"]
                for pop_sample_name in values_for_pop.index
            ]
            values_for_pop = values_for_pop.sort_index()
            series_for_pops[pop] = values_for_pop
        dframes = []
        for pop, series in series_for_pops.items():
            dframe = pandas.DataFrame(
                {
                    param: series.values,
                    "pop": [pop] * series.size,
                    "generation": list(series.index),
                }
            )
            dframes.append(dframe)
        dframe = pandas.concat(dframes)

        return {f"{param}_by_pop": series_for_pops, f"{param}_dframe": dframe}

    def calc_unbiased_exp_het(self):
        res = self.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]
        res = pynei.calc_exp_het_stats_per_var(
            res["vars"], pops=res["indis_by_pop_sample"], unbiased=True
        )
        exp_het = res["mean"]
        series_indexed_by_pop_sample = exp_het
        param = "exp_het"
        return self._create_series_per_pop_and_dframe(
            series_indexed_by_pop_sample, param, pop_samples_info
        )

    def calc_num_variants(self):
        res = self.get_vars_and_pop_samples()
        pop_samples_info = res["pop_samples_info"]
        res = pynei.calc_poly_vars_ratio_per_var(
            res["vars"], pops=res["indis_by_pop_sample"]
        )

        sorted_res = {}
        for param in ["num_poly", "num_variable", "poly_ratio_over_variables"]:
            series_indexed_by_pop_sample = res[param]
            sorted_res[param] = self._create_series_per_pop_and_dframe(
                series_indexed_by_pop_sample, param, pop_samples_info
            )

        return sorted_res

    def calc_allele_freq_spectrum(self):
        res = self.get_vars_and_pop_samples()
        res = pynei.calc_major_allele_stats_per_var(
            res["vars"], pops=res["indis_by_pop_sample"], hist_kwargs={"num_bins": 20}
        )
        return {"counts": res["hist_counts"], "bin_edges": res["hist_bin_edges"]}


def get_info_from_demography(demography: msprime.Demography):
    pop_info = {}
    for population in demography.populations:
        pop_info[population.name] = {
            "id": population.id,
            "name": population.name,
            "initial_size": population.initial_size,
        }
    return {"pops": pop_info}


def create_msprime_sample_set(num_samples: int, ploidy: int, pop_name: str, time: int):
    sample_set = msprime.SampleSet(
        num_samples=num_samples, population=pop_name, ploidy=ploidy, time=time
    )
    return sample_set


def simulate(
    sample_sets: list[msprime.SampleSet],
    demography: msprime.Demography,
    seq_length_in_bp: int,
    recomb_rate=1e-8,
    add_mutations=True,
    random_seed=None,
    mutation_rate=1e-8,
    ploidy=2,
):
    tree_seqs = msprime.sim_ancestry(
        samples=sample_sets,
        demography=demography,
        recombination_rate=recomb_rate,
        sequence_length=seq_length_in_bp,
        random_seed=random_seed,
    )
    if add_mutations:
        tree_seqs = msprime.sim_mutations(
            tree_seqs, rate=mutation_rate, random_seed=random_seed
        )

    return SimulationResult(
        tree_seqs=tree_seqs,
        sample_sets=sample_sets,
        demography=demography,
        ploidy=ploidy,
    )
