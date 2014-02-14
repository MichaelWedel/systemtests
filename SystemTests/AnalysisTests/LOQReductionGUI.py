import stresstesting
from mantid.simpleapi import * 
import isis_reducer
import ISISCommandInterface as i
import isis_instrument
import isis_reduction_steps

MASKFILE = FileFinder.getFullPath('MaskLOQData.txt')
BATCHFILE = FileFinder.getFullPath('loq_batch_mode_reduction.csv')

class LOQMinimalBatchReduction(stresstesting.MantidStressTest):
    def __init__(self):
        super(LOQMinimalBatchReduction, self).__init__()
        config['default.instrument'] = 'LOQ'

    def runTest(self):
        import SANSBatchMode as batch
        i.LOQ()
        i.MaskFile(MASKFILE)
        fit_settings = batch.BatchReduce(BATCHFILE, '.nxs', combineDet='merged', saveAlgs={})

    def validate(self):
        self.tolerance = 1.0e-5
        return 'first_time_merged', 'LOQReductionMergedData.nxs'
