# Selection

## Introduction

In this practice we are going to simulate one locus with two alleles (A and a).
You will be able to set either the initial allelic frequencies (assuming Hardy-Weinberg) or each genotypic frequency independently.
Besides the population size and the number of generations you can also change the fitness for each genotype as well the mutation rates from allele A to allele a and vice-versa.

[Selection simulation application](<https://bioinf.comav.upv.es/pop_lab/simple_selection/>)

## Selection in favour of a minor allele

Let's suppose that at the beginning the genotypes for all individuals are aa, but that we have a mutation rate of 0.005 from allele a to allele A. That means that in each generation some a alleles will mutate to A, so some aa genotypes will be in fact Aa.
Let's start by assuming that the AA homozygote has a fitness of 1, the aa genotype of 0.8 and that the mutation is recessive, so Aa has a fitness of 0.8.

What do you think that will happen the the A allelic frequency in this situation?
Run the simulation and find out which is the result.
You might try to remove the genetic drift to only take into account the effect of the selection.

Take a look at the genotypic frequencies and explain what happens with them, especially with the ones for the heterozygote. 

### What is the influence of the selection strength  

How would you increase or decrease the strength of the selection?
Think about what would happen if you increase or decrease the aa and Aa genotypes fitnesses to make them more or less similar to the AA fitness, that should always be 1.
Run the simulation and find out what happens.
Which is the relation between the selection strength and the number of generations require to reach an equilibrium?

### Recessive and dominant alleles

So far we have been considering that the beneficial allele (A) was recessive, so aa and Aa had the same fitness.
What do you think that would change if A would be dominant, so AA and Aa had the same fitness: 1.
Run the simulation and compare the two scenarios.

## Selection and drift

Do you think that drift would affect in any way the selection process.

### Drift and beneficial alleles

Let's imagine that we have a beneficial allele A that appears by mutation in a population that at the start of the simulation has only aa individuals.
Set the number of individuals at 100 and the mutation rate from a to A at 0.001.
The mutation should be recessive, so Aa and aa should have the same fitness, let's say a fitness of 0.8.

Compare the result of the simulation when the population size is 100 and the case of no-drift (so infinite size).

### Drift and deletereous alleles

Now the AA genotype is lethal, so it's fitness is 0, but recessive, so Aa and aa have a fitness of 1. Let's set it's initial frequency to 0.01 and remove the mutation. What do you think that will happen to the allele?
Run the simulation with a population of 100 individuals and an infinite one and explain the result.
Does the deleterous allele dissapears when there is no drift?

What would happen if if add a minimal mutation rate of 0.001 from a to the deletereous allele A? 

Set different fitnesses for AA and check what happens.

Compare the result with a dominant lethal allele, so now both AA and Aa are lethal.

## Disruptive evolution

In some cases both homozygotes are OK, but the heterozygote is not viable.
This could happen, for instance, in the case in which a large chromosomal inversion has happened. Both homozygotes can reproduce without any problem between them, but the heterozygote cannot reproduce, so it has a fitness of zero.

What do you think would happen in this case?
Run the simulation several times starting with the following starting genotypic frequencies (AA: 0.5, Aa: 0, aa: 0.5) and explain the result.

Would the result change if we would start with the following genotypic frequencies: AA: 0.01, Aa: 0.98, aa: 0.01?

## Heterozygote advantage

In some very rare cases, the heterozygote could had a higher fitness than both homozygotes.
That is the case, for instance, of the [sickle cell anemia](https://en.wikipedia.org/wiki/Sickle_cell_disease). In this case one genotype (AA) is susceptible to malaria, so let's set its fitness to 0.6, while the other homozygote (aa) has a serious condition (assume a fitness of 0.3) while the heterozygote has an advantage because it has no sickle cell anemia and is somewhat resistant to malaria.
This is an example of balancing selection.

What do you think will be the outcome in this case? Would one allele became fixed?
