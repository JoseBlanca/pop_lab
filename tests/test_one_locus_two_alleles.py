import math

import pytest
import numpy

from pop_lab.one_locus_two_alleles_simulator import (
    simulate_forward_in_time,
    Population,
    GenotypicFreqs,
    GenotypicFreqsLogger,
)
from pop_lab import OneLocusTwoAlleleSimulation, Fitness


def test_genotypic_freqs():
    freqs = GenotypicFreqs(1, 0)
    assert numpy.allclose([1, 0, 0], freqs.freqs)

    freqs = GenotypicFreqs(0.5, 0, 0.5)
    assert numpy.allclose([0.5, 0, 0.5], freqs.freqs)

    with pytest.raises(ValueError):
        freqs = GenotypicFreqs(1, 0.5)

    with pytest.raises(ValueError):
        freqs = GenotypicFreqs(1, 0, 0.1)


def test_population():
    pop = Population("pop1", GenotypicFreqs(0.5, 0, 0.5))
    assert math.isclose(pop.allelic_freqs.A, 0.5)
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.5)
    assert numpy.allclose(pop.genotypic_freqs.freqs, [0.25, 0.5, 0.25])


def test_simulate():
    pop = Population("pop1", GenotypicFreqs(0.5, 0, 0.5))
    logger = GenotypicFreqsLogger()
    simulate_forward_in_time([pop], num_generations=2, loggers=[logger])
    numpy.allclose(logger.values_per_generation["freqs_Aa"]["pop1"], [0.0, 0.5])


def test_simulator():
    sim = {
        "pops": {
            "pop1": {"genotypic_freqs": (0.5, 0, 0.5)},
            "pop2": {"genotypic_freqs": (0.3, 0, 0.7)},
        },
        "num_generations": 2,
        "demographic_events": {
            "event1": {
                "type": "size_change",
                "pop": "pop1",
                "new_size": 1000,
                "num_generation": 100,
            },
            "migration_pop1_to_pop2": {
                "type": "migration_start",
                "from_pop": "pop2",
                "to_pop": "pop1",
                "inmigrant_rate": 0.1,
                "num_generation": 2,
            },
            "migration_stop": {
                "migration_id": "migration_pop1_to_pop2",
                "num_generation": 20,
                "type": "migration_stop",
            },
        },
        "loggers": [
            "allelic_freqs_logger",
            "pop_size_logger",
            "genotypic_freqs_logger",
            "exp_het_logger",
        ],
    }
    sim = OneLocusTwoAlleleSimulation(sim)
    assert numpy.allclose(sim.results["allelic_freqs"]["pop1"], [0.5, 0.48])


def test_selection():
    pop = Population(
        "pop1", GenotypicFreqs(0.99, 0.01, 0), fitness=Fitness(0.01, 0.01, 1)
    )
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.9949999999999992)

    pop = Population(
        "pop1", GenotypicFreqs(0.99, 0.01, 0), fitness=Fitness(0.99, 0.99, 1)
    )
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.995)

    pop = Population(
        "pop1", GenotypicFreqs(0.5, 0, 0.5), fitness=Fitness(0.01, 0.01, 1)
    )
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.009900990099009901)

    pop = Population(
        "pop1", GenotypicFreqs(0.5, 0, 0.5), fitness=Fitness(0.99, 0.99, 1)
    )
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.4974874371859296)
    pop = Population(
        "pop1", GenotypicFreqs(0.99, 0, 0.01), fitness=Fitness(0.99, 0.99, 1)
    )
    pop.evolve_to_next_generation()
    assert math.isclose(pop.allelic_freqs.A, 0.9899000100999898)
