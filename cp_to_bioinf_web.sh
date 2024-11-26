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
cp -ra /home/jose/devel/pop_lab/shiny_site/* /home/jose/webs/bioinf/github_io/pop_lab/
