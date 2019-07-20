#!/usr/bin/env python3

# -*- coding: utf-8 -*- #

import re
import urllib.request
import argparse


def getOpt():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=''' 

                    Fish-Scraping: Short module for getting insigths from FishBase database 
                    =======================================================================
                    ><{{{*> . ><(((*> . ><{{{*> . ><(((*> . ><{{{*> . ><(((*> . ><{{{*> . >

                                       * Written by U. Rosas



                                    ''', epilog="* Warning: Scripts here run as fast as FishBase server allow us")

    parser.add_argument('spps',
                        metavar='spps_file',
                        default=None,
                        help='Target species in plain text')
    parser.add_argument('-lw',
                        action='store_true',
                        help='Get Length-Weight relationships'
                        )
    parser.add_argument('-syn',
                        action='store_true',
                        help='Get species synonyms'
                        )
    parser.add_argument('-out', metavar="str",
                        action='store',
                        default='input_based',
                        help='Output name [Default = <input_based>.tsv]'
                        )
    args = parser.parse_args()

    return args


class Fishbase:
    """
    Current functions of fishbase class:

    * Assess the spelling of entries with `validate_name()` function
    * Get fishbase id from validated names with `_get_ids()` function
    * Get synonyms from validated names with `get_synonyms()` function
    * Get length-weight relationships with `lw_relationship()` function
    """
    def __init__(self, species):
        """It is just a single entry.
        Here is where the species name should enter
        as initial value.
        """
        try:
            self.species = re.findall("^[A-Za-z]+ [a-z]+", species)[0]
        except IndexError:
            self.species = re.findall("^[A-Za-z]+", species)[0]  # just choose genera word
        self.species_binary = str.split(self.species, sep=" ")
        self.choices = []
        self.tmp_selected_choice = []
        self.ids = []
        self.synonyms = []


        ## useful urls:
        self.summary_url = "https://www.fishbase.in/summary/"
        self.no_record_url = "https://www.fishbase.in/Nomenclature/ScientificNameSearchList.php?Genus="
        self.api_url = "https://fishbase.ropensci.org/"
        self.synonym_url = "http://www.fishbase.in/Nomenclature/SynonymsList.php?ID="
        self.lw_relationship_url = "https://www.fishbase.in/popdyn/LWRelationshipList.php?ID="


        ## messages
        self.empty_html_body = "Species name is not in the public version of FishBase"
        self.check_string = "Please check possible typos at genus name!"
        self.genus_only = "Species names are stored at choices attr."
        self.consider_review = "Please check your spelling first"
        self.too_many_connections = "Too many connections"

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
        """The initial value is faced against to the Fishbase repository
        to validate whether it really exists
        complete_url = 'https://www.fishbase.de/summary/Sarda-chilnss.html'
        """
        # self = Fishbase("Odontesthes regia")._get_id()

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

    def lw_relationship(self):
        """lw relationship let us to find out parameters of growth already estimated and uploaded at
        FishBase. Since FishBase can easily reach too many connection per day, it is possible that in
        an attempt you have a results of ServerError, which means server oversaturated, and in another
        real result
        """
        wid = self._get_id()

        while wid == '':
            wid = self._get_id()

        if wid == self.consider_review:
            return "{0}{1}".format(self.species, "\tcheck_spell" * 5)

        else:
            complete_url2 = self.lw_relationship_url + wid

            page2 = ""
            tough_connection = re.findall(self.too_many_connections, page2)

            while page2 == "" or len(tough_connection) == 1:
                try:
                    page2 = urllib.request.urlopen(complete_url2).read().decode('utf-8').replace("\n", "")
                    tough_connection = re.findall(self.too_many_connections, page2)

                except urllib.error.HTTPError:
                    pass

            # a
            a = [re.sub(">([0-9.]+)</A>", "\\1", i) for i in re.findall(">[0-9.]+</A>", page2)]


            # flow control if there is any length-weight metric on that species:
            if len(a) == 0:

                return "{0}{1}".format(self.species, "\tNA" * 5)

            else:
                # b
                b_pattern = "<td align='right' width=''>[\r\t]+"

                pre_b = re.findall(b_pattern + "[0-9.]{0,}\\r", page2)

                b = [re.sub("^$", "NA",
                            re.sub(".*\\t([0-9.]{0,})\\r", "\\1", i)) for i in pre_b
                     ]


                # length
                length_pattern = "<td align='center' width=''>[\r\t]+"

                pre_length = re.findall(length_pattern + "[0-9.]+&nbsp;[ 0-9\-.]+" + "|" + length_pattern + "&nbsp;&nbsp;&nbsp;" , page2)


                length = [re.sub("^,&nbsp;&nbsp;$", "NA",
                                 re.sub(".*\\t([0-9.]{0,})&nbsp;([ 0-9\-.]{0,})", "\\1,\\2", i).replace("-", "")) for i in pre_length
                          ]

                ## country
                ctry_pattern = "<td width='10.5%'>[\r\t]+"
                #"[A-Z][A-Za-z\-() ]{0,}"

                pre_country = re.findall(ctry_pattern + "[A-Z]{0,1}[A-Za-z\-() ]{0,}" , page2)

                country = [
                    re.sub('^$', "NA",
                           re.sub(".*\\t([A-Z]{0,1}[A-Za-z\-() ]{0,})", "\\1", i)) for i in pre_country
                ]

                ## sample size
                n_pattern = "<td align='right' width=''>[\r\t]+"
                pre_n = re.findall(n_pattern + "[0-9]{0,}&nbsp", page2)

                n = [
                    re.sub('^$', "NA",
                           re.sub(".*\\t([0-9]{0,})&nbsp", "\\1", i)) for i in pre_n
                ]

                g = ""
                for i in range(len(a)-1):
                    g+="{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(self.species, a[i], b[i], n[i], country[i], length[i])
                g+="{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(self.species, a[-1], b[-1], n[-1], country[-1], length[-1])
                return g


def cname(s, ty):
    """
    :param s: check line 138 of `plot_bars.R`
    :return:
    """
    tail = "_fishbase_%s.tsv" % ty
    try:
        return s.split(".")[-2].split("/")[-1] + tail
    except IndexError:
        return s.split("/")[-1] + tail


def main():
    options = vars(getOpt())
    # print(options)

    file        = open( options['spps'], 'r' ).read().split("\n")
    all_species = [i.replace('\n', '') for i in filter(None, file)]


    if options['lw']:

        fo = options['out'] + '_lw.tsv' if options['out'] != 'input_based' else cname(options['spps'], 'lw')
        # print("\nWriting results into: " + fo + "\n")

        f = open(fo, "w")
        line = 1

        print("\nScrapping data of:\n")
        for i in all_species:

            if line == 1:
                f.write("species\ta\tb\tn\tCountry\tRangeLength" + "\n")
                line += 1

            print("%30s" % i)

            string = Fishbase(i).lw_relationship()

            f.write(string + "\n" )
        f.close()

    if options['syn']:

        fo = options['out'] + '_syn.tsv' if options['out'] != 'input_based' else cname(options['spps'], 'syn')

        f = open(fo, "w")
        line = 1

        print("\nScrapping data of:\n")

        for i in all_species:

            if line == 1:
                f.write("species\tsynonyms" + "\n")
                line += 1

            print("%30s" % i)
            string = Fishbase(i).get_synonyms()

            if not string:
                string = ["NA"]

            stringCol = ', '.join(string)

            f.write("%s\t%s" % (i, stringCol) + "\n" )

        f.close()

if __name__ == '__main__':
    main()