CONFIG = {
    "title": "One locus two alleles simulation",
    "pops": {
        "pop": {
            "freq_A": 0.5,
            "ui_freq_options": ("allelic", "genotypic"),
            "fitness": (1, 1, 1),
            "mutation": {"a2A": 0.0, "A2a": 0.0},
            "selfing_rate": 0,
        },
    },
    "loggers": (
        "allelic_freqs_logger",
        "genotypic_freqs_logger",
        "exp_het_logger",
    ),
    "num_simulations": {"value": 1},
}
