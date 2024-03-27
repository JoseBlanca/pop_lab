from typing import Callable, Iterable
import random
import math
from array import array
from collections import defaultdict, namedtuple

import numpy
import pandas

INF = math.inf

MENDELIAN_SEGREGATIONS = {
    ("AA", "AA"): [(1, 0, 0)],
    ("aa", "aa"): [(0, 0, 1)],
    ("AA", "aa"): [(0, 1, 0)],
    ("aa", "AA"): [(0, 1, 0)],
    ("AA", "Aa"): ((1, 0, 0), (0, 1, 0)),
    ("Aa", "AA"): ((1, 0, 0), (0, 1, 0)),
    ("aa", "Aa"): ((0, 0, 1), (0, 1, 0)),
    ("Aa", "aa"): ((0, 0, 1), (0, 1, 0)),
    ("Aa", "Aa"): (
        (1, 0, 0),
        (0, 1, 0),
        (0, 1, 0),
        (0, 0, 1),
    ),
}


class GenotypicFreqs:
    def __init__(self, freq_AA: float, freq_Aa: float, freq_aa: float | None = None):
        freq_AA = float(freq_AA)
        freq_Aa = float(freq_Aa)

        if freq_AA > 1:
            raise ValueError("freq AA can not be larger than 1")
        if freq_AA < 0:
            raise ValueError("freq AA can not be lower than 0")
        if freq_Aa < 0:
            raise ValueError("freq Aa can not be lower than 0")
        if freq_AA + freq_Aa > 1:
            raise ValueError("AA + Aa freqs cannot be greater than 1")

        self._AA = freq_AA
        self._Aa = freq_Aa
        expected_freq_aa = 1 - self._AA - self._Aa
        if freq_aa is not None:
            if freq_aa < 0:
                raise ValueError("freq A0 can not be lower than 0")
            if not math.isclose(expected_freq_aa, freq_aa, abs_tol=0.01):
                raise ValueError(
                    f"freq_aa ({freq_aa}) should be 1 - freq_AA - freq_Aa ({expected_freq_aa})"
                )
        freq_aa = expected_freq_aa

        if not math.isclose(freq_aa + freq_AA + freq_Aa, 1):
            raise ValueError("Genotypic freqs should sum 1")
        self._aa = freq_aa

    @property
    def freqs(self):
        return (self.AA, self.Aa, self.aa)

    @property
    def A(self):
        return self._AA + self._Aa * 0.5

    @property
    def AA(self):
        return self._AA

    @property
    def Aa(self):
        return self._Aa

    @property
    def aa(self):
        return self._aa

    def __repr__(self):
        return f"{self.__class__.__name__}({self.AA}, {self.Aa}, {self.aa})"


class AllelicFreqs:
    def __init__(self, freq_A):
        self.A = freq_A
        freq_a = 1 - freq_A
        self.a = freq_a
        if not math.isclose(freq_A + freq_a, 1):
            raise ValueError("Allelic freqs should sum 1")

    def __str__(self):
        return f"A: {self.A}, a: {self.a}"


Fitness = namedtuple("Fitness", ("w11", "w12", "w22"))

MutRates = namedtuple("MutRates", ("A2a", "a2A"))


def calc_allelic_freq(genotypic_freqs: GenotypicFreqs):
    return genotypic_freqs.AA + genotypic_freqs.Aa * 0.5


def calc_allelic_freqs(genotypic_freqs: GenotypicFreqs):
    return AllelicFreqs(calc_allelic_freq(genotypic_freqs))


def calc_hwe_genotypic_freqs(allelic_freqs: AllelicFreqs):
    freq_AA = allelic_freqs.A**2
    freq_Aa = 2 * allelic_freqs.A * allelic_freqs.a
    return GenotypicFreqs(freq_AA, freq_Aa)


def _calc_w_avg(genotypic_freqs, fitness):
    if fitness is None:
        raise ValueError("fitness is None")
    w_avg = (
        genotypic_freqs.AA * fitness.w11
        + genotypic_freqs.Aa * fitness.w12
        + genotypic_freqs.aa * fitness.w22
    )
    return w_avg


class Population:
    def __init__(
        self,
        id: str,
        genotypic_freqs: GenotypicFreqs,
        size: int | float = INF,
        fitness: Fitness | None = None,
        mut_rates: MutRates | None = None,
        selfing_rate: float = 0.0,
    ):
        self.id = id
        self.size = size
        self.genotypic_freqs = genotypic_freqs
        self.selfing_rate = selfing_rate

        if fitness is not None:
            w_avg = _calc_w_avg(genotypic_freqs, fitness)
            if math.isclose(w_avg, 0):
                msg = "fitness is 0 because the remaining genotypes have a zero fitness, population would die"
                raise ValueError(msg)
        self.fitness = fitness

        self.mut_rates = mut_rates

    @property
    def allelic_freqs(self):
        genotypic_freqs = self.genotypic_freqs
        return AllelicFreqs(calc_allelic_freq(genotypic_freqs))

    def _choose_parent(self, freq_AA, freq_Aa):
        value = random.uniform(0, 1)
        if value < freq_AA:
            return "AA"
        elif value >= (freq_AA + freq_Aa):
            return "aa"
        else:
            return "Aa"

    def evolve_to_next_generation(self, migration_origins=None):
        genotypic_freqs = self.genotypic_freqs

        if migration_origins is None:
            migration_origins = []

        freq_AA = genotypic_freqs.AA
        freq_Aa = genotypic_freqs.Aa

        # migration
        this_pop_contribution = 1 - sum(
            [origin["inmigrant_rate"] for origin in migration_origins]
        )
        if this_pop_contribution < 0:
            raise ValueError(f"Too many inmigrants for pop {self.id}, more than 100%")

        freq_AA = this_pop_contribution * freq_AA + sum(
            [
                origin["from_pop"].genotypic_freqs.AA * origin["inmigrant_rate"]
                for origin in migration_origins
            ]
        )
        freq_Aa = this_pop_contribution * freq_Aa + sum(
            [
                origin["from_pop"].genotypic_freqs.Aa * origin["inmigrant_rate"]
                for origin in migration_origins
            ]
        )
        freq_aa = this_pop_contribution * genotypic_freqs.aa + sum(
            [
                origin["from_pop"].genotypic_freqs.aa * origin["inmigrant_rate"]
                for origin in migration_origins
            ]
        )
        assert math.isclose(freq_AA + freq_Aa + freq_aa, 1)

        # selection
        fitness = self.fitness
        if fitness is not None:
            w_avg = _calc_w_avg(genotypic_freqs, fitness)
            if math.isclose(w_avg, 0):
                msg = "fitness is 0 because the remaining genotypes have a zero fitness, population would die"
                raise RuntimeError(msg)

            freq_AA = freq_AA * fitness.w11 / w_avg
            freq_Aa = freq_Aa * fitness.w12 / w_avg
        else:
            freq_AA = freq_AA
            freq_Aa = freq_Aa

        # mutation
        if self.mut_rates:
            mu = self.mut_rates.A2a
            mu2 = mu**2
            nu = self.mut_rates.a2A
            nu2 = nu**2
            AA0 = freq_AA
            Aa0 = freq_Aa
            aa0 = 1 - freq_AA - freq_Aa

            new_aa = AA0 * mu2 + Aa0 * mu
            new_AA = aa0 * nu2 + Aa0 * nu
            new_Aa = 2 * AA0 * mu + 2 * aa0 * nu
            AA_removed = AA0 * mu2 + 2 * AA0 * mu
            aa_removed = aa0 * nu2 + 2 * aa0 * nu
            Aa_removed = Aa0 * mu + Aa0 * nu

            AA1 = AA0 + new_AA - AA_removed
            Aa1 = Aa0 + new_Aa - Aa_removed
            aa1 = aa0 + new_aa - aa_removed
            assert math.isclose(AA1 + Aa1 + aa1, 1)
            freq_AA = AA1
            freq_Aa = Aa1

        # drift
        selfing_rate = self.selfing_rate
        if self.size is None or math.isinf(self.size):
            # selfed indivuals
            selfed_freq_AA1 = freq_AA + freq_Aa * 0.25
            selfed_freq_Aa1 = freq_Aa * 0.5
            # non selfed individuals
            allelic_freqs = calc_allelic_freqs(GenotypicFreqs(freq_AA, freq_Aa))
            panmix_genotypic_freqs = calc_hwe_genotypic_freqs(allelic_freqs)
            # final freqs
            freq_AA = selfed_freq_AA1 * selfing_rate + panmix_genotypic_freqs.AA * (
                1 - selfing_rate
            )
            freq_Aa = selfed_freq_Aa1 * selfing_rate + panmix_genotypic_freqs.Aa * (
                1 - selfing_rate
            )
        else:
            num_AA = 0
            num_Aa = 0
            num_aa = 0
            for _ in range(self.size):
                parent1 = self._choose_parent(freq_AA, freq_Aa)

                parent2 = None
                if selfing_rate is not None:
                    value = random.uniform(0, 1)
                    if value < selfing_rate:
                        parent2 = parent1
                if parent2 is None:
                    parent2 = self._choose_parent(freq_AA, freq_Aa)

                mendelian_choices = MENDELIAN_SEGREGATIONS[(parent1, parent2)]
                if len(mendelian_choices) == 1:
                    descendants = mendelian_choices[0]
                else:
                    descendants = random.choice(mendelian_choices)
                num_AA += descendants[0]
                num_Aa += descendants[1]
                num_aa += descendants[2]

            total_indis = num_AA + num_Aa + num_aa
            assert total_indis == self.size

            freq_AA = num_AA / total_indis
            freq_Aa = num_Aa / total_indis

        self.genotypic_freqs = GenotypicFreqs(freq_AA, freq_Aa)


def _update_events(demographic_events, num_generation, active_migrations):
    for event in demographic_events:
        event_num_generation = event.get("num_generation")
        if event_num_generation is not None and event_num_generation != num_generation:
            continue

        if event["type"] == "size_change":
            event["pop"].size = event["new_size"]
        elif event["type"] == "migration_start":
            active_migrations[event["id"]] = event
        elif event["type"] == "migration_stop":
            del active_migrations[event["migration_id"]]


def simulate_forward_in_time(
    pops: list[Population],
    num_generations: int,
    loggers: list[Callable],
    demographic_events: list[dict] | None = None,
    random_seed: int | None = None,
):
    if random_seed is not None:
        numpy.random.seed(random_seed)
        random.seed(random_seed)

    for logger in loggers:
        logger(pops, num_generation=1)

    if demographic_events is None:
        demographic_events = []
    active_migrations = {}
    _update_events(demographic_events, 1, active_migrations)

    for num_generation in range(2, num_generations + 1):
        _update_events(demographic_events, num_generation, active_migrations)

        for pop in pops:
            migration_origin_pops = defaultdict(list)
            for migration in active_migrations.values():
                if migration["to_pop"].id == pop.id:
                    migration_origin_pops[pop.id].append(
                        {
                            "from_pop": migration["from_pop"],
                            "inmigrant_rate": migration["inmigrant_rate"],
                        }
                    )
            pop.evolve_to_next_generation(migration_origin_pops[pop.id])

        for logger in loggers:
            logger(pops, num_generation)


class _PerPopLogger:
    def __init__(self):
        self._values_per_generation = None
        self._generations = array("L")

    @classmethod
    def from_loggers(cls, loggers):
        logger = cls()
        logger._values_per_generation = pandas.concat(
            [logger.values_per_generation for logger in loggers], axis=1
        )
        logger._generations = logger._values_per_generation.index
        return logger

    def __call__(self, pops: Iterable[Population], num_generation: int):
        self._generations.append(num_generation)

        if self._values_per_generation is None:
            values = {pop.id: array("f") for pop in pops}
            self._values_per_generation = values
        else:
            values = self._values_per_generation

        for pop in pops:
            values[pop.id].append(self._calc_value_for_pop(pop))

    @property
    def values_per_generation(self):
        values = self._values_per_generation
        values = pandas.DataFrame(values, index=self._generations)
        return values


class AllelicFreqLogger(_PerPopLogger):
    def _calc_value_for_pop(self, pop):
        return calc_allelic_freq(pop.genotypic_freqs)


class PopSizeLogger(_PerPopLogger):
    def _calc_value_for_pop(self, pop):
        size = pop.size
        if size is None:
            size = math.inf
        return size


class ExpHetLogger(_PerPopLogger):
    def _calc_value_for_pop(self, pop):
        freq_A = calc_allelic_freq(pop.genotypic_freqs)
        exp_het = 2 * freq_A * (1 - freq_A)
        return exp_het


GENOTYPIC_FREQS_NAMES = ["freqs_AA", "freqs_Aa", "freqs_aa"]


class GenotypicFreqsLogger:
    def __init__(self):
        self._values_per_generation = None
        self._generations = array("L")

    @classmethod
    def from_loggers(cls, loggers):
        logger = cls()
        values = {}
        for genotypic_freq_name in loggers[0].values_per_generation.keys():
            values[genotypic_freq_name] = pandas.concat(
                [
                    logger.values_per_generation[genotypic_freq_name]
                    for logger in loggers
                ],
                axis=1,
            )

        logger._values_per_generation = values
        logger._generations = values[genotypic_freq_name].index
        return logger

    def __call__(self, pops: Iterable[Population], num_generation: int):
        self._generations.append(num_generation)

        if self._values_per_generation is None:
            values = {}
            for genotypic_freq_name in GENOTYPIC_FREQS_NAMES:
                values[genotypic_freq_name] = {}
                for pop in pops:
                    values[genotypic_freq_name][pop.id] = array("f")
            self._values_per_generation = values
        else:
            values = self._values_per_generation

        for pop in pops:
            for genotypic_freq_name, value in zip(
                GENOTYPIC_FREQS_NAMES, pop.genotypic_freqs.freqs
            ):
                values[genotypic_freq_name][pop.id].append(value)

    @property
    def values_per_generation(self):
        values = self._values_per_generation
        dframes = {}
        for genotypic_freq_name, freqs in values.items():
            dframes[genotypic_freq_name] = pandas.DataFrame(
                freqs, index=self._generations
            )
        return dframes


LOGGER_CLASSES = {
    "allelic_freqs_logger": AllelicFreqLogger,
    "pop_size_logger": PopSizeLogger,
    "genotypic_freqs_logger": GenotypicFreqsLogger,
    "exp_het_logger": ExpHetLogger,
}
LOGGER_PARAMETERS = {
    AllelicFreqLogger: "allelic_freqs",
    PopSizeLogger: "pop_sizes",
    GenotypicFreqsLogger: "genotypic_freqs",
    ExpHetLogger: "expected_hets",
}


class OneLocusTwoAlleleSimulation:
    def __init__(self, sim_definition: dict):
        pops = self._create_pops(sim_definition["pops"])
        events = self._create_demographic_events(
            sim_definition.get("demographic_events", {}), pops
        )
        loggers = self._create_loggers(sim_definition["loggers"])
        simulate_forward_in_time(
            list(pops.values()),
            num_generations=sim_definition["num_generations"],
            demographic_events=events,
            loggers=loggers,
        )
        self.results = self._gather_results(loggers)

    @staticmethod
    def _create_pops(pop_definitions):
        pops = {}
        for pop_id in sorted(pop_definitions.keys()):
            pop_def = pop_definitions[pop_id]
            kwargs = {}
            kwargs["genotypic_freqs"] = GenotypicFreqs(*pop_def["genotypic_freqs"])
            if "size" in pop_def:
                kwargs["size"] = int(pop_def["size"])
            if "fitness" in pop_def:
                kwargs["fitness"] = Fitness(*pop_def["fitness"])
            if "mut_rates" in pop_def:
                kwargs["mut_rates"] = MutRates(*pop_def["mut_rates"])
            kwargs["selfing_rate"] = float(pop_def.get("selfing_rate", 0.0))

            pops[pop_id] = Population(pop_id, **kwargs)
        return pops

    @staticmethod
    def _create_demographic_events(demographic_events, pops):
        events = []
        for event_id, event in demographic_events.items():
            event["id"] = event_id
            for key in ["pop", "from_pop", "to_pop"]:
                if key in event:
                    event[key] = pops[event[key]]
            events.append(event)
        return events

    @staticmethod
    def _create_loggers(loggers):
        logger_objs = []
        for logger in loggers:
            logger_objs.append(LOGGER_CLASSES[logger]())
        return logger_objs

    @staticmethod
    def _gather_results(loggers):
        results = {}
        for logger in loggers:
            param = LOGGER_PARAMETERS[logger.__class__]
            values = logger.values_per_generation
            results[param] = values
        return results


def simulate(
    pops: list[Population],
    num_generations: int,
    loggers: list[Callable],
    demographic_events: list[dict] | None = None,
    random_seed: int | None = None,
):
    if random_seed is not None:
        numpy.random.seed(random_seed)
        random.seed(random_seed)

    for logger in loggers:
        logger(pops, num_generation=1)

    if demographic_events is None:
        demographic_events = []
    active_migrations = {}
    _update_events(demographic_events, 1, active_migrations)

    for num_generation in range(2, num_generations + 1):
        _update_events(demographic_events, num_generation, active_migrations)

        for pop in pops:
            migration_origin_pops = defaultdict(list)
            for migration in active_migrations.values():
                if migration["to_pop"].id == pop.id:
                    migration_origin_pops[pop.id].append(
                        {
                            "from_pop": migration["from_pop"],
                            "inmigrant_rate": migration["inmigrant_rate"],
                        }
                    )
            pop.evolve_to_next_generation(migration_origin_pops[pop.id])

        for logger in loggers:
            logger(pops, num_generation)


def simulate_one_locus_two_alleles_one_pop(
    freq_AA,
    freq_Aa,
    freq_aa,
    pop_size=INF,
    num_generations=100,
    w11=1,
    w12=1,
    w22=1,
    A2a=0,
    a2A=0,
    selfing_rate=0,
    num_populations=1,
):

    if (w11, w12, w22) == (1, 1, 1):
        fitness = None
    else:
        fitness = Fitness(w11=w11, w12=w12, w22=w22)

    if A2a == 0 and a2A == 0:
        mut_rates = None
    else:
        mut_rates = MutRates(A2a, a2A)

    loggers = {
        "genotypic_freqs_logger": [],
        "allelic_freqs_logger": [],
        "exp_het_logger": [],
    }
    for idx in range(num_populations):
        genotypic_freqs = GenotypicFreqs(
            freq_AA=freq_AA, freq_Aa=freq_Aa, freq_aa=freq_aa
        )
        pop = Population(
            id=f"pop{idx}",
            size=pop_size,
            genotypic_freqs=genotypic_freqs,
            fitness=fitness,
            mut_rates=mut_rates,
            selfing_rate=selfing_rate,
        )

        allelic_freqs_logger = AllelicFreqLogger()
        genotypic_freqs_logger = GenotypicFreqsLogger()
        exp_het_logger = ExpHetLogger()
        simulate(
            pops=[pop],
            num_generations=num_generations,
            demographic_events=None,
            random_seed=None,
            loggers=[allelic_freqs_logger, genotypic_freqs_logger, exp_het_logger],
        )
        loggers["genotypic_freqs_logger"].append(genotypic_freqs_logger)
        loggers["allelic_freqs_logger"].append(allelic_freqs_logger)
        loggers["exp_het_logger"].append(exp_het_logger)

    loggers = {
        key: logger_list[0].__class__.from_loggers(logger_list)
        for key, logger_list in loggers.items()
    }

    return loggers
