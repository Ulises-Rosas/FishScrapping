# FishScrapping

Features:

- [x] get up-to-date information from FishBase database
- [x] Terminal-based scripts

Software requierements:
* Python 3

#### Installation

Upon downloading this repository, unzip it and move into the `FishScrapping` directory. Then you can run the following to install executables:
```Shell
python3 setup.py install
```

Using `git`:
```Shell
git clone https://github.com/Ulises-Rosas/FishScrapping.git
cd FishScrapping
python3 setup.py install
```

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
fishbase.py species.txt -lw
```

While output file name is based on input and on above example this file is named `species_fishbase_lw.tsv`, option `-out` can also modify default names. 

```Shell
cat species_fishbase_lw.tsv
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
### Synonyms
We can also extract species synonyms according to this database with the option `-syn`:

```Shell
fishbase.py species.txt -syn
```

Again, by default `fishbase.py` uses its input to name its output, however this can be modified with `-out` option.

```Shell
cat species_fishbase_syn.tsv
```
```
species	synonyms
Odontesthes regia	Atherina regia, Austromenidia regia, Atherina laticlavia, Austromenidia laticlava, Chirostoma affine, Basilichthys regillus, Cauque regillus, Odontesthes regillus, Basilichthys jordani, Basilichthys octavius, Odontesthes regia
Engraulis ringens	Engraulis pulchellus, Engraulis tapirulus, Anchoviella tapirulus, Stolephorus tapirulus, Engraulis ringens
Menticirrhus undulatus	Umbrina undulata, Menticirrhus undulatus
Sciaena deliciosa	Corvina deliciosa, Sciaena deliciosa
```


