rm -r shiny_site/simple_drift
uv run shinylive export src/apps/fwd/simple_drift_app/ shiny_site/simple_drift/
rm -r shiny_site/simple_selection
uv run shinylive export src/apps/fwd/simple_selection_app/ shiny_site/simple_selection/
rm -r shiny_site/balancing_selection
uv run shinylive export src/apps/fwd/balancing_selection_app/ shiny_site/balancing_selection/
rm -r shiny_site/one_locus
uv run shinylive export src/apps/fwd/one_locus_app/ shiny_site/one_locus/
rm -r shiny_site/drifting_pops
uv run shinylive export src/apps/msprime/drifting_pops_app/ shiny_site/drifting_pops/
rm -r shiny_site/bottleneck
uv run shinylive export src/apps/msprime/bottleneck_app/ shiny_site/bottleneck/
rm -r shiny_site/founder
uv run shinylive export src/apps/msprime/founder_app/ shiny_site/founder/
rm -r shiny_site/admixture
uv run shinylive export src/apps/msprime/admixture_app/ shiny_site/admixture/
rm -r shiny_site/selective_sweep
uv run shinylive export src/apps/msprime/selective_sweep_app/ shiny_site/selective_sweep/


cp -ra /home/jose/devel/pop_lab/shiny_site/* /home/jose/webs/bioinf/github_io/pop_lab/

echo "python3 -m http.server --directory shiny_site/ --bind localhost 8008"