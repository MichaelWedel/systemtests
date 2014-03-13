import stresstesting
from mantid.simpleapi import *
import numpy as np

'''This test checks that the results of PoldiAutoCorrelation match the expected outcome.'''
class POLDIMergeTest(stresstesting.MantidStressTest):  
  def runTest(self):
    dataFiles = ["poldi2013n006903", "poldi2013n006904"]
    
    self.loadData(dataFiles)
    self.runPoldiMerge(dataFiles)
    
    self.loadReferenceData()
    self.analyseResults()
    
  def loadData(self, filenames):
    for dataFile in filenames:
      LoadSINQFile(Instrument='POLDI',Filename=dataFile + ".hdf",OutputWorkspace=dataFile)
      LoadInstrument(Workspace=dataFile, InstrumentName="POLDI", RewriteSpectraMap=True)
      
  def runPoldiMerge(self, workspaceNames):
    PoldiMerge(WorkspaceNames=workspaceNames, OutputWorkspace="poldi_sum_6903_6904")
      
  def loadReferenceData(self):
    Load(Filename="poldi_sum_6903_6904_reference.nxs", OutputWorkspace="poldi_sum_6903_6904_reference")

  def analyseResults(self):
    for i in range(mtd['poldi_sum_6903_6904_reference'].getNumberHistograms()):
        self.assertTrue(np.array_equal(mtd['poldi_sum_6903_6904'].dataY(i), mtd['poldi_sum_6903_6904_reference'].dataY(i)))
      
