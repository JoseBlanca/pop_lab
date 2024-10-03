import shutil
from pathlib import Path
from subprocess import run

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_SITE = PROJECT_DIR / "shiny_site"
# OUTPUT_SITE = Path.home() / "webs" / "bioinf" / "github_io" / "pop_lab"

SRC_DIR = Path(__file__).parent
PYNEI_DIR = PROJECT_DIR / ".." / "pynei" / "src" / "pynei"

SHINY_BASE_CMD = ("uv", "run", "shinylive", "export")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pop Lab</title>
</head>
<body>
    <h1>Welcome to Pop Lab</h1>
    <ul>{list_items}</ul>
</body>
</html>"""


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


def export_msprime_site(app_src_dir, output_site_dir, pynei_dir):
    if pynei_dir:
        app_pynei_dir = app_src_dir / "pynei"
        if app_pynei_dir.exists():
            shutil.rmtree(app_pynei_dir)
        shutil.copytree(pynei_dir, app_pynei_dir)

    export_shiny_site(app_src_dir, output_site_dir)


def write_index_html(output_dir, lis):
    index_path = output_dir / "index.html"
    html = HTML_TEMPLATE.format(list_items="\n".join(lis))
    with index_path.open("wt") as fhand:
        fhand.write(html)


LI_TEMPLATE = '<li><a href="{app_url}">{app_name}</a></li>'


clean_dir(OUTPUT_SITE)

app = "one_locus"
ONE_LOCUS_OUTPUT_SITE = OUTPUT_SITE / app
ONE_LOCUS_APP_SRC = SRC_DIR / f"{app}_app"
export_one_locus_site(ONE_LOCUS_APP_SRC, ONE_LOCUS_OUTPUT_SITE)

lis = [LI_TEMPLATE.format(app_name=app, app_url=f"{app}/")]

MSPRIME_APPS = ["bottleneck", "drifting_pops"]
for app in MSPRIME_APPS:
    export_msprime_site(SRC_DIR / f"{app}_app", OUTPUT_SITE / app, PYNEI_DIR)
    lis.append(LI_TEMPLATE.format(app_name=app, app_url=f"{app}/"))


SERVE_CMD = (
    f"uv run python -m http.server --directory {OUTPUT_SITE} --bind localhost 8008"
)
print("you can serve the site by running:")
print(SERVE_CMD)

write_index_html(OUTPUT_SITE, lis)
