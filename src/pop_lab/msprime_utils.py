import numpy
import pandas
import msprime

import pynei


def get_pop_names_from_demography(demography):
    return [deme.name for deme in demography.to_demes().demes]


class SimulationResult:
    def __init__(
        self, tree_seqs, samplings: list[msprime.SampleSet], demography, ploidy
    ):
        self.tree_seqs = tree_seqs
        self._sampling_list = samplings
        self.demography = demography
        self.ploidy = ploidy

    def _from_haplotype_array_to_gt_array(self, haplotype_array):
        new_shape = (haplotype_array.shape[0], -1, self.ploidy)
        gt_array = haplotype_array.reshape(new_shape)
        return gt_array

    def _get_indi_names(self):
        samplings = self._get_sampling_info()
        indi_names = {}
        for sampling_info in samplings:
            sampling_name = sampling_info["sampling_name"]
            for node_id in sampling_info["sampling_node_ids"]:
                indi_names[node_id] = f"{sampling_name}-indi_{node_id}"
        return indi_names

    def get_gts(self):
        tree_seqs = self.tree_seqs
        sampling_name_for_node_id = {}
        samplings = self._get_sampling_info()
        for sampling_info in samplings:
            for sampling_id in sampling_info["sampling_node_ids"]:
                sampling_name_for_node_id[sampling_id] = sampling_info["sampling_name"]

        indi_names_by_node_id = self._get_indi_names()
        sampling_names = []
        indi_names = []
        for sample_node_id in tree_seqs.samples():
            indi_names.append(indi_names_by_node_id[sample_node_id])
            sampling_names.append(sampling_name_for_node_id[sample_node_id])
        indi_names = indi_names[:: self.ploidy]
        sampling_names = sampling_names[:: self.ploidy]

        haplotype_array = tree_seqs.genotype_matrix()
        gt_array = self._from_haplotype_array_to_gt_array(haplotype_array)
        gts = pynei.genotypes.Genotypes(gt_array, indi_names)
        return {"gts": gts, "sampling_names": numpy.array(sampling_names)}

    def get_gts_by_sampling(self) -> dict:
        samplings = self._get_sampling_info()
        indi_names_by_node_id = self._get_indi_names()
        ploidy = self.ploidy
        node_idxss = []
        pops = []
        indi_namess = []
        for sampling in samplings:
            node_idxs_for_these_samples = sampling["sampling_node_ids"]
            pops_for_this_sample = [
                sampling["sampling_name"]
            ] * node_idxs_for_these_samples.size
            node_idxss.append(node_idxs_for_these_samples)
            pops.extend(pops_for_this_sample)
            num_indis_in_sampling = node_idxs_for_these_samples.size // ploidy
            assert num_indis_in_sampling * ploidy == node_idxs_for_these_samples.size
            indi_names_for_this_sampling = [
                indi_names_by_node_id[node_id]
                for node_id in node_idxs_for_these_samples[::ploidy]
            ]
            indi_namess.append(indi_names_for_this_sampling)

        genotypes = self.tree_seqs.genotype_matrix()
        gts_per_sampling = {}
        for node_idxs, indi_names, sampling in zip(node_idxss, indi_namess, samplings):
            # haplotype_array
            # the first dimension corresponds to the variants genotyped,
            # the second dimension corresponds to the haplotypes.
            # Each integer within the array corresponds to an allele index,
            # where 0 is the reference allele, 1 is the first alternate allele,
            # 2 is the second alternate allele, … and -1 is a missing allele call.
            # Adjacent haplotypes originate from the same sample
            haplotype_array = genotypes[:, node_idxs]
            gt_array = self._from_haplotype_array_to_gt_array(haplotype_array)
            gts = pynei.genotypes.Genotypes(gt_array, indi_names)
            gts_per_sampling[sampling["sampling_name"]] = {
                "gts": gts,
                "sampling_time": sampling["sampling_time"],
                "pop_name": sampling["pop_name"],
            }
        return gts_per_sampling

    @property
    def sampling_info(self) -> dict:
        samplings = self._get_sampling_info()
        sampling_dict = {}
        for sampling in samplings:
            sampling = {
                key: value
                for key, value in sampling.items()
                if key != "sampling_node_ids"
            }
            sampling_dict[sampling["sampling_name"]] = sampling
        return sampling_dict

    def _get_sampling_info(self):
        samplings = []
        tree_seqs = self.tree_seqs
        pop_ids_by_pop_name_in_tseq, _ = self._get_pop_ids_and_names()
        for sampling in self._sampling_list:
            pop_name = sampling.population
            sampling_time = sampling.time
            pop_id = pop_ids_by_pop_name_in_tseq[pop_name]
            sampling = {
                "sampling_node_ids": tree_seqs.samples(
                    population=pop_id, time=sampling_time
                ),
                "sampling_time": sampling_time,
                "pop_name": pop_name,
                "sampling_name": f"{pop_name}_{sampling_time}",
            }
            if sampling["sampling_node_ids"].size == 0:
                continue
            samplings.append(sampling)
        return samplings

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

    def _sort_series_by_sampling_time(self, series_with_sampling_names_as_index):
        samplings = self.sampling_info
        times = [
            -samplings[sampling_name]["sampling_time"]
            for sampling_name in series_with_sampling_names_as_index.index
        ]
        df = pandas.DataFrame(
            {
                series_with_sampling_names_as_index.name: series_with_sampling_names_as_index,
                "times": times,
            }
        )
        df.sort_values("times", inplace=True)
        return df.to_dict(orient="series")

    def _get_generation_times_for_samplings(self, sampling_names):
        samplings = self.sampling_info
        times = [
            -samplings[sampling_name]["sampling_time"]
            for sampling_name in sampling_names
        ]
        return times

    def calc_unbiased_exp_het(self):
        gts_per_sampling = self.get_gts_by_sampling()
        exp_hets = {}
        for sampling_name, gt_info in gts_per_sampling.items():
            gts = gt_info["gts"]
            exp_hets[sampling_name] = pynei.calc_exp_het(gts).values[0]
        exp_hets = pandas.Series(exp_hets)
        exp_hets.name = "exp_het"
        return self._sort_series_by_sampling_time(exp_hets)

    def calc_num_variants(self):
        gts_per_sampling = self.get_gts_by_sampling()
        num_poly = []
        num_variables = []
        poly_ratios = []
        samplings = []
        for sampling_name, gt_info in gts_per_sampling.items():
            gts = gt_info["gts"]
            this_res = pynei.stats.calc_poly_vars_ratio(gts, poly_threshold=0.95)
            samplings.append(sampling_name)
            poly_ratios.append(this_res["poly_ratio_over_variables"]["all_indis"])
            num_variables.append(this_res["num_variable"]["all_indis"])
            num_poly.append(this_res["num_poly"]["all_indis"])
        res = pandas.DataFrame(
            {
                "Polymorphic ratio (95%)": poly_ratios,
                "Num. variables": num_variables,
                "Num. polymorphic": num_poly,
            },
            index=samplings,
        )
        times = self._get_generation_times_for_samplings(samplings)
        res["Generation"] = times
        res.sort_values(by="Generation", inplace=True)
        return res

    def calc_allele_freq_spectrum(self):
        gts_per_sampling = self.get_gts_by_sampling()
        afs_per_sampling = {}
        bin_edges = None
        for sampling_name, gt_info in gts_per_sampling.items():
            gts = gt_info["gts"]
            res = pynei.stats.calc_allele_freq_spectrum(gts)
            afs_per_sampling[sampling_name] = res["counts"]["all_indis"]
            if bin_edges is None:
                bin_edges = res["bin_edges"]
            else:
                assert numpy.allclose(bin_edges, res["bin_edges"])
        afs = pandas.DataFrame(afs_per_sampling)
        return {"counts": afs, "bin_edges": bin_edges}


def create_msprime_sampling(num_samples: int, ploidy: int, pop_name: str, time: int):
    sampling = msprime.SampleSet(
        num_samples=num_samples, population=pop_name, ploidy=ploidy, time=time
    )
    return sampling


def simulate(
    samplings: list[msprime.SampleSet],
    demography: msprime.Demography,
    seq_length_in_bp: int,
    recomb_rate=1e-8,
    add_mutations=True,
    random_seed=None,
    mutation_rate=1e-8,
    ploidy=2,
):
    tree_seqs = msprime.sim_ancestry(
        samples=samplings,
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
        samplings=samplings,
        demography=demography,
        ploidy=ploidy,
    )
