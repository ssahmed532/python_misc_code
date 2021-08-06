import rarfile
import sys


filename = sys.argv[1]

contents = []

rf = rarfile.RarFile(filename)
for f in rf.infolist():
    contents.append(f.filename)

print("rarfile {0} contains {1} files: ".format(filename, len(contents)))
for file in contents:
    print("    {0}".format(file))
