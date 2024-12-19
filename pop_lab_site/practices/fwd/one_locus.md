# One locus foward in time

The one locus foward in time applications simulate one locus with two alleles (A and a) in one or more populations.

Several parameters can be set to configure each simulation, and then, by clicking the "Run simulation" button, the simulation will be carried out and the results plotted.

[One locus forward in time simulation application](<http:../../one_locus/>)

## Initial genotypic frequencies

The initial genotypic frequencies can be set following two paths.

If Hardy-Weinberg is assumed, only the A initial allelic frequency should be set, and the genotypic frequencies will be calculated using the standard formulas.

If we need more control of the initial genotypic frequencies we can choose the "No HW" option and we will be presented with one slider with two knobs that allows us to selected all three genotypic frequencies: AA, Aa and aa. 

## Population size

The population size can be set to infinite or to a particular number of individuals depending if we want to run simulations with genetic drift or not.

## Selection

Simulations will consider the effect of selection if we set the fitness of any one of the genotypes to any value different than one.

## Mutation

Two mutation rates can be set: the mutation rate of the A allele to a and from a to A.
This rate represents the proportion, over 1, of the alleles of each type that will be converted to the other type in any generation.

## Selfing

By default populations will have a selfing rate, a proportion of individuals originated from selfing, of zero, but this value can be changed to create even complete autogamous populations.

## Number of generations

We can choose for how many generation we want to run the simulations.

## Number of parallel simulations

More than one simulations can be run at the same time with the same parameters.
This option will be particulary useful to see the result of the genetic drift.

## Allelic frequencies

One important result is the evolution of the allelic frequencies.
The application will plot the A allelic frequency evolution and will create a table with the initial and final frequencies.

## Genotypic frequencies

Plots for all three genotypic frequencies will be also generated.

## Expected heterozygosity

As a measure of the evolution of diversity the evolution of the expected heterozygosity will be plotted and a table with the initial and final expected heterozygosities will be generated.