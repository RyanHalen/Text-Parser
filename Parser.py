# Parsing Framework Script

"""
This script contains the necessary conversion, import, export, and class methods 
for parsing simple pdf documents according to a pre-set instruction csv. Raw regular
expression matches are additionally input into optional methods, contained in a 
seperate imported module, to construct a data dictionary that can be output to a 
flat csv. 
"""

# Initial Author: Ryan Halen
# Started: 02/22/21
# Last Modified: 03/19/21 RH

# Start
from tika import parser
import re
import parserMethods as pm
import csv
from datetime import datetime

# Create Data Class
class varParse():
    """
    varParse class intakes a row from an instruction set csv that contains:
        1) a variable name
        2) an optional method
        3) a series of regular expresions
    The varParse class initiates by reading in a row of instructions from a csv 
    file. These instructions  create attributes used to extract a matching 
    regular expression from a provided document. The matched text is then input
    to the attendant method, with the result being the final text version.
    """
    
    def __init__(self, row):
        """
        The initialzing function takes in a row argument to create a variable 
        name, attached method, and series of regular expressions, stored as a 
        list.
        """
        self.name = row[0]
        if row[1]:
            self.method = getattr(pm, row[1])
        else:
            self.method = pm.ident
        self.regex = [row[2]]
        self.matches = None
        self.text = None
        self.cleanText = None
        
    def matchText(self, doc):
        """
        matchText takes in a raw text from a parsed pdf document (although just 
        text works as well) and returns a list of matched text from all regular 
        expresions contained in the regex class attribute list.
        """
        
        try:
            self.matches = [re.compile(exp).search(doc) for exp in self.regex]
            
            if self.matches[0] is not None:
                print('{0} matches found for {1}'.format(str(len(self.matches)), 
                  self.name))
                self.text = [match.group(0) for match in self.matches]
                print(self.text)
                self.funcText()
                return self.text
            else:
                print('No matches found for {}'.format(self.name))
                return None
        except:
            print('RE error')
            return None
        
    def funcText(self):
        """
        funcText runs any text contained in the text class attribute through the 
        method class attribute and returns a list of each item. These items are 
        also stored in the cleanText class attribute.
        """
        
        if self.text:
            self.cleanText = [self.method(text) for text in self.text]
            return self.cleanText
        else:
            print('No text matches for {}'.format(self.name))
            return None  

# Santize Text
def sanitize(charlist, text):
    """
    sanitize takes in a list of characters and a block of text as arguments and
    replaces each character in the character list with an empty string in the 
    provided text block. Returns the sanitized text.
    """
    if text is not None:
        cleanText = text
        for char in charlist:
            cleanText = cleanText.replace(char, '')
        return cleanText
    else: return text
    
def sanitizeURL(text):
    
    """
    Searches for URL text in the large text body and replaces any matches with 
    an empty string. Replaces the text attribute with the santized text.
    """
    
    urls = re.findall('http.*\n{1}', text)
    
    if urls:
        for url in urls:
            text.replace(url, '')
        
    return text    

# Load Documents And Instruction Sets
def docLoad(filename='DocFiles.csv'):
    """
    docLoad imports a master csv file as a dictionary. The master csv contains 
    a list of all filepaths and instruction sets, as well as a primary ID key.
    The file should have the following columns: Instruction Set, ID, Directory,
    and File. A dictionary is returned with the ID as a primary key, and each 
    unique Instruction Set under that ID as a seperate dictionary with the directory, 
    file name, and parsed document text attached as key-value pairs.
    """
    data = {}
    sanitizeChar = [';', '_']
    
    with open(filename, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for row in csvreader:
            if not row[4]: #Test for any entry in the multSplit column, which would indicate that the instruction set should be replicated for each subsection in the text denoted by the regular expresion values
                if row[1] not in data:
                    data[row[1]] = {row[0]:{'Directory':row[2], 
                        'File':row[3], 
                        'Text':sanitizeURL(sanitize(sanitizeChar, parser.from_file(row[2]+row[3])['content']))}}
                else:
                    data[row[1]][row[0]] = {'Directory':row[2], 
                        'File':row[3], 
                        'Text':sanitizeURL(sanitize(sanitizeChar, parser.from_file(row[2]+row[3])['content']))}
                
    return data

# Import Directions based on Instruction Sets
def instrLoad(filename):
    """
    instrLoad loads a single set of parsing instructions and returns a dictionary 
    of all variable names and varParse objects associated with those names.
    """
    
    data = {}
    
    with open(filename, 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for row in csvreader:
            data[row[0]]=varParse(row)
    
    return data

def dirLoad(doc_dict):
    """
    dirLoad loads direction sets for each unique Instruction set contained within 
    the passed document dictionary (created through the docLoad function). Returns
    a dictionary with each instruction set key attached to a value list of all
    varParse class objects created by the directions.
    """
    
    data = {}
    for ID in doc_dict:
        for instruction in doc_dict[ID]:
            if instruction not in data:
                data[instruction] = instrLoad('{}Instructions.csv'.format(instruction))
    
    return data

# Loop over variables
def extractText(ID, document, directions):
    """
    extractText takes an ID dictionary and a document keyword argument to obtain 
    a unique ID-document pair and parse the document according to the document 
    keyword in the directions dictionary passed by the relevant directions dictionary. 
    Returns a dictionary with variable names as keys and cleaned text (per 
    varParse class) as values.
    """
    
    data = {}
    
    doc = ID[document]['Text']
    
    for key, var in directions[document].items():
        if var.matchText(doc):
            data[var.name] = ','.join(var.cleanText)
        else:
            data[var.name] = ''
        
    return data   

# Export Data Dictionary
def exportData(direction, data_dict, single=True, filename='test.csv'):
    """
    exportData takes a direction keyword, and extracts the relevant data associated
    with the insruction set denoted by the direction keyword from the passed data
    dictionary. This information is structed as a dataframe with the variables 
    as the column names and ID keys of the data_dict as rows. The information is 
    then written to the passed filename argument.
    """
    
    if single:
    
        with open(filename, 'w') as file:
            csvwriter = csv.writer(file, dialect='excel', lineterminator='\n')
            IDs = [key for key in data_dict]
            headers = ['StudyID'] + [key for key in data_dict[IDs[0]][direction]['Data']]
            print(headers)
            csvwriter.writerow(headers)
            for ID in IDs:
                row = [ID] + [data for key, data in data_dict[ID][direction]['Data'].items()]
                print(row)
                csvwriter.writerow(row)
                
    else:
        with open(filename, 'w') as file:
            csvwriter = csv.writer(file, dialtect='excel', lineterminator='\n')
            IDs = [key for key in data_dict]
            headers = ['StudyID'] + ['EntryNo'] + [key for key in data_dict[IDs[0]][direction]['Data']]
            print(headers)
            csvwriter.writerow(headers)
            for ID in IDs:
                row = ID.split('|') + [data for key, data in data_dict[ID][direction]['Data'].items()]
                print(row)
                csvwriter.writerow(row)
# Main Loop
def main():
    """
    Main function.
    """
    
    print(datetime.now().strftime('%H:%M:%S'))
    
    docs = docLoad()
    dirs = dirLoad(docs)
    
    for ID in docs:
        print('\n', ID, '\n____________________________________________')
        for instructions in dirs:
            docs[ID][instructions]['Data'] = extractText(docs[ID], instructions, dirs)
            
    for instruction in dirs:
        exportData(instruction, docs)
        
    print(datetime.now().strftime('%H:%M:%S'))
        
if __name__ == '__main__':
    main()