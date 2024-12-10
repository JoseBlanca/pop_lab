CONFIG = {
    "title": "Selection",
    "pops": {
        "pop": {
            "freq_A": 0,
            "ui_freq_options": ("allelic", "genotypic"),
            "fitness": (1, 0.8, 0.8),
            "mutation": {"a2A": 0.01, "A2a": 0},
        },
    },
    "loggers": (
        "allelic_freqs_logger",
        "genotypic_freqs_logger",
    ),
}
