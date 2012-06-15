"""
These system tests are to verify the behaviour of the ISIS reflectometry reduction scripts
"""

import stresstesting
from mantidsimple import *

class ReflectometryISIS(stresstesting.MantidStressTest):

    def runTest(self):
        
        PIX=1.1E-3 #m
        SC=75
        avgDB=29
        
        Load(Filename='POLREF00004699.nxs',OutputWorkspace='POLREF00004699')
        X=mtd['POLREF00004699']
        ConvertUnits(InputWorkspace=X,OutputWorkspace=X,Target="Wavelength",AlignBins="1")
        # Reference intensity to normalise by
        CropWorkspace(InputWorkspace=X,OutputWorkspace='Io',XMin=0.8,XMax=14.5,StartWorkspaceIndex=2,EndWorkspaceIndex=2)
        # Crop out transmission and noisy data 
        CropWorkspace(InputWorkspace=X,OutputWorkspace='D',XMin=0.8,XMax=14.5,StartWorkspaceIndex=3)
        Io=mtd['Io']
        D=mtd['D']
    
        # Peform the normaisation step
        Divide(D,Io,'I','1','1')
        I=mtd['I'][0]
        
        # Automatically determine the SC and averageDB 
        FindReflectometryLines(InputWorkspace=I, StartWavelength=10, OutputWorkspace='spectrum_numbers')
        spectrum_table = mtd['spectrum_numbers']
        self.assertTrue(2 == spectrum_table.columnCount())
        self.assertTrue(1 == spectrum_table.rowCount())
        self.assertTrue(avgDB == spectrum_table.cell(0, 0)) #Check that the algorithm found the expected answer for the reflected line
        self.assertTrue(SC == spectrum_table.cell(0, 1)) #Check that the algorithm found the expected answer for the transmisson line
        
        # Move the detector so that the detector channel matching the reflected beam is at 0,0
        MoveInstrumentComponent(Workspace=I,ComponentName="lineardetector",X=0,Y=0,Z=-PIX*( (SC-avgDB)/2.0 +avgDB) )
        
        # Should now have signed theta vs Lambda
        ConvertSpectrumAxis(InputWorkspace=I,OutputWorkspace='SignedTheta_vs_Wavelength',Target='signed_theta')
        
        # Check that signed two theta is being caluclated correctly (not normalised)
        ws1 = mtd['SignedTheta_vs_Wavelength']
        upperHistogram = ws1.getNumberHistograms()-1
        for i in range(0, upperHistogram):
            thisTheta = ws1.detectorSignedTwoTheta(ws1.getDetector(i))
            nextTheta = ws1.detectorSignedTwoTheta(ws1.getDetector(i+1)) 
            #This check would fail if negative values were being normalised.
            self.assertTrue(thisTheta < nextTheta)
        
        # MD transformations
        ConvertToReflectometryQ(InputWorkspace='SignedTheta_vs_Wavelength',OutputWorkspace='QxQy',OutputDimensions='Q (lab frame)', Extents='-0.0005,0.0005,0,0.12')
        ConvertToReflectometryQ(InputWorkspace='SignedTheta_vs_Wavelength',OutputWorkspace='KiKf',OutputDimensions='K (incident, final)', Extents='0,0.05,0,0.05')
        ConvertToReflectometryQ(InputWorkspace='SignedTheta_vs_Wavelength',OutputWorkspace='PiPf',OutputDimensions='P (lab frame)', Extents='0,0.1,-0.02,0.15')
        
        # Bin the outputs to histograms because observations are not important.
        BinMD(InputWorkspace='QxQy',AxisAligned='0',BasisVector0='Qx,(Ang^-1),1,0',BasisVector1='Qz,(Ang^-1),0,1',OutputExtents='-0.0005,0.0005,0,0.12',OutputBins='100,100',Parallel='1',OutputWorkspace='QxQy_rebinned')
        BinMD(InputWorkspace='KiKf',AxisAligned='0',BasisVector0='Ki,(Ang^-1),1,0',BasisVector1='Kf,(Ang^-1),0,1',OutputExtents='0,0.05,0,0.05',OutputBins='200,200',Parallel='1',OutputWorkspace='KiKf_rebinned')
        BinMD(InputWorkspace='PiPf',AxisAligned='0',BasisVector0='Pz_i + Pz_f,(Ang^-1),1,0',BasisVector1='Pz_i - Pz_f,(Ang^-1),0,1',OutputExtents='0,0.1,-0.02,0.15',OutputBins='50,50',Parallel='1',OutputWorkspace='PiPf_rebinned')
        
        # Fetch benchmarks for testing against
        LoadMD(Filename="POLREF_qxqy_benchmark.nxs", OutputWorkspace="QxQy_benchmark")
        LoadMD(Filename="POLREF_kikf_benchmark.nxs", OutputWorkspace="KiKf_benchmark")
        LoadMD(Filename="POLREF_pipf_benchmark.nxs", OutputWorkspace="PiPf_benchmark")
        
        # Check the outputs
        qxqy_comparison = CompareMDWorkspaces(Workspace1='QxQy_rebinned',Workspace2='QxQy_benchmark', Tolerance=0.01, CheckEvents=False)
        kikf_comparison = CompareMDWorkspaces(Workspace1='KiKf_rebinned',Workspace2='KiKf_benchmark', Tolerance=0.01, CheckEvents=False)
        pipf_comparison = CompareMDWorkspaces(Workspace1='PiPf_rebinned',Workspace2='PiPf_benchmark', Tolerance=0.01, CheckEvents=False)
        
        # Assert against the outputs
        self.assertTrue(int(qxqy_comparison.getPropertyValue("Equals")) == 1)
        self.assertTrue(int(kikf_comparison.getPropertyValue("Equals")) == 1)
        self.assertTrue(int(pipf_comparison.getPropertyValue("Equals")) == 1)
        
        return True;
        
    def doValidate(self):
        return True;
    