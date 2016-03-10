#!/usr/bin/env python
"""
Making combined ntuple with qie8 and qie10 signals
# -*- coding: UTF-8 -*-
"""

import sys, os
import math
#from ROOT import *
import ROOT
sys.path.append("../Common")
from utils import *
import numpy as np


#Output Ntuple
    #Double_t depth8;\
    #Double_t depth10;\
ROOT.gROOT.ProcessLine(\
"struct Qie8and10{\
    Double_t eta;\
    Double_t phi;\
    Double_t emhad;\
    Double_t nentries8;\
    Double_t fcMean8;\
    Double_t fcMean8err;\
    Double_t fcIntegral8;\
    Double_t nentries10;\
    Double_t fcMean10;\
    Double_t fcMean10err;\
    Double_t fcIntegral10;\
    };")

from ROOT import Qie8and10

files = {
    'qie8':'/afs/cern.ch/work/s/stepobr/public/264789/hcalSourceDataMon.264789.root',
    'qie10':'/afs/cern.ch/work/s/stepobr/public/264789/hcalSourceDataMon.264789_qie10.root'}

output = 'forQieRatios.root'

# HAD/EM towers from depths
emhad = {
    '1':'em',
    '3':'em',
    '2':'had',
    '4':'had'
}

emhadId = {
    'em' : 1,
    'had' : 2
}

#Low edges for histos
xx = {
    'qie8': np.array([-3.0,-0.4,2.2,4.8,7.4,10.0,12.6,15.2,17.8,20.4,23.0,25.6,28.2,30.8,33.4,36.0,41.2,46.4,51.6,
        56.8,62.0,67.2,72.4,80.2,88.0,95.8,103.6,114.0,124.4,134.8,147.8,160.8,173.8,
        186.8,199.8,212.8,225.8,238.8,251.8,264.8,277.8,290.8,303.8,316.8,329.8,342.8,368.8,394.8,420.8,
        446.8,472.8,498.8,524.8,563.8,602.8,641.8,680.8,732.8,784.8,836.8,901.8,966.8,1031.8 ]),
    'qie10': np.array([-16.0,-12.9,-9.8,-6.7,-3.6,-0.5,2.6,5.7,8.8,11.9,15.0,18.1,21.2,24.3,27.4,30.5,33.6,39.8,46.0,52.2,58.4,64.6,70.8,
                77.0,83.2,89.4,95.6,101.8,108.0,114.2,120.4,126.6,132.8,139.0,145.2,151.4,157.6,170.0,182.4,194.8,207.2,219.6,232.0,
                244.4,256.8,269.2,281.6,294.0,306.4,318.8,331.2,343.6,356.0,368.4,380.8,393.2,405.6,418.0,442.8,467.6,492.4,517.2,
                542.0,566.8,591.6,])
}

#Limits for histogram
xLowHigh = {
    'qie8': (23., 563.8), 
    'qie10': (24.3, 566.8)
}

deltaReel = 200  # Making sure that we are within absorber
deltaHad = 300   # Hadron fibers are 30 cm shorter

def specialEtas(key, eta, phi, depth) :
    if eta == 30 or  eta == 34:
        if key == 'qie10' and depth == 2:
            return  1
        else:
            return 0
    else:   
        return 0
    


def main():
    
    eventData = {} # Dictionary to hold all the data

    for key in files.keys():
        h = {}
        f = ROOT.TFile(files[key])
        print "Processing", files[key]
        t = f.Get("eventTree")
        

        specialKeys = []   # Kyes for eta 30 and 34 (Both anodes go to qie10)
        fileData = {}  # Eventdata for a given file 
        
         #Loop over entries
        for i in range(0, t.GetEntries()):
            nb = t.GetEntry(i)
            if nb < 0:
                continue 

            nDepths = t.nChInEvent
            if nDepths < 1:
                #print "Zero number of depths in event, file for ", key
                continue            
            
            (hf, eta, phi) = getEtaPhiFromTube(t.tubeName)  # Eta/phi from tube name

            (reelMin, reelMax) = getReelLimits(t.tubeDescription)  # within absorber from tube description
            reelMin += deltaReel
            reelMax -= deltaReel
            
            cap0hist = np.array(t.chHistBinContentCap0, dtype=np.ushort).reshape(nDepths, 65)
            cap1hist = np.array(t.chHistBinContentCap1, dtype=np.ushort).reshape(nDepths, 65)
            cap2hist = np.array(t.chHistBinContentCap2, dtype=np.ushort).reshape(nDepths, 65)
            cap3hist = np.array(t.chHistBinContentCap3, dtype=np.ushort).reshape(nDepths, 65)
            
            for n in range(nDepths):
                if  t.detiphi[n] != phi or t.detieta[n] != eta:
                    print "Eta/phi mismatch in tubename and event"
                    continue     
                
                if t.detieta[n] == 40:    # Eta=40 shouldn't be here
                    continue
                
                if emhad[str(t.detidepth[n])] == 'had':
                    reelMax -= deltaHad
                
                if t.reelPos < reelMin and t.reelPos > reelMax:
                    continue  # outside limits
        
                eventKey = str(t.detieta[n]) + '_' + str(t.detiphi[n]) + '_' + emhad[str(t.detidepth[n])]
                
                # Book histo if not exists already
                if eventKey not in h.keys():
                    h[eventKey] = ROOT.TH1D(eventKey, eventKey, len(xx[key])-1, xx[key])
                    fileData[eventKey] = {}  # Init dictionary for given key
                    
                # Make special key for eta 30, 34 and depth2  (this qie10 info will go to qie8 key)
                if specialEtas(key, t.detieta[n], t.detiphi[n], t.detidepth[n]):
                    eventKey = eventKey + '-2'
                    if eventKey not in h.keys():
                        h[eventKey] = ROOT.TH1D(eventKey, eventKey, len(xx[key])-1, xx[key])
                        fileData[eventKey] = {}  # Init dictionary for given key
                        specialKeys.append(eventKey)
                        
                #Fill eta/phi/depth information (will be overwritten many times) :-)
                fileData[eventKey]['eta'] = float(t.detieta[n])
                fileData[eventKey]['phi'] = float(t.detiphi[n])
                
                #if key == 'qie8':
                    #eventData[eventKey]['depth8'] = float(t.detidepth[n])
                    ##if eventKey == '31_39_had':
                        ##print eventKey, eventData[eventKey]['depth8']
                #elif key == 'qie10':
                    #eventData[eventKey]['depth10'] = float(t.detidepth[n])
                    
                fileData[eventKey]['emhad'] = float(emhadId[emhad[str(t.detidepth[n])]])  # 1 for EM, 2 for HAD
                
                #Filling histogram
                for j in range(0, 63):
                    
                    if xx[key][j] < xLowHigh[key][0] or xx[key][j] > xLowHigh[key][1]:
                        continue
                    
                    binContent = cap0hist[n][j] + cap1hist[n][j] + cap2hist[n][j] + cap3hist[n][j]
                    
                    if key == 'qie8':
                        if j>31:
                            h[eventKey].Fill(xx[key][j-2] + 0.001,  binContent/(xx[key][j-1] - xx[key][j-2]))
                        else:
                            h[eventKey].Fill(xx[key][j] +0.001,  binContent/(xx[key][j+1] - xx[key][j]))
                            
                    elif key == 'qie10':
                        h[eventKey].Fill(xx[key][j] +0.001,  binContent/(xx[key][j+1] - xx[key][j]))
                        
                    else:
                        print "Wrong key?"
                    
                
        #for hkey in h.keys():
            #c = ROOT.TCanvas()
            #ROOT.gStyle.SetOptStat(2222222)
            #c.SetLogy()
            #h[hkey].Draw()
            #print  h[hkey].GetMean(), h[hkey].GetMeanError()
            #print  h[hkey].GetEntries(), h[hkey].Integral(), h[hkey].Integral("width")
            #raw_input("Press enter to continue")
        
        #Store results in dictionary
        i = 0
        for eventKey in fileData.keys():
            if key == 'qie8':
                i += 1
                fileData[eventKey]['nentries8'] = h[eventKey].GetEntries()
                fileData[eventKey]['fcMean8'] = h[eventKey].GetMean()
                fileData[eventKey]['fcMean8err'] = h[eventKey].GetMeanError()
                fileData[eventKey]['fcIntegral8'] = h[eventKey].Integral("width")
                
            if key == 'qie10':
                if eventKey in specialKeys:
                    # Eta 30 and 34 depth 2 stored in qie8 data 
                    newkey, dummy = eventKey.split('-')
                    fileData[newkey]['nentries8'] = h[eventKey].GetEntries()
                    fileData[newkey]['fcMean8'] = h[eventKey].GetMean()
                    fileData[newkey]['fcMean8err'] = h[eventKey].GetMeanError()
                    fileData[newkey]['fcIntegral8'] = h[eventKey].Integral("width") 
                    #eventData[newkey]['depth8'] = eventData[hkey]['depth10']
                else:
                    fileData[eventKey]['nentries10'] = h[eventKey].GetEntries()
                    fileData[eventKey]['fcMean10'] = h[eventKey].GetMean()
                    fileData[eventKey]['fcMean10err'] = h[eventKey].GetMeanError()
                    fileData[eventKey]['fcIntegral10'] = h[eventKey].Integral("width") 
        

        del h            
        del f
        del t
        # Write everything into eventData
        for eventKey in fileData.keys():
            for dataKey in fileData[eventKey].keys():
                try:
                    eventData[eventKey][dataKey] = fileData[eventKey][dataKey]
                except KeyError:
                    eventData[eventKey] = {}
                    eventData[eventKey][dataKey] = fileData[eventKey][dataKey]
            #try:
                #eventData[eventKey].append(fileData[eventKey])
            #except KeyError:
                #eventData[eventKey] = fileData[eventKey]
                
 
        print "===="
        print eventData['31_39_had']
        print "===="
    

    #Store data in ntuple
    print "Writing ntuple in", output 
    s = Qie8and10()  
    fout = ROOT.TFile(output,'RECREATE')
    t = ROOT.TTree('t', 'qie8 and qie10 data')
    t.Branch('qie data', s, "eta/D:phi/D:emhad/D:nentries8/D:fcMean8/D:fcMean8err/D:fcIntegral8/D:nentries10/D:fcMean10/D:fcMean10err/D:fcIntegral10/D")
    
    errors = 0
    for eventKey in eventData.keys():
        if eventKey in specialKeys:
            continue
        print "Writing", eventKey
        try:
            s.eta = eventData[eventKey]['eta']
            s.phi = eventData[eventKey]['phi']
            s.nentries10 = eventData[eventKey]['nentries10']
            s.fcMean10 = eventData[eventKey]['fcMean10']
            s.fcMean10err = eventData[eventKey]['fcMean10err']
            s.fcIntegral10 = eventData[eventKey]['fcIntegral10']
            s.emhad = eventData[eventKey]['emhad']
            s.fcMean8 = eventData[eventKey]['fcMean8']
            s.nentries8 = eventData[eventKey]['nentries8']
            s.fcMean8err = eventData[eventKey]['fcMean8err']
            s.fcIntegral8 = eventData[eventKey]['fcIntegral8']
        except KeyError, e:
            print  "Key error for", str(e) 
            errors += 1
            pass
        
        t.Fill()
    print "errors", errors
    fout.Write()
    fout.Close()

if __name__=="__main__":
    main()
