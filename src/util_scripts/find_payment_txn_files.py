import datetime
import os
import stat
import sys


DIR_PATH = r'C:\Users\ssahm\OneDrive\Pictures'

START_DATE = datetime.date.fromisoformat('2020-07-01')
END_DATE = datetime.date.fromisoformat('2021-06-30')


if __name__ == "__main__":
    """A simple script to find all files in a specified path that
       were modified between a specific date range.
    """
    files = os.listdir(DIR_PATH)
    for f in files:
        full_path = os.path.join(DIR_PATH, f)

        statinfo = os.stat(full_path)

        if not stat.S_ISDIR(statinfo.st_mode) and stat.S_ISREG(statinfo.st_mode):
            last_modified_dt = datetime.date.fromtimestamp(statinfo.st_mtime)

            if (last_modified_dt >= START_DATE) and (last_modified_dt <= END_DATE):
                print(full_path)
