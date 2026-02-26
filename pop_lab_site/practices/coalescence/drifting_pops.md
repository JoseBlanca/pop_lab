# Drifting Populations

In this practice, we will simulate the evolution of three populations that originate from the same ancestral population but evolve independently over time due to genetic drift. Through these simulations, we will observe how genetic drift influences population divergence and genetic distances.

You will be able to modify:

- The population size of each group.
- The number of generations they evolve after the split.

Here, we will simulate the mutations and recombination events that occur in a genomic segment. At the end of the simulation, the genomic segment will contain variable loci that have arisen through mutation and have been reshuffled through recombination.

You will also have the option to modify additional parameters such as:

- The recombination rate
- The mutation rate
- The sequence length
- The sample size (the number of individuals sampled from each population to calculate the different parameters)

To quantify how genetic drift influences populations, we will analyze several population genetic metrics. These will help us understand changes in genetic diversity and population divergence over time. The available metrics include:

- Expected heterozygosity
- Number of variable loci
- Number and proportion of polymorphic loci
- Principal Component Analysis (PCA) performed on the genotypes of sampled individuals
- Dest genetic distances between pairs of populations

The PCA will provide a visual representation of genetic relationships, while the distance matrix will quantify differences between populations. Together, they allow us to track genetic divergence over time.

Be aware that the PCA might fail if too few SNPs remain after filtering. Because mutations occur at random, results may vary from run to run—if this happens, simply repeat the simulation.

[Drifting populations simulation application](<https://plantgenomics.es/pop_lab/drifting_pops/>)

## Genetic distances

Imagine you have three populations that initially share the same genetic composition. As they evolve independently, how do you think genetic drift will influence their genetic distances?

Before running the simulation, take a moment to predict the outcome:

- How do you expect genetic distances between populations to change over time?
- Will they remain similar, or will they diverge?
- How do you think the PCA and distance matrix will reflect these changes?

### Simulation and Analysis

- Run the simulation for a chosen number of generations.
- Observe genetic distances between populations at different time points.
- Examine the PCA plot: What patterns do you observe? How do populations cluster over time?
- Compare your predictions with the results.
- How does this align with what you learned in the single-locus drift exercise?


## Population size influence

Genetic drift has a stronger effect in small populations than in large ones. Let’s test this by modifying population sizes.

### Scenario 1: Large Populations

Increase the size of all three populations to 2000 individuals.

Predict what will happen:

- Will genetic distances between populations be larger, smaller, or similar compared to smaller populations?
- Will the PCA and distance matrix show more or less divergence?

Run the simulation and analyze the results. Compare them with your predictions and explain the outcome.

### Scenario 2: Mixed Population Sizes

Set two populations to 2000 individuals and one population to 100 individuals.

Predict what will happen:

- Will the smaller population behave differently from the larger ones?
- How will its genetic distance change relative to the larger populations?
- What do you expect to see in the PCA and distance matrix?

Run the simulation and analyze the results.

- Does the smaller population experience stronger drift than the larger ones?

## Time Scale of Divergence

Keep population size constant at 500 for all three populations, but vary generations (e.g. 50, 200, 1000).

Questions:
- How does the genetic distances between population 1 and 2 scale with time?
- Does divergence increase linearly?

## Conclusions

- Summarize your findings on how genetic drift affects genetic distances.
- Discuss the role of population size in drift.
- Explain how PCA can be used to visualize genetic relationships between populations over time.
- Can this process help explain speciation or genetic differentiation among isolated human or breeding populations?
