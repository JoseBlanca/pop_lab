CONFIG = {
    "title": "Balancing selection",
    "pops": {
        "pop_a": {
            "freq_A": 0.5,
            "fitness": (1, 1, 0),
            "ui_freq_options": ("allelic",),
            "immigration": {
                "rate": {"min": 0, "max": 0.2, "value": 0.1},
                "from_pop": "pop_b",
            },
        },
        "pop_b": {
            "freq_A": 0.5,
            "fitness": (0, 1, 1),
            "ui_freq_options": ("allelic",),
            "immigration": {
                "rate": {"min": 0, "max": 0.2, "value": 0.1},
                "from_pop": "pop_a",
            },
        },
    },
    "loggers": (
        "allelic_freqs_logger",
        "exp_het_logger",
    ),
}
