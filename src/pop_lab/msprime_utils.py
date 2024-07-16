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

    def get_genotypes(self):
        samplings = self._get_sampling_info()
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
                f"{sampling['sampling_name']}-indi_{idx}"
                for idx in range(num_indis_in_sampling)
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
            new_shape = (haplotype_array.shape[0], -1, self.ploidy)
            gt_array = haplotype_array.reshape(new_shape)
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

    def calc_unbiased_exp_het(self):
        gts_per_sampling = self.get_genotypes()
        exp_hets = {}
        for sampling_name, gt_info in gts_per_sampling.items():
            gts = gt_info["gts"]
            exp_hets[sampling_name] = pynei.calc_exp_het(gts).values[0]
        exp_hets = pandas.Series(exp_hets)
        return exp_hets


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
