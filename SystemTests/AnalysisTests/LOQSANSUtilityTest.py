import stresstesting
from mantid.simpleapi import *
from mantid import config
import SANSUtility as su
import SANSadd2 as add

import os

def unixLikePathFromWorkspace(ws):
    return su.getFilePathFromWorkspace(ws).replace('\\','/')


class SANSUtilityTest(stresstesting.MantidStressTest):

    def runTest(self):
        # created after issue reported in #8156
        ws = Load('LOQ54432')
        self.assertTrue('Data/LOQ/LOQ54432.raw' in unixLikePathFromWorkspace(ws))
        ws = Load('LOQ99618.RAW')
        self.assertTrue('Data/LOQ/LOQ99618.RAW' in unixLikePathFromWorkspace(ws))
        add.add_runs(('LOQ54432','LOQ54432'),'LOQ','.raw')
        ws = Load('LOQ54432-add')
        file_path =  unixLikePathFromWorkspace(ws)
        self.assertTrue('logs/LOQ54432-add' in file_path)
        os.remove(file_path)
        
