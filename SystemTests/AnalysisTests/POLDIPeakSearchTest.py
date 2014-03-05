import stresstesting
from mantid.simpleapi import *
import numpy as np

'''This test checks that the results of PoldiAutoCorrelation match the expected outcome.'''
class POLDIPeakSearchTest(stresstesting.MantidStressTest):  
  def runTest(self):
    dataFiles = ["poldi2013n006903", "poldi2013n006904"]
    
    self.loadReferenceCorrelationData(dataFiles)
    self.loadReferencePeakData(dataFiles)
    self.runPeakSearch(dataFiles)
    self.analyseResults(dataFiles)
      
  def loadReferenceCorrelationData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference.nxs" % (dataFile), OutputWorkspace=dataFile)
      
  def loadReferencePeakData(self, filenames):
    for dataFile in filenames:
      Load(Filename="%s_reference_Peaks.nxs" % (dataFile), OutputWorkspace="%s_reference_Peaks" % (dataFile))

  def runPeakSearch(self, filenames):
    for dataFile in filenames:
      PoldiPeakSearch(InputWorkspace=dataFile, OutputWorkspace="%s_Peaks" % (dataFile))

  def analyseResults(self, filenames):
    for dataFile in filenames:
      calculatedPeaks = mtd["%s_Peaks" % (dataFile)]
      referencePeaks = mtd["%s_reference_Peaks" % (dataFile)]
      self.assertEqual(calculatedPeaks.rowCount(), referencePeaks.rowCount())
      
      positions = calculatedPeaks.column(0)
      referencePositions = referencePeaks.column(0)
      
      for position, referencePosition in zip(positions, referencePositions):
          self.assertDelta(position, referencePosition, 1e-6)

      intensities = calculatedPeaks.column(1)
      referenceIntensities = referencePeaks.column(1)
      
      for intensity, referenceIntensity in zip(intensities, referenceIntensities):
          self.assertDelta(intensity, referenceIntensity, 1e-3)
