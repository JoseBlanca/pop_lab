import itertools

import matplotlib.pyplot as plt

COLORS = list(plt.rcParams["axes.prop_cycle"].by_key()["color"])
COLOR_CYCLE = itertools.cycle(COLORS)

MARKERS = [
    ("o", True),
    ("x", True),
    ("s", False),
    ("v", True),
    ("^", True),
    ("<", True),
    (">", True),
    ("p", True),
    ("*", True),
    ("h", True),
    ("H", True),
    ("D", True),
    ("d", True),
]
MARKER_CYCLE = itertools.cycle(MARKERS)

LINESTYLES = ["solid", "dashed", "dotted", "dashdotted", "dashdotdotted"]
LINESTYLES_CYCLE = itertools.cycle(LINESTYLES)
