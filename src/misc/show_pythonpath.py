import os
import sys


print("Current working dir: ", os.getcwd())

print("All the paths that Python is using for loading & checking for Packages:")
print('\n'.join(sys.path))
