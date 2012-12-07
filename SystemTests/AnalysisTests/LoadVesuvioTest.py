import stresstesting

from mantid.api import MatrixWorkspace, mtd
from mantid.simpleapi import LoadVesuvio

import unittest

DIFF_PLACES = 12

class VesuvioTests(unittest.TestCase):
    
    ws_name = "evs_raw"


    def tearDown(self):
        if self.ws_name in mtd:
            mtd.remove(self.ws_name)

    #================== Success cases ================================
    def test_load_with_back_scattering_spectra_produces_correct_workspace(self):
        self._run_load("14188", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(843675.4580568932, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(154711.85462469794, evs_raw.readY(131)[1188], places=DIFF_PLACES)

    def test_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(11669506.890067935, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(2906821.9049028009, evs_raw.readY(131)[1188], places=DIFF_PLACES)

    def test_non_consecutive_runs_with_back_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "3-134", "Double")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(7049905.3576081544, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-935544.50673137605, evs_raw.readY(131)[1188], places=DIFF_PLACES)

    def test_load_with_forward_scattering_spectra_produces_correct_workspace(self):
        self._run_load("14188", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-7874182.0009550452, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-244186.74077558052, evs_raw.readY(63)[1188], places=DIFF_PLACES)

    def test_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188-14190", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-56441823.199241638, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(-41421.057527974248, evs_raw.readY(63)[1188], places=DIFF_PLACES)

    def test_non_consecutive_runs_with_forward_scattering_spectra_gives_expected_numbers(self):
        self._run_load("14188,14190", "135-198", "Single")

        # Check some data
        evs_raw = mtd[self.ws_name]
        self.assertAlmostEqual(-25611027.229559898, evs_raw.readY(0)[1], places=DIFF_PLACES)
        self.assertAlmostEqual(43777.688780918717, evs_raw.readY(63)[1188], places=DIFF_PLACES)

    def test_using_ip_file_adjusts_instrument_and_attaches_parameters(self):
        self._run_load("14188", "3", "Single","IP0005.dat")
        
        # Check some data
        evs_raw = mtd[self.ws_name]
        det0 = evs_raw.getDetector(0)
        param = det0.getNumberParameter("t0")
        self.assertEqual(1, len(param))
        self.assertAlmostEqual(-0.4157, param[0],places=4)

    def _run_load(self, runs, spectra, diff_opt, ip_file=""):
        LoadVesuvio(RunNumbers=runs,OutputWorkspace=self.ws_name,
            SpectrumList=spectra,DifferenceType=diff_opt,InstrumentParFile=ip_file)

        self._do_ads_check(self.ws_name)

        def to_min_max(str_param):
            if "-" in str_param:
                elements = str_param.split("-")
                return (int(elements[0]), int(elements[1]))
            else:
                return (int(str_param), int(str_param))

        min,max = to_min_max(spectra)
        expected_size = max - min + 1
        self._do_size_check(self.ws_name, expected_size)

    def _do_ads_check(self, name):
        self.assertTrue(name in mtd)
        self.assertTrue(type(mtd[name]) == MatrixWorkspace)

    def _do_size_check(self,name, expected_nhist):
        loaded_data = mtd[name]
        self.assertEquals(expected_nhist, loaded_data.getNumberHistograms())
        
    #================== Failure cases ================================

    def test_missing_spectra_property_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name)
        
    def test_load_with_invalid_spectra_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="200")

    def test_load_with_spectra_mixed_from_forward_backward_raises_error(self):
        # Everything
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="3-198")
        # Smaller range
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="125-180")
        
        # Just two
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                  OutputWorkspace=self.ws_name, SpectrumList="134,135")
        
    def test_load_with_spectra_that_are_just_monitors_raises_error(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, SpectrumList="1")
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188",
                          OutputWorkspace=self.ws_name, SpectrumList="1-2")
        
    def test_load_with_invalid_difference_option_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, DifferenceType="Unknown",SpectrumList="3-134")

    def test_load_with_difference_option_not_applicable_to_current_spectra_raises_error(self):
        self.assertRaises(ValueError, LoadVesuvio, RunNumbers="14188",
          OutputWorkspace=self.ws_name, DifferenceType="",SpectrumList="3-134")

    def test_raising_error_removes_temporary_raw_workspaces(self):
        self.assertRaises(RuntimeError, LoadVesuvio, RunNumbers="14188,14199", # Second run is invalid
          OutputWorkspace=self.ws_name, DifferenceType="Single",SpectrumList="3-134")

        self._do_test_temp_raw_workspaces_not_left_around()

    def _do_test_temp_raw_workspaces_not_left_around(self):
        self.assertTrue("__loadraw_evs" not in mtd) 
        self.assertTrue("__loadraw_evs_monitors" not in mtd)


#====================================================================================

class LoadVesuvioTest(stresstesting.MantidStressTest):

    def runTest(self):
        self._success = False
        # Custom code to create and run this single test suite
        suite = unittest.TestSuite()
        suite.addTest( unittest.makeSuite(VesuvioTests, "test") )
        runner = unittest.TextTestRunner()
        # Run using either runner
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True 
        else:
            self._success = False

    def validate(self):
        return self._success
