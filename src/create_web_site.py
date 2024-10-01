import shutil
from pathlib import Path
from subprocess import run

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_SITE = PROJECT_DIR / "shiny_site"
# OUTPUT_SITE = Path.home() / "webs" / "bioinf" / "github_io" / "pop_lab"

SRC_DIR = Path(__file__).parent
ONE_LOCUS_OUTPUT_SITE = OUTPUT_SITE / "one_locus"
ONE_LOCUS_APP_SRC = SRC_DIR / "one_locus_app"
PYNEI_DIR = PROJECT_DIR / ".." / "pynei" / "src" / "pynei"

SHINY_BASE_CMD = ("uv", "run", "shinylive", "export")


def clean_dir(dir):
    if dir.exists():
        shutil.rmtree(dir)
    dir.mkdir()


def export_shiny_site(app_src_dir, output_site_dir):
    output_site_dir.mkdir()
    cmd = list(SHINY_BASE_CMD)
    cmd.append(str(app_src_dir))
    cmd.append(str(output_site_dir))
    print(cmd)
    run(cmd, check=True)


def export_one_locus_site(app_src_dir, output_site_dir):
    export_shiny_site(app_src_dir, output_site_dir)


def export_bottleneck_site(app_src_dir, output_site_dir, pynei_dir):
    if pynei_dir:
        app_pynei_dir = app_src_dir / "pynei"
        if app_pynei_dir.exists():
            shutil.rmtree(app_pynei_dir)
        shutil.copytree(pynei_dir, app_pynei_dir)

    export_shiny_site(app_src_dir, output_site_dir)


clean_dir(OUTPUT_SITE)

export_one_locus_site(ONE_LOCUS_APP_SRC, ONE_LOCUS_OUTPUT_SITE)

BOTTLENECK_APP_SRC = SRC_DIR / "bottleneck_app"
BOTTLENECK_OUTPUT_SITE = OUTPUT_SITE / "bottleneck"
export_bottleneck_site(BOTTLENECK_APP_SRC, BOTTLENECK_OUTPUT_SITE, PYNEI_DIR)

SERVE_CMD = (
    f"uv run python -m http.server --directory {OUTPUT_SITE} --bind localhost 8008"
)
print("you can serve the site by running:")
print(SERVE_CMD)
