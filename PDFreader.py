""" This script contains the necessary classes and functions to parse PDF files 
for specific field information. A document class is defined that is initialized 
with a filename and parsing directions. The filename links to a parsable PDF while
the parsing directions provide the relevant field names and a list of regular 
expressions to be used to identify values. The fields and values identified are
then stored as a class attribute dictionary that can be exported as a single line
entry to an exisitng csv file, or a new csv file entirely. """

# Author: Ryan Halen
# Date Started: 2/16/20

# Last Modified: 8/21/20 (RH)

# Import Statements
from tika import parser
import csv
import re
import os

#Class Definition

class parseDoc:
    
    def __init__(self, filename, directions, outfile):
        
        self.source = filename
        self.direction_source = directions
        self.outfile = outfile
        
        #Create file object
        self.raw_text = parser.from_file(self.source)
        self.content = self.raw_text['content'].split('\n\n')
        
        #Create Directions object
        with open(self.direction_source, 'r') as directions_obj:
            self.raw_directions = csv.reader(directions_obj, dialect='excel')
            
        #Create Direction Dict
        self.parse_directions = {line[0]:line[1:] for line in self.raw_directions}
        self.fields = self.parse_directions.keys()
        self.retext = self.parse_directions.values()
        
        #Create Data Dict
        self.data = {field:'' for field in self.fields}
        
    def parse_field(self, field, re_direct):
        """
        Primary function that extracts an item of text using a single regular expresion.
        Stores obtain text, if exists, into class data dictionary under field name,
        else stores 'ERROR'.
        """
        try:
            self.data[field] = re.match(re_direct, self.content).group(1)
        except Exception as err:
            print('Search for {0} field failed with {1}'.format(field, err))
            self.data[field] = 'ERROR'
            
    def export(self):
        """
        Writer function to output data dictionary to a specific file. Will create 
        a new file called outfile if non-exists in the current directory, else will
        append a new line to existing file (fields and headers must match).
        """
        
        if self.outfile not in os.listdir():
            with open(self.outfile, 'w', newline='\n') as file:
                csvwriter = csv.writer(file)
                csvwriter.writerow([key for key in self.fields])
                csvwriter.writerow([self.data[key] for key in self.fields])
        else:
            with open(self.outfile, 'a', newline='\n') as file:
                csvreader = csv.reader(file)
                csvwriter = csv.writer(file)
                headers = next(csvreader)
                csvwriter.writerow([self.data[key] for key in headers])
            
    def parseLoop(self):
        """
        Wrapper function for the parse_field function. Attempts to extract all
        data for each field. Can attempt multiple listed regular expressions; 
        will return first non-ERROR or '' data match.
        """
        
        for field, retext in self.parse_directions.items():
            i = 0
            while self.data[field] == '' or self.data[field] == 'ERROR':
                if i > len(retext): break
                self.parse_field(field, retext[i])
                i += 1
                
        self.export()
                    