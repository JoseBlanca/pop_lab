# Drifting populations

In this practice, we will simulate the evolution of three populations that originate from the same ancestral population but evolve independently over time due to genetic drift.
Through these simulations, we will observe how genetic drift influences population divergence and genetic distances.

You will be able to modify:

- The population size of each group.
- The number of generations they evolve after the split.

Here, we will simulate the mutations and recombinations that occur in a genomic segment.
At the end of the simulation, the genomic segment will contain variable loci that have arisen through mutation and have been reshuffled through recombination.
You could have the option of modifying other parameters like:

- The recombination rate.
- The mutation rate.
- The sequence length.
- The sample size, the number of individuals taken from the population to calculate the different paramenters.

To quantify how genetic drift influences the populations, we will analyze several population genetic metrics. These will help us understand changes in genetic diversity and population divergence over time. The metrics available include:

- The expected heterozygosity.
- The number of variable loci.
- The number and ratio of polymorphic loci.
- A Principal Component Analysis (PCA) carried out with the genotype of the sampled individuals.
- The Dest genetic distances between pairs of populations.

The PCA will provide a visual representation of genetic relationships, while the distance matrix will quantify differences between populations. Together, they allow us to track genetic divergence over time.

[Drifting populations simulation application](<https://plantgenomics.es/pop_lab/drifting_pops/>)

## Genetic distances

Imagine you have three populations that initially share the same genetic composition. As they evolve independently, how do you think genetic drift will influence their genetic distances?

Before running the simulation, take a moment to predict the outcome::

- How do you expect the genetic distances between the populations to change over time?
- Will they remain similar, or will they diverge?
- How do you think the Principal Component Analysis (PCA) and the distance matrix will reflect these changes?

Simulation & Analysis:

- Run the simulation for a given number of generations.
- Observe the genetic distances between populations at different time points.
- Examine the PCA plot: What patterns do you observe? How do populations cluster over time?
- Compare your initial predictions with the actual results.
- How does this result align with what you learned in the practice on genetic drift with one locus?

## Population size influence

Genetic drift has a stronger effect in small populations than in large ones. Let’s test this by modifying population sizes.

### Scenario 1: Large Populations

Increase the size of all three populations to 2000 individuals.

Predict what will happen:

- Will the genetic distances between populations be larger, smaller, or similar compared to smaller populations?
- Will the PCA and distance matrix show more or less divergence?

Run the simulation and analyze the results.
Compare with your predictions and explain the outcome.

### Scenario 2: Mixed Population Sizes

Set two populations to 2000 individuals and one population to 100 individuals.

Predict what will happen:

- Will the smaller population behave differently from the larger ones?
- How will its genetic distance change compared to the larger populations?
- What do you expect to see in the PCA and the distance matrix?
    
Run the simulation and analyze the results.

- Does the smaller population experience more drift than the larger ones?

## Conclusions

- Summarize your findings on how genetic drift affects genetic distances.
- Discuss the role of population size in genetic drift.
- Explain how PCA can be used to visualize genetic relationships between populations over time.
- Can this process help explain speciation or genetic differentiation between isolated human populations or breeding populations?
