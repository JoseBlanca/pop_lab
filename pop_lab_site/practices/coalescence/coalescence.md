# Coalescence simulations

These applications simulate a genomic region evolving through time with some mutation and recombination rates.
Unlike the case with one locus and two alleles, in these cases the simulations are not calculated forward in time, but by a [coalescence](https://en.wikipedia.org/wiki/Coalescent_theory) approach.

[msprime](https://tskit.dev/msprime/docs/stable/intro.html) is the library used to run these simulations. Once the simulation is completed the software generates a genotypic matrix with the genotype for each individual and marker.

The different parameters are calculated using the [pyNei](https://github.com/JoseBlanca/pynei) library.

## Expected heterozygosity

The expected heterozygosity, a measure of genetic diversity, is calculated using the Unbiased expected heterozygosity [Genalex](https://biology-assets.anu.edu.au/GenAlEx/Welcome.html) formula.

```{math}

    uh = {\frac{n}{(n - 1)}}  (1 - \sum p_i^2)

```

## Polymorphic markers

A variation/marker is considered polymorphic when its major allele has a frequency lower than 95%.
The simulations calculate the total number of polymorphic variants and the proportion of polymorphic variants calculated over the total number of variations.

## Allele Frequency Spectrum

The Allele Frequency Spectrum is the distribution of allelic frequencies of the major allele, the most abundant allele. So, in the chart the number of polymorphic alleles for different major allele frequencies is plotted.

## Principal Component Analysis (PCA)

The Principal Component Analysis is not calculated using all markers.
Before the calculation the non-polymorphic (95%) and the highly associated (r² > 0.1) markers are filtered out.
With the remaining markers the genotypes are coded in a array with 0 for the major allele homozygote, 2 for a homozygote of any minor allele and 1 for the heterozygotes.
Finally, this array is used to carry out the [Principal Component Analysis](https://en.wikipedia.org/wiki/Principal_component_analysis).

## Population distances

Distances between populations are calculated following the Jost's Differentiation estimation (Dest) suggested by Genalex.

```{math}

D_est = \left( \frac{k}{k - 1} \right)\left( \frac{cH_T - cH_s}{1 - cH_s} \right)

```

Observed Heterozygosity.


```{math}

H_o = \frac{Num.ofhets}{N}

```


Observed heterozygosity, averaged across populations. The average observed heterozygosity of a collection of populations.
Here, HOs is the observed heterozygosity in the s-th population; k is the number of populations.

```{math}

\bar{H_o} = \frac{\sum H_{Os}}{k}

```

Average within population heterozygosity. Identical to the mean He, being the average of the within population
expected heterozygosity across populations.

```{math}

H_s = \bar{H_E} = \sum \frac{H_{ES}}{k}

```

Corrected Hs. HS for a given locus is adjusted for small population size and inbreeding by the correction of Nei and Cheeser [30], where n̂ is the harmonic mean population size for k populations, and HO is the average
observed within-population heterozygosity for the populations.

```{math}

cH_s = \frac{\hat{n}}{\hat{n} - 1} \left[ H_s - \frac{\bar{H_o}}{2\hat{n}} \right]

```

Total expected heterozygosity calculated as if all populations were pooled (no subdivision).

```{math}

H_T = 1 - \sum_{i=1}^{h}\bar{p}_i^2

```

Corrected Ht, adjusted for small population size and inbreeding, using the correction of Nei and Cheeser. The harmonic mean of population size over the k populations is n̂.

```{math}

cH_T = H_T + \frac{cH_S}{\hat{n}k} - \frac{\bar{H_O}}{2\hat{n}k}

```
