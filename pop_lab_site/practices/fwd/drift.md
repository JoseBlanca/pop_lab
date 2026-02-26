# Drift

## Introduction

In this practice, we will simulate the evolution of a locus with two alleles (A and a).
You will be able to modify:

- the initial allele frequency of A (we will assume that the starting genotypic frequencies follow Hardy–Weinberg equilibrium),
- the number of generations, and
- the population size.

You will also be able to run one or multiple simulations simultaneously.
Take into account that the outcome might vary from one simulation to the next randomly, so run the simulations several times to observe the general trend.

In these simulations, there will be no mutation or selection—just a population of a given size evolving generation after generation through random mating.

Before running the simulations, think about how each parameter might influence the outcome.

[Drift simulation application](<https://plantgenomics.es/pop_lab/simple_drift/>)

## Learning objectives

- Understand the role of genetic drift in allele frequency changes.
- Explore how population size influences drift effects.
- Understand how genetic diversity is influenced by genetic drift.

## Randomness

What do you think will happen if a population with an initial allele frequency of A equal to 0.5 and 100 individuals evolves over 100 generations?

Do you expect all simulations to follow the same trajectory? Why or why not?

Run 20 simulations and compare the final allele frequency of A and the expected heterozygosity.
Calculate also the average allele frequency over all the simulations.

## Fixation

Fixation occurs when one allele reaches a frequency of 1 in the population, meaning the other allele is lost.

Evolve a population of 100 individuals over 100 generations.
Run the simulation 20 times and count how many times each allele becomes fixed.
Plot an histogram with the number of times that A or a become fixed and the number of times in which there is no fixation.
Calculate the frequency of simulations that reach fixation.

What happens if, instead of 100 generations, the population evolves for 300 generations?
What do you think would eventually happen if we ran the simulation for thousands of generations?

When fixation occurs, is one allele more likely to become fixed than the other?
In a simulation with for 100 individuals and 300 generations, compare the number of times A vs. a becomes fixed when the initial frequency of A is 0.5, and also for the initial frequencies of 0.1 and 0.9.
Plot an histrogram with the number of times that each allele gets fixated for all three initial allele frequencies.
Calculate the fixation probability of A for both initial frequencies.
How does the starting frequency affect fixation probability?

What will usually happen to alleles at very low frequencies in the population?
Could an allele with a low initial frequency increase over time?

Imagine that you have a population of an endangered species. There is one locus responsible for a color variation, with a minor allele frequency of 0.1. Due to environmental degradation, the population size is reduced to 200 individuals. After 50 generations, what would be the probability of preserving that phenotypic variation?

## Population Size Influence

How does the number of individuals affect differences between evolutionary outcomes?
Compare the number of times an allele becomes fixed across populations of 50, 100, and 200 individuals over 100 generations.
How does population size influence the likelihood of fixation?

Does the variation in allele frequencies from one population to the next increase or decrease when we increase or decrease population size?

What would happen if we assumed a very large population—or, as in Hardy–Weinberg equilibrium, an infinite population?
Make the population infinite, run the simulation and check the result.

## Drift and Diversity

Expected heterozygosity (He) is a measure of genetic variation in a population. It is defined as the heterozygosity expected if genotype frequencies follow Hardy–Weinberg proportions. In a population with two alleles of frequencies p and q, the expected heterozygosity is:

H = 2pq = 1 - p² - q²

Now that you have explored allele frequency dynamics, can you predict how expected heterozygosity changes over time?

Starting with an A allele frequency of 0.5, is it possible for expected heterozygosity to increase over time? Why or why not?

Could there be a case in which genetic drift increases diversity at a particular locus?

Run simulations starting with an A allele frequency of 0.1 in a population of 200 individuals over 50 generations. How often does expected heterozygosity increase? How often does it decrease?

What happens if we decrease the population size to 100 and increase the number of generations to 300?

If we continue the simulation for thousands of generations, what do you predict will happen to genetic diversity? Why?

If we start with an allele frequency of A equal to 1, can drift alone generate diversity?
