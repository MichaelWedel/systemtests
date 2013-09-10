from mantid.simpleapi import *
from mantid.api import FrameworkManager
import os
import re
import glob
import stresstesting
import multiprocessing

EXPECTED_EXT = '.expected'

def loadAndTest(filename):
    """Do all of the real work of loading and testing the file"""
    try:
        wksp = LoadEmptyInstrument(filename)
        if wksp is None:
            return filename
    except Exception, e:
        return filename

    # TODO standard tests
    if wksp.getNumberHistograms() <= 0:
        del wksp
        return filename
    if wksp.getMemorySize() <= 0:
        print "Workspace takes no memory: Memory used=" + str(wksp.getMemorySize())
        del wksp
        return filename

    # cleanup
    del wksp
    return None


class LoadLotsOfInstruments(stresstesting.MantidStressTest):
    def __getDataFileList__(self):
        # get a list of directories to look in
        direc = config['instrumentDefinition.directory']
        print "Looking for instrument definition files in: %s" % direc
        cwd = os.getcwd()
        os.chdir(direc)
        myFiles = glob.glob("*Definition*.xml")
        os.chdir(cwd)
        # Files and their corresponding sizes. the low-memory win machines
        # fair better loading the big files first
        files = []
        for filename in myFiles:
            files.append(os.path.join(direc, filename))
        files.sort()
        return files

    def runTest(self):
        """Main entry point for the test suite"""
        files = self.__getDataFileList__()

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        # run the tests
        failed = []
        result = pool.imap_unordered(loadAndTest,files)
        pool.close()
        try:
            while True:
                filename = result.next()
                if filename is not None:
                    print "FAILED TO LOAD '%s'" % filename
                    failed.append(filename)
        except StopIteration:
            pass

        # final say on whether or not it 'worked'
        print "----------------------------------------"
        if len(failed) != 0:
            print "SUMMARY OF FAILED FILES"
            for filename in failed:
                print filename
            raise RuntimeError("Failed to load %d of %d files" \
                                   % (len(failed), len(files)))
        else:
            print "Successfully loaded %d files" % len(files)
	    #print files
