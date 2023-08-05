from cmath import pi
import jsonpickle
import numpy as np
import numba
from numba import jit
import scipy.io as sio
import h5py

DictionaryEntry = np.dtype([('T1', np.float32), ('T2', np.float32), ('B1', np.float32)])

class Dictionary:
    def __init__(self, name, entries=[]):
        self.name = name
        self.entries = entries

    def __str__(self):
        return "(" + str(len(self.entries)) + ")"

    def Initialize(self, T1s, T2s, B1s=[]):
        self.entries = np.empty(len(T1s), dtype=DictionaryEntry)
        if (len(T1s)!=len(T2s)):
            print("Import Failed: T1/T2 files must have identical number of entries")
            return 
        for index in range(len(T1s)):
            if(B1s != []):
                for b1Index in range(len(B1s)):
                    self.entries[index] = (T1s[index], T2s[index], B1s[b1Index])
            else:
                self.entries[index] = (T1s[index], T2s[index], None)
        print(self.name + " || Populated " + str(len(self.entries)) + " entries")

    def ImportFromTxt(self, T1Filepath, T2Filepath, B1Filepath=""):
        T1s = np.loadtxt(T1Filepath)
        T2s = np.loadtxt(T2Filepath)
        if(B1Filepath != ""):
            B1s = np.loadtxt(B1Filepath)
            self.Initialize(T1s, T2s, B1s)
        else:
            self.Initialize(T1s,T2s)
            
    def PopulateFromPercent(self, t1Range=(100,4000), t2Range=(1,400), percentStepSize=5, includeB1=False, b1Range=(0.5,1.5), b1Stepsize=0.05):
        T1s = []
        T2s = []
        t1 = t1Range[0]
        t2 = t2Range[0]
        while t1 <= t1Range[1]:
            T1s.append(t1/1000)
            t1 = t1*(1+(percentStepSize/100))
        while t2 <= t2Range[1]:
            T2s.append(t2/1000)
            t2 = t2*(1+(percentStepSize/100))
        pairs = []
        for t1Val in T1s:
            for t2Val in T2s:
                if(t1Val>t2Val): # Don't include pairs with T2 longer than T1
                    pairs.append((t1Val,t2Val))
        T1sFromPairs = []
        T2sFromPairs = []
        for pair in pairs:
            T1sFromPairs.append(pair[0])
            T2sFromPairs.append(pair[1])
        if(includeB1):
            B1s = np.arange(b1Range[0], b1Range[1], b1Stepsize)
            self.Initialize(T1sFromPairs,T2sFromPairs, B1s)
        else:
            self.Initialize(T1sFromPairs, T2sFromPairs)

    def PopulateFromFixedStep(self, t1Range=(100,4000), t2Range=(1,400), fixedStepSize=1, includeB1=False, b1Range=(0.5,1.5), b1Stepsize=0.05):
        T1s = []
        T2s = []
        t1 = t1Range[0]
        t2 = t2Range[0]
        while t1 <= t1Range[1]:
            T1s.append(t1/1000)
            t1 = t1+fixedStepSize
        while t2 <= t2Range[1]:
            T2s.append(t2/1000)
            t2 = t2+fixedStepSize
        pairs = []
        for t1Val in T1s:
            for t2Val in T2s:
                if(t1Val>t2Val): # Don't include pairs with T2 longer than T1
                    pairs.append((t1Val,t2Val))
        T1sFromPairs = []
        T2sFromPairs = []
        for pair in pairs:
            T1sFromPairs.append(pair[0])
            T2sFromPairs.append(pair[1])
        if(includeB1):
            B1s = np.arange(b1Range[0], b1Range[1], b1Stepsize)
            self.Initialize(T1sFromPairs,T2sFromPairs, B1s)
        else:
            self.Initialize(T1sFromPairs, T2sFromPairs)

    def SaveToTxtFiles(self, includeB1=False):
        t1File = open(self.name+"_T1s.txt","w")
        t2File = open(self.name+"_T2s.txt","w")
        for entry in self.entries:
            t1File.write(f'{entry["T1"]:7.5f}'+"\n")
            t2File.write(f'{entry["T2"]:7.5f}'+"\n") 
        if(includeB1):
            b1File = open(self.name+"_B1s.txt","w")
            for entry in self.entries:
                b1File.write(f'{entry["B1"]:7.5f}'+"\n") 
    
    def Export(self, filename, force=False):
        if ".mrf" in filename:
            outfile = h5py.File(filename, "a")
            try:
                dictionariesGroup = outfile.create_group("dictionaries")
            except:
                print("Dictionary group already exists. Appending.") 
            if (self.name in list(outfile["dictionaries"].keys())) and not force:
                print("Dictionary already exists in .mrf file. Specify 'force' to overwrite")
            else:
                dictionary = dictionariesGroup.create_group(self.name)
                timepointDataset = dictionary.create_dataset("entries",shape=len(self.entries), dtype=DictionaryEntry)
                timepointDataset.write_direct(self.entries)
                outfile.close()
        else:
            print("Input is not a .mrf file")

    @staticmethod
    def Import(filename, dictionaryName):
        if ".mrf" in filename:
            infile = h5py.File(filename, "r")
            dictionaryGroup = infile["dictionaries"][dictionaryName]
            new_dictionary = Dictionary(dictionaryName, dictionaryGroup["entries"][:])
            infile.close()
            return new_dictionary
        else:
            print("Input is not a .mrf file")
    
    @staticmethod
    def GetAvailableDictionaries(filename):
        if ".mrf" in filename:
            infile = h5py.File(filename, "r")
            return list(infile["dictionaries"].keys())
        else:
            print("Input is not a .mrf file")