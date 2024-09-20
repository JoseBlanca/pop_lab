import msprime
import numpy

from pop_lab.msprime_sim_utils import (
    get_pop_names_from_demography,
    create_msprime_sample_set,
    simulate,
)


def create_simple_demography(num_pops=1, pop_size=10000):
    demography = msprime.Demography()
    for idx in range(num_pops):
        pop_name = f"pop_{idx + 1}"
        demography.add_population(
            name=pop_name, initial_size=pop_size, initially_active=True
        )
    return demography


def test_msprime_simulation():
    demography = create_simple_demography(num_pops=1)
    pop_names = get_pop_names_from_demography(demography)

    num_samples = 10
    samplings = [
        create_msprime_sample_set(
            num_samples=num_samples, ploidy=2, pop_name=pop, time=0
        )
        for pop in pop_names
    ]
    sim_res = simulate(
        samplings, demography=demography, seq_length_in_bp=1e4, random_seed=42
    )
    sim_res.get_vars_and_pop_samples()


def test_exp_het():
    demography = create_simple_demography(num_pops=1)
    pop_names = get_pop_names_from_demography(demography)

    num_samples = 20
    times = [10, 20]
    samplings = [
        create_msprime_sample_set(
            num_samples=num_samples, ploidy=2, pop_name=pop_names[0], time=time
        )
        for time in times
    ]
    sim_res = simulate(
        samplings, demography=demography, seq_length_in_bp=1e4, random_seed=42
    )
    res = sim_res.calc_unbiased_exp_het()
    assert numpy.allclose(res["exp_het"].values, [0.2707265, 0.29444444])


def test_num_vars():
    demography = create_simple_demography(num_pops=1)
    pop_names = get_pop_names_from_demography(demography)

    num_samples = 20
    times = [10, 20]
    samplings = [
        create_msprime_sample_set(
            num_samples=num_samples, ploidy=2, pop_name=pop_names[0], time=time
        )
        for time in times
    ]
    sim_res = simulate(
        samplings, demography=demography, seq_length_in_bp=1e4, random_seed=42
    )
    res = sim_res.calc_num_variants()
    assert numpy.allclose(res["Num. variables"].values, [12, 10])
    assert numpy.allclose(res["Num. polymorphic"].values, [9, 9])

    res = sim_res.calc_allele_freq_spectrum()
    expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 0, 3, 1, 0, 2, 2]
    assert numpy.all(numpy.equal(res["counts"]["pop_1_10"].values, expected))
