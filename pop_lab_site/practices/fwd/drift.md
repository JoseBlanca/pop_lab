# Drift

## Introduction

In this practice, we will simulate the evolution of a locus with two alleles (A and a).
You will be able to modify:

- the initial allelic frequency of A (and will will assume that the starting genotypic frequencies follow Hardy-Weinberg),
- the number of generations, and
- the population size.

You will also be able to run one or multiple simulations simultaneously.

In these simulations, there will be no mutation or selection, just a population of a given size evolving generation after generation through random mating.

Before running the simulations, think about how each parameter might influence the outcome. 

[Drift simulation application](<https://bioinf.comav.upv.es/pop_lab/simple_drift/>)

## Learning objectives

- Understand the role of genetic drift in allele frequency changes.
- Explore how population size influences drift effects.
- Think about how genetic diversity is influenced by genetic drift.

## Randomness

What do you think will happen if a population with an initial A allelic frequency of 0.5 and 100 individuals evolves over 100 generations?

Do you expect all simulations to follow the same trajectory? Why or why not? Run multiple simulations and compare the results.

## Fixation

Fixation occurs when one allele reaches a frequency of 1 in the population, meaning the other allele is lost.

Evolve a population of 100 individuals over 100 generations.
Run the simulation 20 times and count how many times an allele becomes fixed.

What happens if, instead of 100 generations, the population evolves for 300 generations?
What do you think would eventually happen if we ran the simulation for thousands of generations?

When fixation occurs, is one allele more likely to be fixed than another?
Compare the number of times A vs. a is fixed when the initial frequency of A is 0.5 versus when it is 0.9. How does the starting frequency affect the probability of fixation?

What will usually happen to alleles at very low frequencies in the population?
Could an allele with a low initial frequency increase its frequency over time?

Imagine that you have a population of an endangered species.
There is one locus, responsible for a color variation, with an allele frequency for the minor allele of 0.1.
Due to a degradation of its environment its population size is reduced to 200 individuals, after 50 generations, which would be the chances of having preserved that phenotypic variation?

## Population Size Influence

How does the number of individuals affect the differences between evolutionary outcomes?
Do the differences between trials increase or decrease when we increase or decrease the population size?
How does population size influence the likelihood of fixation?

Compare the number of times an allele becomes fixed across populations of 50, 100, and 200 individuals for 100 generations. Does the rate of fixation change? Why?

What would happen if we assume a very big population or , as in Hardy-Weinberg equilibrium, that the population is infinite?

## Drift and Diversity

Expected heterozygosity (He) is a measure of genetic variation in a population. It is defined as the heterozygosity that we would expect in a population in which the genotypic frequencies follow Hardy-Weinberg. So, in a population with two alleles with frequencies p and q the expected heterozygosity would be H = 2pq or H = 1 - p² - q*².

Now that you have explored the allelic frequency behavior, could you predict how expected heterozygosity changes over time?

Starting with an A allele frequency of 0.5, is it possible for expected heterozygosity to increase over time? Why or why not?"

Could there be a case in that genetic drift could increase diversity for a particular locus?
Run simulations starting with an A allele frequency of 0.1 in a population of 200 individuals over 50 generations. How often does expected heterozygosity increase? Decrease?
What would happen if we decrease the number of individuals to 100 and increase the number of generations to 300?

If we continue the simulation for thousands of generations, what do you predict will happen to genetic diversity? Why?
If we started with an A allelic frequency of 1, could drift alone generate diversity?
