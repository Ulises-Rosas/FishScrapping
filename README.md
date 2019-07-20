# FishScrapping

**Warning**: Under development yet

Features:

- [x] get up-to-date information from FishBase database
- [x] Terminal-based scripts

Software requierements:
* Python 3


### Length-Weight relationships

Let's suppose we have the following a list of species stored at [species.txt](https://github.com/Ulises-Rosas/FishScrapping/blob/master/species.txt):

```Shell
cat species.txt
```
```
Odontesthes regia
Engraulis ringens
Menticirrhus undulatus
Sciaena deliciosa
```
We can obtain their LWRs by using:

```Shell
./src/fishbase.py species.txt -lw
```

While output file name is based on input and on above example this file is named `species_fishbase.tsv`, option `-out` can also modify default names. 

```Shell
cat species_fishbase.tsv
```
```
species	a	b	n	Country	RangeLength
Odontesthes regia	NA	NA	NA	NA	NA
Engraulis ringens	0.02150	2.604	NA	Peru	NA
Engraulis ringens	0.00674	3.000	NA	Peru	NA
Engraulis ringens	0.00460	3.121	NA	Chile	NA
Engraulis ringens	0.00421	3.144	NA	Chile	NA
Engraulis ringens	0.00375	3.221	NA	Chile	NA
Menticirrhus undulatus	0.01027	3.000	1	NA	61.0, 61.0
Sciaena deliciosa	NA	NA	NA	NA	NA
```

