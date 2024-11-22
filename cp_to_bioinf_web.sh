rm -r shiny_site/one_locus
uv run shinylive export src/one_locus_app/ shiny_site/one_locus/
rm -r shiny_site/drifting_pops
uv run shinylive export src/drifting_pops_app/ shiny_site/drifting_pops/
rm -r shiny_site/bottleneck
uv run shinylive export src/bottleneck_app/ shiny_site/bottleneck/
cp -ra /home/jose/devel/pop_lab/shiny_site/* /home/jose/webs/bioinf/github_io/pop_lab/
