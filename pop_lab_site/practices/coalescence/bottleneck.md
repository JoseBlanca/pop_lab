# Bottlenecks and Genetic Diversity

A population bottleneck is a sharp reduction in population size over a period of time.  
This can be caused by environmental factors such as droughts, viral diseases, or human-induced events like habitat destruction. During a bottleneck, only a fraction of the original population survives, which can have significant effects on genetic diversity.

In this practice, we will analyze how a population evolves over time after experiencing a bottleneck.

You will be able to modify:

- The population size before, during, and after the bottleneck
- The duration of the bottleneck
- The time elapsed after the bottleneck

Here, we will simulate the mutations and recombination events that occur in a genomic segment. At the end of the simulation, the genomic segment will contain variable loci that have arisen through mutation and have been reshuffled through recombination.

You will also have the option to modify additional parameters such as:

- The recombination rate.
- The mutation rate.
- The sequence length.
- The sample size (the number of individuals sampled from the population to calculate parameters).

Be aware that crosses, mutations and recombinations will happen at random, so run each simulation several times to notice the general trend and not just a particularly weird random outcome.

After running the simulation, you will have access to several genetic diversity metrics:

- Expected heterozygosity (a measure of genetic variation)
- Number of variant loci
- Number and proportion of polymorphic loci
- Allele Frequency Spectrum (AFS), which describes the distribution of allele frequencies.

[Bottleneck simulation application](<https://plantgenomics.es/pop_lab/bottleneck/>)

## Bottlenecks and diversity

Imagine that we have run two simulations. In both of them the initial and final number of individuals is 50,000, but in one a bottleckneck has occurred.
At the beginning, in the past, in both of them the expected heterozigosity was 0.25, and at the end, in the present day the expected heteorigosity is 0.06 for the first one and 0.25 for the second one. Which of the populations has gone through a bottleneck and why.

## Bottlenecks and diversity simulation

Imagine a population goes through a bottleneck. How do you think this event will affect its genetic diversity?

Before running the simulation, predict what will happen to:

- Expected heterozygosity
- Number of genetic variants
- Number and proportion of polymorphic loci
- Whether the population will recover its initial genetic diversity after the bottleneck ends, and why

Run the simulation and examine the results before, during, and after the bottleneck. Compare your expectations with the observed changes in:

- Expected heterozygosity
- Number of genetic variants
- Number and proportion of polymorphic loci (95% threshold)

Remember that you can obtain these values for each time period from the plots and tables.

How does the bottleneck affect the Allele Frequency Spectrum? Compare the oldest sample of the population with the most recent one (generation 0).

Are all variations lost at the same rate? Compare hihgly variable ones with the ones with a very low minor allele frequency.

Can you explain the effect of the bottleneck on the proportion of polymorphic (95%) loci?

## Effect of the bottleneck strength

Not all bottlenecks have the same severity. Let’s explore how different bottleneck conditions affect genetic diversity.

Vary the number of individuals that survive the bottleneck.

How does bottleneck severity (number of surviving individuals) affect:

- Expected heterozygosity?
- Number of variants?
- Proportion of polymorphic loci?

Is there a minimum number of survivors for which the bottleneck effect becomes negligible?

Vary the duration of the bottleneck.

- How does increasing bottleneck duration influence diversity loss?
- Would an extremely severe bottleneck, even if short, still be problematic?

## Real-World consequences: Conservation and Breeding

Bottlenecks are not just theoretical; they have real-world implications for population management.

### Endangered Species Recovery

Imagine an endangered species that has gone through a severe bottleneck but later recovers in population size.

- Will its genetic diversity fully recover over time?
- What risks does low genetic diversity pose for long-term survival (e.g., inbreeding, disease susceptibility)?

### Breeding Populations

Some domesticated populations—for example, cultivated tomato or the “piel de sapo” melon variety—originate from only a few individuals. How might this affect their genetic diversity and long-term adaptability?

## Effect of the population size and time after the bottleneck

After a bottleneck, a population can recover in size—but does this also restore its genetic diversity?  
Do expected heterozygosity, number of variants, and proportion of polymorphic loci return to their initial values after the bottleneck? Why or why not?

### Scenario 1: Increasing Population Size After the Bottleneck

- Increase the population size after the bottleneck and observe the effect.
- Does a larger post-bottleneck population help restore genetic diversity? Why or why not?
- Which evolutionary force would drive this recovery over time?

### Scenario 2: Time Elapsed Since the Bottleneck

- Run simulations with different numbers of generations after the bottleneck.
- Does increasing the time since the bottleneck help recover lost diversity?
- Which genetic parameters recover, and which remain altered?

### How can we restore genetic diversity?

Imagine you are trying to increase the diversity of a population that has experienced a bottleneck, such as a wild population after a drought or a cultivated plant variety that has lost most of its genetic variation.

Could you propose an intervention to restore diversity?

- Could controlled breeding programs help?
- Would introducing individuals from other populations be beneficial?
- What role does mutation play in restoring diversity?

## Conclusions

Summarize your findings:

- How does a bottleneck affect genetic diversity?
- Can diversity recover after a bottleneck, and under what conditions?

Discuss key evolutionary forces:

- What role does genetic drift play during and after a bottleneck?
- How do mutation and natural selection contribute to long-term recovery?

Apply your knowledge to real-world cases:

- What lessons can we draw for conservation biology and breeding programs?
- How can we mitigate the negative effects of bottlenecks in endangered, managed, or breeding populations?