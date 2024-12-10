OUTPUT_SITE="built_site"
OUTPUT_HTML_DIR="$OUTPUT_SITE/html"

rm -r $OUTPUT_SITE

uv run sphinx-build -M html pop_lab_site $OUTPUT_SITE

rm -r $OUTPUT_HTML_DIR/simple_drift
uv run shinylive export src/apps/fwd/simple_drift_app/ $OUTPUT_HTML_DIR/simple_drift/
rm -r $OUTPUT_HTML_DIR/simple_selection
uv run shinylive export src/apps/fwd/simple_selection_app/ $OUTPUT_HTML_DIR/simple_selection/
rm -r $OUTPUT_HTML_DIR/balancing_selection
uv run shinylive export src/apps/fwd/balancing_selection_app/ $OUTPUT_HTML_DIR/balancing_selection/
rm -r $OUTPUT_HTML_DIR/one_locus
uv run shinylive export src/apps/fwd/one_locus_app/ $OUTPUT_HTML_DIR/one_locus/
rm -r $OUTPUT_HTML_DIR/drifting_pops
uv run shinylive export src/apps/msprime/drifting_pops_app/ $OUTPUT_HTML_DIR/drifting_pops/
rm -r $OUTPUT_HTML_DIR/bottleneck
uv run shinylive export src/apps/msprime/bottleneck_app/ $OUTPUT_HTML_DIR/bottleneck/
rm -r $OUTPUT_HTML_DIR/founder
uv run shinylive export src/apps/msprime/founder_app/ $OUTPUT_HTML_DIR/founder/
rm -r $OUTPUT_HTML_DIR/admixture
uv run shinylive export src/apps/msprime/admixture_app/ $OUTPUT_HTML_DIR/admixture/
rm -r $OUTPUT_HTML_DIR/selective_sweep
uv run shinylive export src/apps/msprime/selective_sweep_app/ $OUTPUT_HTML_DIR/selective_sweep/


cp -ra /home/jose/devel/pop_lab/$OUTPUT_HTML_DIR/* /home/jose/webs/bioinf/github_io/pop_lab/

echo "uv run python -m http.server --directory $OUTPUT_HTML_DIR/ --bind localhost 8008"