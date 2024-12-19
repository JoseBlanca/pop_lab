# Balancing selection

Selection usually removes diversity from the gene pool because it removes all alleles that are not being selected for.
However, in some cases a balancing selection can increase the diversity in the selected locus.

In this practice we are going to simulate two populations.
We will be able to control the fitnesses in both populations independently, so, for instance in one population we could select in favor of genotype AA and in the other in favor of aa.

There will be also, migration between both populations, so genotypes from one can go to the other.
We will have control of the immigration rate, the proportion of individuals in each generation that come from the other population.

[Balancing selection simulation application](<http:../../balancing_selection/>)

## Same selection preasure

Let's start by running a simulation with setting the same fitness in both populations.
For instance, let's select for a dominat A allele (fitness AA: 1, Aa: 1, aa: 0.5) starting with an allelic frequency of 0.01 for A in both populations.
This is a standard situation in which a beneficial allele appears in a population. For instance, one allele that confers resistance to a disease, so it is selected for.

How do you think that the A allelic frequency will evolve?
Which will be the consenquences for the diversity?
Run the simulation and explain the observed result.

## Different selection preasure

Now let's imagine that we have two populations with different selection preassures.
For instance, we can have a domesticated population in which animals or plants are selected by breeders to have some characteristics, like size or color, that are selected against in nature.
Another case would be populations of different breeds in which different phenotypes are selected for a trait in the different breeds, like the fur color in different cat or dog breeds or the fruit size in cherry and salad tomatoes.
Another possible case is an allele that defends against a predator that is present in one population, but absent in the other.

Let's imagine that a dominant allele appears in low frequency that is selected for in one of the populations and against in the other.
At the begining the A allelic frequency will be low in both populations.

### No migration

Start by thinking about a situation with no migration.
What do you think that will happen to the allele frequencies and diversities?
Run the simulation and explain the result.

### Migration

Now let's assume that 10% of the alleles of both population in each generation are due to genetic flow, migration, from one population to the other.
How that migration will alter the allelic frequencies? Will the allele selected against in each population disapear?
What would happen to the expected heterozygosity?
Run the simulations and explain the result.

How will the the final diversity depend on the migration rates?
Run simulation with different rates and explain the result.
