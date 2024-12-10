from pathlib import Path
import shutil
from subprocess import run

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_SITE_SPHINX_DIR = PROJECT_DIR / "built_site"
OUTPUT_HTML_DIR = OUTPUT_SITE_SPHINX_DIR / "html"
POPLAB_SPHINX_SRC_DIR = PROJECT_DIR / "pop_lab_site"
APPS_SRC_DIR = PROJECT_DIR / "src" / "apps"
FWD_APPS_SRC_DIR = APPS_SRC_DIR / "fwd"
FWD_APP_NAMES = [
    "balancing_selection",
    "one_locus",
    "simple_drift",
    "simple_one_locus",
    "simple_selection",
]
MSPRIME_APPS_SRC_DIR = APPS_SRC_DIR / "msprime"
MSPRIME_APPS = [
    "admixture",
    "bottleneck",
    "drifting_pops",
    "founder",
    "selective_sweep",
]


def create_sphinx_site():
    cmd = [
        "uv",
        "run",
        "sphinx-build",
        "-M",
        "html",
        str(POPLAB_SPHINX_SRC_DIR),
        OUTPUT_SITE_SPHINX_DIR,
    ]
    run(cmd, check=True)


def create_apps(app_names, apps_src_base_dir, output_base_dir):
    for app_name in app_names:
        app_dir = apps_src_base_dir / f"{app_name}_app"
        output_dir = output_base_dir / app_name
        if output_dir.exists():
            shutil.rmtree(output_dir)
        cmd = ["uv", "run", "shinylive", "export", str(app_dir), str(output_dir)]
        run(cmd, check=True)


if OUTPUT_SITE_SPHINX_DIR.exists():
    shutil.rmtree(OUTPUT_SITE_SPHINX_DIR)

create_sphinx_site()
create_apps(FWD_APP_NAMES, FWD_APPS_SRC_DIR, OUTPUT_HTML_DIR)
create_apps(MSPRIME_APPS, MSPRIME_APPS_SRC_DIR, OUTPUT_HTML_DIR)

SERVE_CMD = (
    f"uv run python -m http.server --directory {OUTPUT_HTML_DIR} --bind localhost 8008"
)
print("You can serve the web site with the command:")
print(SERVE_CMD)
