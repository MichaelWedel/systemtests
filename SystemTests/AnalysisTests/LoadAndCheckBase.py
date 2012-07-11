"""
These system tests are to verify the behaviour of the ISIS reflectometry reduction scripts
"""

import stresstesting
from mantid.simpleapi import *
import mantid.api._api

from abc import ABCMeta, abstractmethod

class LoadAndCheckBase(stresstesting.MantidStressTest):

    __metaclass__ = ABCMeta # Mark as an abstract class
    
    __comparison_out_workspace_name = 'a_integrated'
    
    @abstractmethod
    def get_raw_workspace_filename(self):
        """Returns the name of the raw workspace file"""
        raise NotImplementedError("Implement get_raw_workspace_filename")
    
    @abstractmethod
    def get_nexus_workspace_filename(self):
        """Returns the name of the nexus workspace file"""
        raise NotImplementedError("Implement get_nexus_workspace_filename")
          
    @abstractmethod
    def get_expected_number_of_periods(self):
        return 1
        
    @abstractmethod
    def get_integrated_reference_workspace_filename(self):
        """Returns the name of the benchmark file used for end-of-test comparison."""
        raise NotImplementedError("Implement get_nexus_workspace_filename")
    
    def do_check_workspace_shape(self, ws1, ws2):
        self.assertTrue(ws1.getNumberHistograms(), ws2.getNumberHistograms())
        self.assertTrue(len(ws1.readX(0)) == len(ws2.readX(0)))
        self.assertTrue(len(ws1.readY(0)) == len(ws2.readY(0)))
    
    def runTest(self):
        Load(Filename=self.get_nexus_workspace_filename(), OutputWorkspace='nexus')
        Load(Filename=self.get_raw_workspace_filename(), OutputWorkspace='raw')
        
        a = mtd['nexus']
        b = mtd['raw']
        n_periods = self.get_expected_number_of_periods()
        
        self.assertTrue(type(a) == type(b))

        #raise NotImplementedError()
        if(isinstance(a,mantid.api._api.WorkspaceGroup)):
            self.assertTrue(a.size() == b.size())
            self.assertTrue(a.size() == n_periods)
            # Loop through each workspace in the group and apply some simple comaprison checks.
            for i in range(0, a.size()):
                self.do_check_workspace_shape(a[i], b[i])
            Integration(InputWorkspace=a[0], OutputWorkspace=self.__comparison_out_workspace_name)
        else:
            self.do_check_workspace_shape(a, b)
            Integration(InputWorkspace=a[0], OutputWorkspace=self.__comparison_out_workspace_name)
        
    def validate(self):
        return self.__comparison_out_workspace_name, self.get_integrated_reference_workspace_filename()

    
    