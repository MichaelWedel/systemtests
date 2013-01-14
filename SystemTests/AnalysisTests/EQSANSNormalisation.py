import stresstesting
from MantidFramework import *
mtd.initialise(False)
from mantidsimple import *
from reduction.instruments.sans.sns_command_interface import *
import os

class EQSANSNormalisationNoFlux(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, 
                   PreserveEvents=False, LoadMonitors=False)
        EQSANSNormalise(InputWorkspace=ws, NormaliseToBeam=False)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_no_flux")
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_no_flux", 'EQSANSNormalisation_NoFlux.nxs'

class EQSANSNormalisationDefault(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, 
                   PreserveEvents=False, LoadMonitors=False)
        EQSANSNormalise(InputWorkspace=ws,NormaliseToBeam=True)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_default_flux")
        
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_default_flux", 'EQSANSNormalisation_DefaultFlux.nxs'
    
class EQSANSNormalisationInputFlux(stresstesting.MantidStressTest):
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
        mtd.settings['default.facility'] = 'SNS'
        ws = "__eqsans_normalisation_test"
        
        parentDir = os.path.abspath('..')
        spectrum_file = os.path.join(parentDir, "Data", "eqsans_beam_flux.txt")
        
        EQSANSLoad(Filename="EQSANS_1466_event.nxs", OutputWorkspace=ws, 
                   PreserveEvents=False, LoadMonitors=False)
        EQSANSNormalise(InputWorkspace=ws,NormaliseToBeam=True,BeamSpectrumFile=spectrum_file)
        SumSpectra(InputWorkspace=ws, OutputWorkspace="eqsans_input_flux")
  
    def validate(self):
        self.disableChecking.append('Instrument')
        self.disableChecking.append('Sample')
        self.disableChecking.append('SpectraMap')
        self.disableChecking.append('Axes')
        
        return "eqsans_input_flux", 'EQSANSNormalisation_InputFlux.nxs'

class EQSANSNormalisationBeamFlux(stresstesting.MantidStressTest):
    """
        Analysis Tests for EQSANS
    """
    
    def runTest(self):
        """
            Check that EQSANSTofStructure returns the correct workspace
        """
        # Note that the EQSANS Reducer does the transmission correction by default,
        # so we are also testing the EQSANSTransmission algorithm
        mtd.settings['default.facility'] = 'SNS'
        self.prop_mng = "eqsans_normalise_options"
        self.data_ws = "eqsans_normalise_data_ws"

        EQSANSLoad(Filename="EQSANS_3293_event.nxs",
                   NoBeamCenter=True,
                   ReductionProperties=self.prop_mng,
                   OutputWorkspace=self.data_ws)
        
        EQSANSNormalise(InputWorkspace=self.data_ws,
                        BeamSpectrumFile='SANSBeamFluxCorrectionMonitor.nxs',
                        NormaliseToMonitor=True,
                        ReductionProperties=self.prop_mng)

    def validate(self):
        ref_values = [9.66631788e-08, 1.99540011e-08, 0.00000000e+00, 2.84897084e-08,
                      2.58802935e-08, 0.00000000e+00, 3.43023370e-08, 1.11017160e-08,
                      3.22199520e-08, 8.31598470e-08, 3.05866692e-08, 3.00540473e-08,
                      2.97218143e-08, 5.92981344e-08, 2.92735276e-08, 1.91616696e-08,
                      4.63637972e-08, 8.94602703e-09, 4.34305480e-08, 1.71487695e-08,
                      2.51816301e-08, 3.24283000e-08, 2.40811371e-08, 3.20081242e-08,
                      8.03994116e-09, 3.23002602e-08, 2.43204630e-08, 7.99166600e-09,
                      2.40009985e-08, 8.04082934e-09, 1.61818559e-08, 2.44975746e-08,
                      0.00000000e+00, 2.49096583e-08, 0.00000000e+00, 8.48764614e-09,
                      8.59073435e-09, 0.00000000e+00, 8.77853612e-09, 0.00000000e+00,
                      3.69158961e-08, 2.16789982e-08, 1.41834793e-08]
   
        output_y = mtd[self.data_ws].readY(0)
        if output_y[0]-ref_values[0] > 0.000006:
            return False
        if output_y[5]-ref_values[5] > 0.000006:
            return False
        if output_y[10]-ref_values[10] > 0.000006:
            return False
        if output_y[25]-ref_values[25] > 0.000006:
            return False
        
        return True

