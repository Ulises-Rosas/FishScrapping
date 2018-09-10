#!/usr/bin/python3

import re
import urllib.request


class Worms:
    def __init__(self, taxon):

        self.taxon = taxon.replace(" ", "%20")
        self.taxonomic_ranges = []
        self.classification_page = ""

        aphiaID_url = "http://www.marinespecies.org/rest/AphiaIDByName/" + \
                      self.taxon + \
                      "?marine_only=true"

        self.aphiaID = None
        # make sure aphiaID will be available for downstream analyses
        while self.aphiaID is None:
            try:
                self.aphiaID = urllib.request.urlopen(aphiaID_url).read().decode('utf-8')
            except urllib.error.HTTPError:
                pass

        self.records_url = "http://www.marinespecies.org/rest/AphiaChildrenByAphiaID/" + \
                      self.aphiaID + \
                      "?marine_only=true&offset=1"
        self.accepted_name = ""
        self.classfication_url = "http://www.marinespecies.org/rest/AphiaClassificationByAphiaID/"

    def get_children_names(self, till = "Species"):

        records_url = 'http://www.marinespecies.org/rest/AphiaChildrenByAphiaID/205965?marine_only=true&offset=1'

        page = urllib.request.urlopen(records_url).read().decode('utf-8')

        names = [names.replace('\"','').replace('valid_name:', '') for names in re.findall('"valid_name":"[A-Z][a-z]+[ a-z]+"', page)]

        ## in progress
        pass

    def get_accepted_name(self):
        """this function assumes that name is deprecated and tries to find epitopes
        which is more similar with
        """
        # species with unaccepted names for testing:
        #self = Worms("Paratrophon exsculptus")
        #self =  Worms("Manta birostris")

        if len(self.aphiaID) == 0 or self.aphiaID == '-999':

            species_binary = self.taxon.split("%20")

            genus_id_url = "http://www.marinespecies.org/rest/AphiaIDByName/" + species_binary[0] + "?marine_only=true"

            genus_id = urllib.request.urlopen(genus_id_url).read().decode('utf-8')

            complete_url = "http://www.marinespecies.org/aphia.php?p=taxdetails&id=" + genus_id

            page = urllib.request.urlopen(complete_url).read().decode('utf-8')

            # line which contains span
            lines = re.findall("<span.*>" + species_binary[0] + "[\(A-Za-z\) ]{0,} [a-z]+<.*", page)

            # it takes the first species pattern
            epitopes = [re.findall("<i>[A-Z][a-z]+[\(\)A-Za-z ]{0,} [a-z]+</i>", i)[0].split(" ")[-1].replace("</i>", "") for i in lines]


            def get_pieces(string, amplitude):

                pieces = [string[i:i + amplitude] for i in range(len(list(string)))]

                trimmed_pieces = [i for i in pieces if len(i) > amplitude - 1]

                return trimmed_pieces

            for index in range(len(list(species_binary[1])) - 1):
                # pieces by the length of index, e.g.,
                # if the string is "abc" and index = 0, then ['a', 'b', 'c']
                # if the string is "abc" and index = 1, then ['ab', 'bc']

                a = get_pieces(species_binary[1], index + 1)

                lengths = []

                for string in epitopes:

                    matches = [re.findall(i, string) for i in set(a)]
                    # n1 is the number of matches that pieces `a` have with a string
                    # d1 is the number of choices available for matches from a string

                    if len(get_pieces(string, index + 1)) == 0:
                        # if a, which are pieces of `species_binary[1]`, is larger than
                        # the string, you will always have zero matches. That is, `n1` will
                        # be always zero. So, it does not care what value takes d1. In this
                        # case it will take 1 so as to avoid emerging conflicts from division

                        d1 = 1
                    else:
                        d1 = len(get_pieces(string, index + 1))
                    # number of matches. Since inside sum function there is just a list of lists,
                    # sum only counts crowded lists,i.e., number of matches
                    n1 = sum([len(c) for c in matches])

                    # since it can appear a large string with multiple matches from just a part of it,
                    # n1/d1 is just a measure of quality in matches


                    # d2 is the number of pieces of `a`.
                    # n2 is the number of pieces that did not have any match with pieces a string
                    # therefore, 1 - n2/d2 is a measure of coverage on a, or `species_binary[1]`
                    d2 = len(set(a))
                    n2 = len(set(a) - set(["".join(set(b)) for b in matches if len(b) > 0])) #len(b) filter just matches

                    # render index
                    lengths.append(n1/d1 + 1 - n2/d2)

                check_max_epitopes = []
                # check if that max value of `length` just belongs to one single epitopes
                for d in range(len(lengths)):
                    if lengths[d] == max(lengths):
                        check_max_epitopes.append(epitopes[d])

                # the loop increase the word size till there is only one single max index
                if len(set(check_max_epitopes)) == 1:
                    page_line = lines[lengths.index(max(lengths))]

                    self.accepted_name = re.findall("<i>[A-Z][a-z]+ [a-z]+</i>", page_line)[-1].replace("<i>", "").replace("</i>", "")

                    self.aphiaID = re.findall("aphia.php\?p=taxdetails&id=[0-9]+", page_line)[0].replace("aphia.php?p=taxdetails&id=","")

                    break

            return self.accepted_name

        else:
            complete_url = "http://www.marinespecies.org/aphia.php?p=taxdetails&id=" + self.aphiaID

            page = None
            # make sure aphiaID will be available for downstream analyses
            while page is None:
                try:
                    page = urllib.request.urlopen(complete_url).read().decode('utf-8')
                except urllib.error.HTTPError:
                    pass

            if len(re.findall(">unaccepted<", page)) == 1:

                # get down till species name line:
                line = re.findall('id="AcceptedName".*\n.*\n.*\n.*\n.*', page)[0]

                # previously tested:
                #line = re.findall("p=taxdetails&id=(?!" + self.aphiaID + ").*<i>[A-Z][a-z]+ [a-z]+</i>", page)[0]
                #line = re.findall(">Accepted Name<.*p=taxdetails&id=[0-9]+.*></i><i>[A-Z][a-z]+ [a-z ]{1,}</i>",
                #           page.replace("\n", ""))[0]
                #self.accepted_name = re.sub(".*</i><i>(.*)</i>", "\\1", line)

                self.accepted_name = re.sub(".*</i><i>(.*)</i>.*", "\\1", line.replace("\n", ""))

                return self.accepted_name

            else:
                self.accepted_name = self.taxon.replace("%20", " ")

                return self.accepted_name

    def taxamatch(self):

        complete_url = "http://www.marinespecies.org/rest/AphiaRecordsByMatchNames?scientificnames%5B%5D=" + \
                       self.taxon + \
                       "&marine_only=true"

        page = urllib.request.urlopen(complete_url).read().decode('utf-8')

        self.accepted_name = re.sub('.*"valid_name":"(.*)","valid_.*',"\\1", page )

        return self.accepted_name

    def get_taxonomic_ranges(self):
        """Name of all valuable ranks are retrieved and stored at self.taxonomic_ranges and
        also complete string of information used to get it at self.classification_page
        """

        complete_url = self.classfication_url + self.aphiaID

        # This while loop is because of classfication page, or classification string, is needed
        # since self.classification_page is not starting with a value,
        # this while loop may not slow down its request
        while self.classification_page == "":
            try:
                self.classification_page = urllib.request.urlopen(complete_url).read().decode('utf-8')
            except urllib.error.HTTPError:
                pass

        # grant with a white space into the pattern can end up as non-smart search, but it is kept anyways
        self.taxonomic_ranges = [re.sub('"rank":"([A-Za-z ]+)"', "\\1", i) for i in re.findall('"rank":"[A-Za-z ]+"', self.classification_page)]

    def get_rank(self, rank):

        if len(self.taxonomic_ranges) == 0:
            # if there is not a list of ranks for comparing with the rank variable
            # then, get it with the following and store them
            self.get_taxonomic_ranges()

        # since the prior ensures a list of rank's names, rank variable is looked between them
        spell = [i for i in self.taxonomic_ranges if i == rank]

        # if there was not any match, then a "check_spell" is returned
        if len(spell) == 0:
            return "check_spell"

        return  re.sub('.*"rank":"' + spell[0] + '","scientificname":"([A-Za-z ]+)".*',
                       "\\1",
                       self.classification_page)
