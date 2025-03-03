# Founder Effect and Genetic Diversity

The founder effect occurs when a new population is established by a small number of individuals from a larger original population. This results in a genetic bottleneck, reducing diversity and increasing genetic divergence from the source population.

This phenomenon is commonly observed in:

- Colonization of new habitats, such as islands or remote areas.
- Small, isolated populations, such as those resulting from habitat fragmentation or species introductions.
- The formation of new breeds or cultivated varieties.

In this practice, we will analyze how the founder effect influences genetic diversity and differentiation over time.

You will be able to modify:

- The original population size.
- The number of founder individuals.
- The final size of the new population.
- The duration of the bottleneck period (before population growth).
- The time at which the new population was created.

Here, we will simulate the mutations and recombinations that occur in a genomic segment.
At the end of the simulation, the genomic segment will contain variable loci that have arisen through mutation and have been reshuffled through recombination.
You could have the option of modifying other parameters like:

- The recombination rate.
- The mutation rate.
- The sequence length.
- The sample size, the number of individuals taken from the population to calculate the different parameters.

After running the simulation, you will have access to several genetic diversity metrics:

- Expected heterozygosity (a measure of genetic variation).
- Total number of variable loci.
- Number and proportion of polymorphic markers.
- Allele Frequency Spectrum.
- Principal Component Analysis (PCA).
- Genetic distance matrix (quantifying differentiation between populations).

[Founder effect simulation application](<https://bioinf.comav.upv.es/pop_lab/founder/>)

## Effect on diversity

When a small group of individuals establishes a new population, they typically carry only a fraction of the genetic variation present in the original population.

### Predictions

Before running the simulation, think about the following:

- How will the expected heterozygosity of the new population compare to the original one?
- Will the total number of genetic markers change?
- How many polymorphic markers will remain?
- If the new population grows in size, will these diversity parameters recover over time?

### Simulation & Analysis

Run the simulation and compare the genetic diversity of the founder population with the original population.

- Observe how expected heterozygosity, number of markers, and polymorphism levels change.
- Let the new population grow after the bottleneck and observe whether genetic diversity recovers.

Compare your expectations with the observed results.

## Genetic distances

Even though the founder population originates from the original population, the process of founding itself creates genetic divergence.

### Predictions

- When will the bulk of the genetic distance between populations emerge—immediately after founding or later?
- Once the populations are differentiated, do you expect them to become genetically similar again over time if no further migration occurs?
- How will increasing the founder population size influence genetic distance?

### Simulation & Analysis

Run the simulation and check the genetic distance matrix between the original and founder populations.

- Compare distances immediately after founding versus after the population has grown.
- Do the genetic distances stabilize over time, or do they continue increasing?

## Bottleneck strength

Not all founder events are equal, some populations start with more individuals or experience a longer bottleneck period before growing.

### Predictions

- How do you think the number of founder individuals affects diversity loss and genetic distances?
- If the population stays small for a longer period before expanding, how will that influence its genetic composition?

### Simulation & Analysis

Run simulations with different numbers of founder individuals and different bottleneck durations.

Compare the effects on:

- Expected heterozygosity
- Number of polymorphic markers
- Genetic distances

Identify whether there is a minimum number of founders that makes the genetic impact of the bottleneck negligible.

## Real-World Implications: Conservation and Breeding

The founder effect has significant consequences for both conservation biology and artificial selection.
Reflect on how these results relate to real-world examples, such as island colonization or the creation of isolated human communities.

Could introducing individuals from other populations help mitigate the effect of the genetic drift?

Many breeds of domesticated plants and animals originate from a small number of individuals.
How might this impact their genetic diversity?
Can selective breeding increase diversity, or does it further reduce variation?