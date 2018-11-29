# FishScrapping

**Warning**: Under development yet

Features:

- [x] get up-to-date information from FishBase database
- [x] Terminal-based scripts

Software requierements:
* Python 3
* Git




### Length-Weight relationships

Let's suppose we have the following a list of species stored at [species.txt]():

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
python3 ./src/fishbase.py species.txt -lw -out species_lw.tsv
```
