import re
import urllib
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Short module for getting insights about DNA barcode given a list of species')

parser.add_argument('fastq', metavar='SpeciesList',
                    # nargs = "+",
                    type=argparse.FileType('r'),
                    help='Target species in text format.')

args = parser.parse_args()

all_species = [i.replace('\n', '') for i in args.fastq]

class fishbase:
    """Validate names against to the fishbase database
    """
    def __init__(self, species):
        """It is just a single entry.
        Here is where the species name should enter
        as initial value.
        """
        try:
            self.species = re.findall("^[A-Za-z]+ [a-z]+", species)[0]
        except IndexError:
            self.species = re.findall("^[A-Za-z]+", species)[0]  # just choose genus word
        self.species_binary = str.split(self.species, sep=" ")
        self.choices = []
        self.tmp_selected_choice = []
        self.ids = []
        self.synonyms = []

        ##useful urls:
        self.summary_url = "https://www.fishbase.de/summary/"
        self.no_record_url = "https://www.fishbase.de/Nomenclature/ScientificNameSearchList.php?Genus="
        self.api_url = "https://fishbase.ropensci.org/"
        self.synonym_url = "http://www.fishbase.se/Nomenclature/SynonymsList.php?ID="

        ##messages
        self.empty_html_body = "Species name is not in the public version of FishBase"
        self.check_string = "Please check possible typos at genus name!"
        self.genus_only = "Species names are stored at choices attr."
        self.consider_review = "Please check your spelling first"

    def validate_name(self):
        """BOLD system require accurate species name for getting metadata and sequences and most of time
        species lists contain a wide variety of typos. Hence, a function like this is needed for validating
        species name.This function will find species name between names retrieved from FishBase ant then will return
        them. In order to get it faster, this function doesn't take hints or suggestion of name if there were
        not matches between files of FishBase and just uses all species from a given genus
        (i.e. first word of the input) instead. On this prior, get_names function takes a species name based on
        number of matches between of consonants between tips by default.
        """
        complete_url = self.summary_url + self.species.replace(' ', '-') + '.html'

        try:
            page = urllib.request.urlopen(complete_url).read().decode('utf-8')

        except urllib.error.HTTPError:
            page = self.empty_html_body

        if page.find(self.empty_html_body) != -1:

            no_record = self.no_record_url + self.species_binary[0]
            page = urllib.request.urlopen(no_record).read().decode('utf-8')

            searching_paragraph = "Please wait. Searching..."

            if page.find(searching_paragraph) != -1:

                self.tmp_selected_choice.append(self.check_string)

                return self.check_string

            else:
                vowels = ["a", "e", "i", "o", "u", "y"]
                pattern = "<i>[A-Za-z]+ [a-z]+</i></td>"

                choices = [re.findall("[A-Za-z]+ [a-z]+", i)[0] for i in list(set(re.findall(pattern, page)))]

                """All species of the genus are stored in an initial variable.
                So, it can be easily callable as an attribute.
                """
                self.choices.extend(choices)

                if len(self.species_binary) == 2:

                    pattern2 = "[" + \
                               "|".join(set(list(self.species_binary[1])) - set(vowels)) + \
                               "]"

                    lengths = []

                    for string in choices:
                        lengths.append(
                            len(
                                re.findall(pattern2,
                                           str.split(string, sep=" ")[1]))
                        )

                    selected = choices[lengths.index(max(lengths))]
                    self.tmp_selected_choice.append(selected)

                    return selected

                else:
                    self.tmp_selected_choice.append(self.genus_only)

                    return self.genus_only

        else:

            genus_name = list(set(re.findall("&GenusName=[A-Za-z]+", page)))[0].replace("&GenusName=", "")
            species_name = list(set(re.findall("&SpeciesName=[A-Za-z]+", page)))[0].replace("&SpeciesName=", "")

            one_entry_string = genus_name + " " + species_name

            self.tmp_selected_choice.append(one_entry_string)

            return one_entry_string

    def validate_name_html(self):
        """The initial value is confronted to the Fishbase repository
        to validate whether it really exists
        complete_url = 'https://www.fishbase.de/summary/Sarda-chilnss.html'
        """
        complete_url = self.summary_url + self.species.replace(' ', '-') + '.html'
        page = urllib.request.urlopen(complete_url).read().decode('utf-8')

        f = open(self.species + '.html', 'w')
        f.write(page)
        f.close()

    def _get_id(self):
        """The initial value is confronted to the Fishbase repository
        to validate whether it really exists
        complete_url = 'https://www.fishbase.de/summary/Sarda-chilnss.html'
        """
        if len(self.tmp_selected_choice) == 0:

            complete_url = self.summary_url + self.species.replace(" ", "-") + ".html"

            try:
                page = urllib.request.urlopen(complete_url).read().decode('utf-8')

            except urllib.error.HTTPError:
                self.ids.append(self.consider_review)

                return self.consider_review

            if page.find(self.empty_html_body) != -1:
                self.ids.append(self.consider_review)

                return self.consider_review

            else:

                IDs = [i.replace('SynonymsList.php?ID=', '') for i in re.findall("SynonymsList\.php\?ID=[0-9]+", page)]

                if len(set(IDs)) == 1:
                    self.ids.append(IDs[0])

                    return IDs[0]

                else:
                    self.ids.extend(list(set(IDs)))
                    IDs_formated = ", ".join(set(IDs))

                return IDs_formated

        else:

            if (self.tmp_selected_choice[0] == self.genus_only or
                    self.tmp_selected_choice[0] == self.check_string):
                self.ids.append(self.consider_review)

                return self.consider_review

            else:

                complete_url = self.summary_url + self.tmp_selected_choice[0].replace(" ", "-") + ".html"
                page = urllib.request.urlopen(complete_url).read().decode('utf-8')
                IDs = [i.replace('SynonymsList.php?ID=', '') for i in re.findall("SynonymsList\.php\?ID=[0-9]+", page)][0]

                self.ids = [IDs]

                return IDs

    def get_synonyms(self):
        """get_synonym function retrieves species names from the fishbase web portal
        by using simple web scrapping methods and a species' ID. The prior, is
        retrieved from another function
        """

        if len(self.ids) == 0:
            self._get_id()

        if self.ids[0] == self.consider_review:
            self.synonyms.append(self.consider_review)

            return self.consider_review
        else:
            complete_url = self.synonym_url + self.ids[0]

            page = urllib.request.urlopen(complete_url).read().decode('utf-8')

            synonyms = []

            for syn in re.findall("<a href='.*Status=synonym.*'>[A-Z][a-z]+ [a-z]+</a>", page):
                synonyms.append(
                    re.findall(">[A-Z][a-z]+ [a-z]+", syn)[0].replace(">", "")
                )

            for accep in re.findall("<a href='.*Status=accepted\sname.*'>[A-Z][a-z]+ [a-z]+</a>", page):
                synonyms.append(
                    re.findall(">[A-Z][a-z]+ [a-z]+", accep)[0].replace(">", "")
                )

            self.synonyms = synonyms

            return self.synonyms


valid_names = []

all_ids = []

for spps in all_species:

    fish_tmp = fishbase(spps)
    ID = fish_tmp.validate_name()

    all_ids.append(ID)

    if len(re.findall("Species ID", ID)) == 1:
        valid_names.append(spps)


table0 = pd.concat([
    pd.Series(all_species, name='Species'),
    pd.Series(all_ids, name='Species IDs')],
    axis=1)

table0.to_csv("Names_and_IDs.txt", header=True, index=False, sep= "\t") ##possible bug from the sep argument

print(f"\n {table0} \n\nNames with their corresponding were stored at Names_and_IDs.txt")



class bold:

    def __init__(self, all_species):
        '''It gets just a list of entries.
        Here is where the species names should enter
        as initial value. These values are taken from arg.parser objects
        '''
        self.names = all_species

        self.speciesName = []
        self.Nseqs = []

    def get_Meta_and_Seqs(self):


        file = open('sequences.fasta', 'w')

        def export_lines(byte_list):
            for i in byte_list:
                file.write(i.decode('utf-8'))

        for query in self.names:

            base_url = 'http://www.boldsystems.org/index.php/API_Public/sequence?taxon='

            if len(re.findall('\s', query)) == 1:
                self.speciesName.append(query)

                complete_url = base_url + query.replace(' ', '%20')
                seqs_object = urllib.request.urlopen(complete_url)

                print( "Accessing to: {}".format(complete_url) )

                seqs = seqs_object.readlines()

                export_lines(seqs)

                self.Nseqs.append(
                    sum( [ len(re.findall('>', i.decode('utf-8'))) for i in seqs ] )
                    )

        file.close()

        table = pd.concat([
            pd.Series(self.speciesName, name='Species'),
            pd.Series(self.Nseqs, name='Number of sequences')],
            axis=1)

        table.to_csv("table.csv", header=True, index=False)

        print(f"\n {table} \n\nMetadata and sequences were stored in table.csv and sequences.fasta respectively")


bold_tmp = bold(all_species)

bold_tmp.get_Meta_and_Seqs()
