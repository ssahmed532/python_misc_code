import os
import sys

from wordcount import WordCounter


def replace_words(filename):
    with open(filename, 'r') as input:
        real_path = os.path.realpath(filename)
        filename_portion = os.path.basename(real_path)

        new_filename = os.path.dirname(real_path) + os.sep + "replaced_" + filename_portion

        with open(new_filename, 'w')as output:
            for line in input:
                line = line.rstrip()
                newline = line.replace("Alice", "Dora the Explorer")
                print(newline)
                output.write(newline)
        
        return new_filename


if __name__ == '__main__':
    filename = sys.argv[1]
    replaced_filename = replace_words(filename)

    wc_obj = WordCounter(filename)
    print("Word counts for original file {0}: {1}".format(filename, wc_obj.word_count()))
    print("WordCounter __name__:", WordCounter.__name__)
    print()

    wc_obj_replaced = WordCounter(replaced_filename)
    print("Word counts for *replaced* file {0}: {1}".format(replaced_filename, wc_obj_replaced.word_count()))
    print("replace __name__:", __name__)
    print()
