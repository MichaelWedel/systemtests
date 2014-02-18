from stresstesting import MantidStressTest
#from mantid.simpleapi import MaskDetectors, mtd, config
from mantid.simpleapi import *
import DirectEnergyConversion as reduction
from mantid.kernel import PropertyManager
import os

class DirectInelasticDiagnostic(MantidStressTest):
    
    def runTest(self):
        white = 'MAP17186.raw'
        sample = 'MAP17269.raw'
        
        # Libisis values to check against
        tiny=1e-10
        huge=1e10

        v_out_lo = 0.01
        v_out_hi = 100.

        vv_lo = 0.1
        vv_hi = 2.0
        vv_sig = 0.0
        
        sv_sig = 3.3
        sv_hi = 1.5
        sv_lo = 0.0
        s_zero = True
        
        reducer = reduction.setup_reducer('MAPS')
        # parameters which explicitly affect diagnostics
        #
        reducer.wb_integr_range = [20,300]
        reducer.bkgd_range=[12000,18000]
        diag_mask = reducer.diagnose(white, sample=sample, tiny=tiny, huge=huge, 
                                     van_out_lo=v_out_lo, van_out_hi=v_out_hi,
                                     van_lo=vv_lo, van_hi=vv_hi, van_sig=vv_sig,
                                     samp_lo=sv_lo, samp_hi=sv_hi, samp_sig=sv_sig, samp_zero=s_zero,hard_mask_file=None)
 
        sample_ws = mtd[sample]	
        MaskDetectors(Workspace=sample_ws, MaskedWorkspace=diag_mask)

        # Save the masked spectra nmubers to a simple ASCII file for comparison
        self.saved_diag_file = os.path.join(config['defaultsave.directory'], 'CurrentDirectInelasticDiag.txt')
        handle = file(self.saved_diag_file, 'w')
        for index in range(sample_ws.getNumberHistograms()):
            if sample_ws.getDetector(index).isMasked():
                spec_no = sample_ws.getSpectrum(index).getSpectrumNo()
                handle.write(str(spec_no) + '\n')
        handle.close
        
    def cleanup(self):
        if os.path.exists(self.saved_diag_file):
            if self.succeeded():
                os.remove(self.saved_diag_file)
            else:
                os.rename(self.saved_diag_file, os.path.join(config['defaultsave.directory'], 'DirectInelasticDiag-Mismatch.txt'))
        
    def validateMethod(self):
        return 'validateASCII'
        
    def validate(self):
        return self.saved_diag_file, \
            os.path.join(os.path.dirname(__file__), 'ReferenceResults','DirectInelasticDiagnostic.txt')


class DirectInelasticDiagnosticSNS(MantidStressTest):
    
    def runTest(self):
        red_man = PropertyManager()
        red_man_name = "__dgs_reduction_properties"
        pmds[red_man_name] = red_man
              
    
        white = 'MAP17186.raw'
        sample = 'MAP17269.raw'
    
        detvan = Load(white)
        sample = Load(sample)
        
            
        # Libisis values to check against       

        sv_lo = 0.0
      # Libisis values to check against
        # All PropertyManager properties need to be set
        red_man["LowCounts"] = 1e-10   #     tiny=1e-10
        red_man["HighCounts"] = 1e10   #     huge=1e10
        red_man["LowOutlier"] = 0.01   #     v_out_lo = 0.01
        red_man["HighOutlier"] = 100.  #     v_out_hi = 100.
        red_man["ErrorBarCriterion"] = 0.0    #  ?
        red_man["MedianTestLow"] = 0.1        #    vv_lo = 0.1
        red_man["MedianTestHigh"] = 2.0       #    vv_hi = 2.0
        red_man["SamBkgMedianTestLow"] = 0.0  #   vv_sig = 0.0
        red_man["SamBkgMedianTestHigh"] = 1.5  #          sv_hi = 1.5 
        red_man["SamBkgErrorbarCriterion"] = 3.3 #          sv_sig = 3.3
        red_man["RejectZeroBackground"] = True   #         s_zero = True
        # Things needed to run vanadium reduction
        red_man["IncidentBeamNormalisation"] = "ToMonitor"
        red_man["DetVanIntRangeUnits"] = "Energy"
        #  properties affecting diagnostics:

        #reducer.wb_integr_range = [20,300]
        red_man["DetVanIntRangeLow"] = 20.
        red_man["DetVanIntRangeHigh"] = 300.
        red_man["BackgroundCheck"] = True
        red_man["BackgroundTofStart"]=12000.
        red_man["BackgroundTofEnd"]=18000.
        #reducer.bkgd_range=[12000,18000]


        diag_mask = DgsDiagnose(DetVanWorkspace=detvan, SampleWorkspace=sample,
                                ReductionProperties=red_man_name)
   
        MaskDetectors(sample, MaskedWorkspace=diag_mask)       

        # Save the masked spectra nmubers to a simple ASCII file for comparison
        self.saved_diag_file = os.path.join(config['defaultsave.directory'], 'CurrentDirectInelasticDiag.txt')
        handle = file(self.saved_diag_file, 'w')
        for index in range(sample.getNumberHistograms()):
            if sample.getDetector(index).isMasked():
                spec_no = sample.getSpectrum(index).getSpectrumNo()
                handle.write(str(spec_no) + '\n')
        handle.close
        
    def cleanup(self):
        if os.path.exists(self.saved_diag_file):
            if self.succeeded():
                os.remove(self.saved_diag_file)
            else:
                os.rename(self.saved_diag_file, os.path.join(config['defaultsave.directory'], 'DirectInelasticDiag-Mismatch.txt'))
        
    def validateMethod(self):
        return 'validateASCII'
        
    def validate(self):
        return self.saved_diag_file, \
            os.path.join(os.path.dirname(__file__), 'ReferenceResults','DirectInelasticDiagnostic.txt')
