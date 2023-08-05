from cmath import pi
import jsonpickle
import numpy as np
import numba
from numba import jit
import scipy.io as sio

SimulationConfiguration = np.dtype([('sequence', np.unicode_, 32), ('dictionary', np.unicode_, 32), ('phaseRange', np.float32,(2,)), ('spins', np.int64), ('averageSpins', np.bool8)])

class Simulation: 
    def __init__(self, sequence, dictionary, simulationConfiguration):
        self.sequence = sequence
        self.dictionary = dictionary
        self.simulationConfiguration = simulationConfiguration

    @staticmethod
    def GenerateConfiguration(sequenceName, dictionaryName, phaseRange=(-8*np.pi, 8*np.pi), spins=1, averageSpins=False):
        config = np.empty(1,dtype=SimulationConfiguration)[0]
        config['sequence'] = sequenceName
        config['dictionary'] = dictionaryName
        config['phaseRange'] = phaseRange
        config['spins'] = spins
        config['averageSpins'] = averageSpins
        return config

    @staticmethod
    @jit(parallel=True, nopython=True)
    def ExecuteNumbaSimulation(numBeats,numTimepointsPerBeat,T1s,T2s,TRs,TEs,FAs,prepIDs,prepTimes,rrTimes,phaseValues,numberOfSpins):

        numberOfExperiments = np.int32(numTimepointsPerBeat*numBeats)         
        numberOfDictionaryEntries = len(T1s)
        FAs = FAs[0:numberOfExperiments]
        prepTimes = prepTimes/1000
        TREs = TRs-TEs        
        Mx0 = np.zeros((numberOfExperiments,numberOfDictionaryEntries,numberOfSpins))
        My0 = np.zeros((numberOfExperiments,numberOfDictionaryEntries,numberOfSpins))
        Mz0 = np.zeros((numberOfExperiments,numberOfDictionaryEntries,numberOfSpins))

        phaseValueCosines = np.cos(phaseValues)
        phaseValueSines = np.sin(phaseValues)
                            
        for dictionaryEntryNumber in numba.prange(0,numberOfDictionaryEntries):
            
            T1 = T1s[dictionaryEntryNumber]
            T2 = T2s[dictionaryEntryNumber]
        
            Mx = np.zeros(numberOfSpins)
            My = np.zeros(numberOfSpins)
            Mz = np.zeros(numberOfSpins)
            Mz[:] = 1
            
            for ibeat in range(numBeats):
                baseExperimentNumber = ibeat*numTimepointsPerBeat
                tr = TRs[baseExperimentNumber]
                te = TEs[baseExperimentNumber]
                tre = TREs[baseExperimentNumber]

                At2te = np.exp(-1*te/T2)
                At1te = np.exp(-1*te/T1)
                Bt1te = 1-At1te
                
                At2tr = np.exp(-1*tre/T2)
                At1tr = np.exp(-1*tre/T1)
                Bt1tr = 1-At1tr

                RRtime = rrTimes[ibeat]
                At2rr = np.exp(-1*RRtime/T2)
                At1rr = np.exp(-1*RRtime/T1)
                Bt1rr = 1-At1rr
                
                Preptime = prepTimes[ibeat]
                At2p = np.exp(-1*Preptime/T2)
                At1p = np.exp(-1*Preptime/T1)
                Bt1p = 1-At1p
                
                Mx = np.multiply(Mx,At2rr)
                My = np.multiply(My,At2rr)
                Mz = np.multiply(Mz,At1rr)+Bt1rr
                    
                if prepIDs[ibeat] == 1:
                    My = -My
                    Mz = -Mz
                    Mx = np.multiply(Mx,At2p)
                    My = np.multiply(My,At2p)
                    Mz = np.multiply(Mz,At1p)+Bt1p
                    Mxi = Mx
                    Myi = My
                    Mx = np.multiply(phaseValueCosines,Mxi) - np.multiply(phaseValueSines,Myi)
                    My = np.multiply(phaseValueSines,Mxi) + np.multiply(phaseValueCosines,Myi)
                    
                elif prepIDs[ibeat] == 2:
                    Myi = My
                    Mzi = Mz
                    My = -Mzi
                    Mz = Myi
                    Mx = np.multiply(Mx,At2p)
                    My = np.multiply(My,At2p)
                    Mz = np.multiply(Mz,At1p)+Bt1p
                    Myi = My
                    Mzi = Mz
                    My = Mzi
                    Mz = -Myi
                    Mxi = Mx
                    Myi = My
                    Mx = np.multiply(phaseValueCosines,Mxi) - np.multiply(phaseValueSines,Myi)
                    My = np.multiply(phaseValueSines,Mxi) + np.multiply(phaseValueCosines,Myi)
                    
                for timepointNumber in range(numTimepointsPerBeat):
                    experimentNumber = baseExperimentNumber+timepointNumber
                    crf = np.cos(FAs[experimentNumber])
                    srf = np.sin(FAs[experimentNumber])
                    Myi = My
                    Mzi = Mz
                    My = np.multiply(crf,Myi)-np.multiply(srf,Mzi)
                    Mz = np.multiply(srf,Myi)+np.multiply(crf,Mzi)
                    Mx = np.multiply(Mx,At2te)
                    My = np.multiply(My,At2te)
                    Mz = np.multiply(Mz,At1te)+Bt1te
                    Mx0[experimentNumber,dictionaryEntryNumber,:]=Mx[:]
                    My0[experimentNumber,dictionaryEntryNumber,:]=My[:]
                    Mz0[experimentNumber,dictionaryEntryNumber,:]=Mz[:]
                    Mx = Mx*At2tr
                    My = My*At2tr
                    Mz = Mz*At1tr+Bt1tr
                    Mxi = Mx
                    Myi = My
                    Mx = np.multiply(phaseValueCosines,Mxi) - np.multiply(phaseValueSines,Myi)
                    My = np.multiply(phaseValueSines,Mxi) + np.multiply(phaseValueCosines,Myi)
        return Mx0,My0,Mz0
        
    @staticmethod
    @jit(parallel=True, nopython=True)
    def ParallizedMeans(Mx0,My0,Mz0):
        MeansXo = np.zeros((np.shape(Mx0)[0],np.shape(Mx0)[1]))
        MeansYo = np.zeros((np.shape(Mx0)[0],np.shape(Mx0)[1]))
        MeansZo = np.zeros((np.shape(Mx0)[0],np.shape(Mx0)[1]))

        for n in numba.prange(np.shape(Mx0)[1]):
            for timepoint in range(np.shape(Mx0)[0]):
                MeansXo[timepoint,n] = np.mean(Mx0[timepoint,n,:])
                MeansYo[timepoint,n] = np.mean(My0[timepoint,n,:])
                MeansZo[timepoint,n] = np.mean(Mz0[timepoint,n,:])
        return MeansXo, MeansYo, MeansZo

    def Execute(self, numBeats=-1, numTimepointsPerBeat=-1):
        if(numBeats == -1):
            numBeats = len(self.sequence.beats)
        if(numTimepointsPerBeat == -1):
            numTimepointsPerBeat = int(len(self.sequence.timepoints)/numBeats)

        TRs = []
        TEs = []
        FAs = []
        prepIDs = []
        prepTimes = []
        rrTimes = []
        T1s= []
        T2s = []
        B1s = []

        for dictionaryEntry in self.dictionary.entries:
            T1s.append(dictionaryEntry['T1'])
            T2s.append(dictionaryEntry['T2'])
            B1s.append(dictionaryEntry['B1'])

        for timepoint in self.sequence.timepoints:
            TRs.append(timepoint['TR'])
            TEs.append(timepoint['TE'])
            FAs.append(timepoint['FA'])

        for beat in self.sequence.beats:
            prepIDs.append(beat['PrepID'])
            prepTimes.append(beat['PrepTime'])
            rrTimes.append(beat['RRTime'])
    
        phaseValues = np.linspace(-self.simulationConfiguration['phaseRange'][0]/2,self.simulationConfiguration['phaseRange'][1]/2,self.simulationConfiguration['spins'])

        Mx0,My0,Mz0 = self.ExecuteNumbaSimulation(numTimepointsPerBeat,numBeats,np.asarray(T1s),np.asarray(T2s),np.asarray(TRs),np.asarray(TEs),np.asarray(FAs),np.asarray(prepIDs),np.asarray(prepTimes),np.asarray(rrTimes),phaseValues,self.simulationConfiguration['spins'])
       
        if(self.simulationConfiguration['averageSpins']):
            simulationResults = self.ParallizedMeans(Mx0,My0,Mz0)
        else:
            simulationResults = (Mx0, My0, Mz0)
        
        return simulationResults


