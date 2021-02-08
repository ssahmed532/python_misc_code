import os
import pefile
import shutil


def getFilename(filePath):
    return os.path.basename(filePath)


def getFileExtension(filePath):
    filename = getFilename(filePath)
    return os.path.splitext(filename)[1]


def getFileList(dirPath, matchingExtensions=None):
    """
    Returns a list of files present in a directory.
    Optionally, only include those files that match the given extension.

    Args:
            dirPath: the directory path for which to get files.
            matchingExtensions: optional extension to match files against.

    Returns:
            A list of files present in the specified directory path.
    """

    fileList = []

    if matchingExtensions is None:
        fileList = [os.path.join(dirPath, f) for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]
    else:
        fileList = [os.path.join(dirPath, f) for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f)) and getFileExtension(f).lower() in matchingExtensions]

    return fileList


def getFileVersionInfo(filePath):
    #
    # Code addapted from:
    #   http://stackoverflow.com/questions/5996650/find-version-of-binary-file
    #   http://stackoverflow.com/questions/1264472/using-the-pefile-py-to-get-file-exe-version
    #
    # Note that this function requires the pefile module to be installed.
    #
    fileVerInfo = None
    prodVerInfo = None

    pe = pefile.PE(filePath)
    if 'VS_FIXEDFILEINFO' not in pe.__dict__:
        print('ERROR: Oops, {} has no version info. Unable to continue.'.format(filePath))
        return None, None

    if not pe.VS_FIXEDFILEINFO:
        print('ERROR: VS_FIXEDFILEINFO field not set for {}. Unable to continue.'.format(filePath))
        return None, None

    verinfo = pe.VS_FIXEDFILEINFO

    fileVerInfo = '{:d}.{:d}.{:d}.{:d}'.format(
        verinfo.FileVersionMS >> 16,
        verinfo.FileVersionMS & 0xFFFF,
        verinfo.FileVersionLS >> 16,
        verinfo.FileVersionLS & 0xFFFF)

    prodVerInfo = '{:d}.{:d}.{:d}.{:d}'.format(
        verinfo.ProductVersionMS >> 16,
        verinfo.ProductVersionMS & 0xFFFF,
        verinfo.ProductVersionLS >> 16,
        verinfo.ProductVersionLS & 0xFFFF)

    if fileVerInfo != prodVerInfo and False:
        print('WARNING: File version info ({}) does not match Product version info ({}) for file {}'.format(fileVerInfo, prodVerInfo, getFilename(filePath)))

    return fileVerInfo, prodVerInfo


def copyFile(filePath, destDir):
    """
    Copy a file to a specified directory path.

    Args:
            filePath: the absolute path to the file to be copied.
            destDir: destination directory to copy the file to.
    """
    os.makedirs(destDir, exist_ok=True)
    shutil.copy2(filePath, destDir)
    print('Copied file {} to {}'.format(filePath, destDir))


def getAllFilesRecursive(dirPath):
    """ Function to recursively retrieve all files present in the
        specified directory path, including all sub-directories.

        Args:
            dirPath: the directory path for which to get all files.

        Returns:
            A list of all files present in the specified directory
            path including all sub-directories.

    """
    files = []

    try:
        for entry in os.scandir(dirPath):
            if entry.is_file():
                files.append(entry.path)
            elif entry.is_dir():
                # recurse into sub-dir and add all files found in there
                files = files + getAllFilesRecursive(entry.path)
    except PermissionError:
        print('Skipping dir path {} due to permissions issues'.format(dirPath))

    return files
