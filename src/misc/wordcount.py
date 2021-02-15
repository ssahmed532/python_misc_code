#
# http://veekaybee.github.io/2017/09/26/python-packaging/
#

import re
import sys


class WordCounter:

    def __init__(self, filename):
        self.filename = filename

    def open_file(self, filename):
        """ Opens the specified file and returns the file contents """
        with open(filename, 'r') as f:
            file_contents = f.read()
            return file_contents
    

    def word_count(self):
        """ Returns a file's word count """
        file_contents = self.open_file(self.filename)

        return len(file_contents.split())
    

    def sentence_count(self):
        """ Returns a file's sentence count """
        file_contents = self.open_file(self.filename)

        return file_contents.count('.') + file_contents.count('!') + file_contents.count('?')
    
    
    def letter_count(self):
        letter_count = 0

        re_pattern = r'[\W]' # exclude all punctuation

        file_contents = self.open_file(self.filename)
        
        total_words = file_contents.split()

        for word in total_words:
            for letter in word:
                if not re.search(re_pattern, letter):
                    letter_count += 1
        
        return letter_count

    def counts(self):
        print("Word counts for file ", self.filename)
        print("\tword count: ", self.word_count())
        print("\tsentence count: ", self.sentence_count())
        print("\tletter count: ", self.letter_count())
        #print(self.word_count(), '\n', self.sentence_count(), '\n', self.letter_count())


if __name__ == "__main__":
    wc_obj = WordCounter(sys.argv[1])
    wc_obj.counts()
