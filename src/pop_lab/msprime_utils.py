import pandas
import msprime

import pynei


def get_pop_names_from_demography(demography):
    return [deme.name for deme in demography.to_demes().demes]


class SimulationResult:
    def __init__(self, tree_seqs, sampling_times, demography, ploidy):
        self.tree_seqs = tree_seqs
        self.sampling_times = sampling_times
        self.demography = demography
        self.ploidy = ploidy

    def get_genotypes(self, sampling_times=None, pop_names=None, sampling_info=None):
        samplings = self._get_samplings(
            sampling_times=sampling_times,
            pop_names=pop_names,
            sampling_info=sampling_info,
        )
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

    def _get_samplings(self, sampling_times=None, pop_names=None, sampling_info=None):

        if sampling_info is not None:
            if sampling_times is not None or pop_names is not None:
                msg = (
                    "if samples are given, sampling_times and pop_names should be None"
                )
                raise ValueError(msg)
            return self._get_samplings_from_sampling_info(sampling_info)

        if sampling_times is None:
            sampling_times = [None]
        elif isinstance(sampling_times, (int, float)):
            sampling_times = [sampling_times]
        if pop_names is not None:
            pop_names = list(pop_names)

        if len(sampling_times) == 1:
            return self._get_samplings_for_pops(
                sampling_time=sampling_times[0], pop_names=pop_names
            )
        elif pop_names is None or len(pop_names) == 1:
            if pop_names is None:
                pop_name = pop_names
            else:
                pop_name = pop_names[0]
            return self._get_samplings_for_times(
                sampling_times=sampling_times, pop_name=pop_name
            )
        else:
            raise NotImplementedError("Fixme")

    def _get_samples_from_sampling_info(self, sampling_info):
        samplings = []
        tree_seqs = self.tree_seqs
        pop_ids_by_pop_name_in_tseq, _ = self._get_pop_ids_and_names()
        for pop_name, sampling_time in sampling_info:
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

    def _get_samplings_for_pops(self, sampling_time=None, pop_names=None):

        res = self._get_pop_ids_and_names()
        pop_ids_by_pop_name_in_tseq, pop_names_by_pop_id_in_tseq = res

        if pop_names is None:
            pop_names = list(sorted(pop_ids_by_pop_name_in_tseq.keys()))

        if sampling_time is None:
            if len(self.sampling_times) == 1:
                sampling_time = self.sampling_times[0]
            else:
                msg = "You have samplings at different times, so you have to set one sample time"
                raise ValueError(msg)
        if sampling_time not in self.sampling_times:
            msg = f"Sampling time ({sampling_time}) not in available sampling times ({self.sampling_times})"
            raise ValueError(msg)

        if pop_names:
            pop_ids = [pop_ids_by_pop_name_in_tseq[pop_name] for pop_name in pop_names]
        else:
            pop_ids = sorted(pop_ids_by_pop_name_in_tseq.values())

        tree_seqs = self.tree_seqs

        samplings = []
        for pop_id in pop_ids:
            pop_name = pop_names_by_pop_id_in_tseq[pop_id]
            sampling = {
                "sampling_node_ids": tree_seqs.samples(
                    population=pop_id, time=sampling_time
                ),
                "sampling_time": sampling_time,
                "pop_name": pop_name,
                "sampling_name": pop_name,
            }
            if sampling["sampling_node_ids"].size == 0:
                continue
            samplings.append(sampling)
        return samplings

    def _get_samplings_for_times(self, sampling_times, pop_name=None):
        res = self._get_pop_ids_and_names()
        pop_ids_by_pop_name_in_tseq, _ = res

        if pop_name is None:
            if len(pop_ids_by_pop_name_in_tseq) == 1:
                pop_id = list(pop_ids_by_pop_name_in_tseq.values())[0]
            else:
                msg = "You have more than one pop, so you have to set one pop"
                raise ValueError(msg)
        else:
            pop_id = pop_ids_by_pop_name_in_tseq[pop_name]

        for sampling_time in sampling_times:
            if sampling_time not in self.sampling_times:
                msg = f"Sampling time ({sampling_time}) not in available sampling times ({self.sampling_times})"
                raise ValueError(msg)

        tree_seqs = self.tree_seqs

        samplings = []
        for sampling_time in sampling_times:
            sample = {
                "sampling_node_ids": tree_seqs.sample(
                    population=pop_id, time=sampling_time
                ),
                "sampling_time": sampling_time,
                "pop_name": pop_name,
                "sampling_name": f"{pop_name}_{sampling_time}",
            }
            if sample["sampling_node_ids"].size == 0:
                continue
            samplings.append(sample)
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

    sampling_times = sorted({sampling.time for sampling in samplings})

    return SimulationResult(
        tree_seqs=tree_seqs,
        sampling_times=sampling_times,
        demography=demography,
        ploidy=ploidy,
    )
