from app.config import DEFAULT_MANPATH, MANPATH
from glob import glob
import os

def search(manual):
    '''Search for manual. First find everything that matches the input, then
    break it up into components (manpath, manpage, section) and return it as a
    dictionary.
    '''
    #: Absolute paths of any manpages found
    abs_paths = []
    for path in MANPATH:
       abs_paths = abs_paths + glob(path + '/*/' + manual + '.*')

    #: Split the paths into their components (manpath, manpage & section)
    results = {} 
    for path in abs_paths:
        #: Get the manpath where the manpage is located
        manpath = os.path.dirname(path).rsplit('/', 1)[0]
        #: Get its index in the list of all manpaths available (MANPATH global)
        manpath_index = MANPATH.index(manpath)
        #: Full filename of man page without file extension 
        filename = os.path.basename(path).split('.')
        # Remove file extension from the filename
        if 'gz' in filename: filename.remove('gz')

        # Handle long filenames such as mkfs.ext4.8
        if len(filename) == 3:
            #: Manpage is always the 1st and 2nd element (e.g. mkfs.ext4)
            manpage = '.'.join(map(str, filename[0:-1]))
            #: Section is always the last element (e.g. 8)
            section = filename[-1]
        else:
            manpage = filename[0]
            section = filename[1]

        results[manpage] = {'section':section, 'path_index':manpath_index}
    
    return results
