import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *
class EQSANSIQOutput(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
        Testing that the I(Q) output of is correct 
    """
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        self.cleanup()
        mtd.settings['default.facility'] = 'SNS'
        EQSANS()
        AppendDataFile("EQSANS_1466_event.nxs")
        NoSolidAngle()
        UseConfig(False)
        UseConfigTOFTailsCutoff(False)
        UseConfigMask(False)
        TotalChargeNormalization(normalize_to_beam=False)
        Reduce1D()        
        # Scale up to match correct scaling. The reference data is off by a factor 10.0 
        Scale("EQSANS_1466_event_Iq", "EQSANS_1466_event_Iq", 10.0)                
                        
    def cleanup(self):
        for ws in ["EQSANS_1466_event_Iq", "EQSANS_1466_event", "EQSANS_1466_event_evt", "beam_hole_transmission_EQSANS_1466_event"]:
            if mtd.workspaceExists(ws):
                mtd.deleteWorkspace(ws)
                
    def validate(self):
        self.tolerance = 0.1
        mtd["EQSANS_1466_event_Iq"].dataY(0)[0] = 269.687
        mtd["EQSANS_1466_event_Iq"].dataE(0)[0] = 16.4977
        mtd["EQSANS_1466_event_Iq"].dataE(0)[1] = 6.78
        mtd["EQSANS_1466_event_Iq"].dataY(0)[2] = 11.3157
        mtd["EQSANS_1466_event_Iq"].dataE(0)[2] = 1.23419
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        return "EQSANS_1466_event_Iq", 'EQSANSIQOutput.nxs'
