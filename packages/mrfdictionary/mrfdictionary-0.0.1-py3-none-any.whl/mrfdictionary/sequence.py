from cmath import pi
import json
import jsonpickle
from json import JSONEncoder
import pickle
import numpy as np
import numba
from numba import jit
import scipy.io as sio
import h5py

Timepoint = np.dtype([('TR', np.float32), ('TE', np.float32), ('FA', np.float32)])
Beat = np.dtype([('RRTime', np.float32), ('PrepTime', np.float32), ('PrepID', np.float32)])

class Sequence:

    def __init__(self, name, timepoints=[], beats=[]):
        self.name = name
        self.timepoints = timepoints
        self.beats = beats

    def __str__(self):
        return "(" + str(self.timepoints) + ", " + str(self.beats) + ")"

    def Initialize(self, TRs, TEs, FAs, rrTimes, prepTimes, prepIDs):
        self.timepoints = np.empty(len(TRs), dtype=Timepoint)
        if (len(TRs)!=len(TEs)) or (len(TRs)!=len(FAs)):
            print("Import Failed: TR/TE/FA files must have identical number of entries")
            return 
        for index in range(len(TRs)):
            self.timepoints[index] = (TRs[index], TEs[index], FAs[index])
        self.beats = np.empty(len(rrTimes), dtype=Beat)
        if (len(rrTimes)!=len(prepTimes)) or (len(rrTimes)!=len(prepIDs)):
            print("Import Failed: RRTime/PrepTime/PrepID files must have identical number of entries")
            return 
        for index in range(len(rrTimes)):
            self.beats[index] = (rrTimes[index], prepTimes[index], prepIDs[index])
        print(self.name + " || Initialized " + str(len(self.timepoints)) + " timepoint definitions and " + str(len(self.beats)) + " beat definitions")

    def ImportFromTxt(self, trFilepath, teFilepath, faFilepath, rrTimeFilepath, prepTimeFilepath, prepIDFilepath):
        TRs = np.loadtxt(trFilepath)
        TEs = np.loadtxt(teFilepath)
        FAs = np.loadtxt(faFilepath)
        rrTimes = np.loadtxt(rrTimeFilepath)
        prepTimes = np.loadtxt(prepTimeFilepath)
        prepIDs = np.loadtxt(prepIDFilepath)
        self.Initialize(TRs, TEs, FAs, rrTimes, prepTimes, prepIDs)

    def Export(self, filename, force=False):
        if ".mrf" in filename:
            outfile = h5py.File(filename, "a")
            try:
                sequencesGroup = outfile.create_group("sequences")
            except:
                print("Sequences group already exists. Appending.") 
            if (self.name in list(outfile["sequences"].keys())) and not force:
                print("Sequence already exists in .mrf file. Specify 'force' to overwrite")
            else:
                sequence = sequencesGroup.create_group(self.name)
                timepointDataset = sequence.create_dataset("timepoints",shape=len(self.timepoints), dtype=Timepoint)
                timepointDataset.write_direct(self.timepoints)
                beatDataset = sequence.create_dataset("beats",shape=len(self.beats), dtype=Beat)
                beatDataset.write_direct(self.beats)           
                outfile.close()
        else:
            print("Input is not a .mrf file")

    @staticmethod
    def Import(filename, sequenceName):
        if ".mrf" in filename:
            infile = h5py.File(filename, "r")
            sequenceGroup = infile["sequences"][sequenceName]
            new_sequence = Sequence(sequenceName, sequenceGroup["timepoints"][:], sequenceGroup["beats"][:])
            infile.close()
            return new_sequence
        else:
            print("Input is not a .mrf file")
    
    @staticmethod
    def GetAvailableSequences(filename):
        if ".mrf" in filename:
            infile = h5py.File(filename, "r")
            return list(infile["sequences"].keys())
        else:
            print("Input is not a .mrf file")