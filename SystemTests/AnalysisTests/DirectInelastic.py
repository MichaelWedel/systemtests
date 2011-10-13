import stresstesting
from mantidsimple import Load, AddSampleLog

from DirectEnergyConversion import setup_reducer

def do_reduction(mono_run, white, van_run):
  '''Call the actual reduction routines
  '''
  reducer = setup_reducer('MARI')
  ei = 11
  reducer.energy_bins = [-11,0.05,11]
  # Disable auto save
  reducer.save_formats = []
  reducer.map_file = 'mari_res.map'
  reducer.abs_map_file = reducer.map_file
  reducer.sample_mass = 10
  reducer.sample_rmm = 435.96
  
    # Diagnostics
  reducer.spectra_masks = reducer.diagnose(white, mono_run,remove_zero=True, tiny=0.0, large=1e10, median_lo=0.1,
                                           median_hi=3.0, signif=3.3, bkgd_threshold=5.0, variation=1.1)
  
  reducer.convert_to_energy(mono_run=mono_run, ei=ei, white_run=white,
                            mono_van=van_run, abs_white_run=white)


class ReduceMonoFromFile(stresstesting.MantidStressTest):
    
  def runTest(self):
    
    mono_run = 11015
    white = 11060
    van_run = 11001
    do_reduction(mono_run, white, van_run)

  def validate(self):
    # Need to disable checking of the Spectra-Detector map because it isn't
    # fully saved out to the nexus file; some masked detectors should be picked
    # up with by the mask values in the spectra
    self.disableChecking.append('SpectraMap')
    self.disableChecking.append('Instrument')
    return '11015.spe','DI.ReduceMonoFromFile.nxs'
    
class ReduceMonoFromWorkspace(stresstesting.MantidStressTest):
  '''This test should exactly match the test above as it simply
  loads the files first and passes the workspaces on to the reduction
  '''
  def runTest(self):
    
    mono_run = Load('MAR11015.RAW','MAR11015.RAW')
    mono_ws = mono_run.workspace()
    AddSampleLog(mono_ws, 'Filename', mono_run['Filename'].value)
    white_ws = Load('MAR11060.RAW','MAR11060.RAW').workspace()
    van_run = Load('MAR11001.RAW','MAR11001.RAW')
    van_ws = van_run.workspace()
    AddSampleLog(van_ws, 'Filename', van_run['Filename'].value)

    do_reduction(mono_ws, white_ws, van_ws)

  def validate(self):
    # Need to disable checking of the Spectra-Detector map because it isn't
    # fully saved out to the nexus file; some masked detectors should be picked
    # up with by the mask values in the spectra
    self.disableChecking.append('SpectraMap')
    self.disableChecking.append('Instrument')
    return '11015.spe','DI.ReduceMonoFromFile.nxs'
    
