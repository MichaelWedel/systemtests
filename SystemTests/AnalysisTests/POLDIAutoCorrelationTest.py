import stresstesting
from mantid.simpleapi import *
import numpy as np

'''This test checks that the results of PoldiAutoCorrelation match the expected outcome.'''
class POLDIAutoCorrelationTest(stresstesting.MantidStressTest):  
  def runTest(self):
    dataFiles = ["poldi2013n006903", "poldi2013n006904"]
    
    self.prepareDataFilesForAnalysis(dataFiles)
    self.loadReferenceData(dataFiles)
    
    # run autocorrelation and all dependencies for loading instrument etc.
    PoldiProjectRun(mtd["TestWorkspace"], OutputWorkspace="ResultWorkspace")
    
    self.analyseResults(dataFiles)
    
  def prepareDataFilesForAnalysis(self, filenames):
    for dataFile in filenames:
      PoldiProjectAddFile("%s.hdf" % (dataFile), OutputWorkspace="TestWorkspace")
      
  def loadReferenceData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference.nxs" % (dataFile), OutputWorkspace="%s_reference" % (dataFile))

  def analyseResults(self, filenames):
    for dataFile in filenames:
      workspaceNameTemplate = "Comparison_%s" % (dataFile)
      
      referenceData = mtd["%s_reference" % (dataFile)].dataY(0)
      calculatedData = mtd["%sCorr" % (dataFile)].dataY(0)
      
      self.assertEqual(calculatedData.shape[0], referenceData.shape[0], "Number of d-values does not match for %s (is: %i, should: %i)" % (dataFile, calculatedData.shape[0], referenceData.shape[0]))
      
      CreateWorkspace(referenceData, calculatedData, OutputWorkspace=workspaceNameTemplate)
      
      fitNameTemplate = "Fit_%s" % (dataFile)
      Fit("name=LinearBackground", mtd[workspaceNameTemplate], StartX=-1000, EndX=10000, Output=fitNameTemplate)
      
      fitResult = mtd[fitNameTemplate + "_Parameters"]
      
      slope = fitResult.cell(1, 1)
      self.assertGreaterThan(slope, 0.95, "Slope is too small for %s (is: %d)" % (dataFile, slope))
      self.assertLessThan(slope, 1.0, "Slope is larger than 1.0 for %s (is: %d)" % (dataFile, slope))
      
      relativeSlopeError = fitResult.cell(1, 2) / slope
      self.assertLessThan(relativeSlopeError, 1e-4, "Relative error of slope is too large for %s (is: %d)" % (dataFile, relativeSlopeError))
      
      intercept = fitResult.cell(0, 1)
      self.assertLessThan(intercept, 5.0, "Intercept is too large for %s (is: %d)" % (dataFile, intercept))
      
      relativeInterceptError = fitResult.cell(0, 2) / intercept
      self.assertLessThan(relativeInterceptError, 1e-1, "Relative error of intercept is too large for %s (is: %d)" % (dataFile, relativeInterceptError))
      
      residuals = mtd[fitNameTemplate + "_Workspace"].dataY(2)
      maxAbsoluteResidual = np.max(np.abs(residuals))
      self.assertLessThan(maxAbsoluteResidual, 0.5, "Maximum absolute residual is too large for %s (is: %d)" % (dataFile, maxAbsoluteResidual))
      
