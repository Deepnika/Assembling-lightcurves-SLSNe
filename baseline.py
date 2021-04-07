#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 3:45 2019

@author: deepnikajain
"""


import os
import requests
import pandas as pd
from astropy.time import Time
import numpy as np
import matplotlib.pyplot as plt


from Coadding.keypairs import get_keypairs
from Coadding.setup import yes_no


def compute_offset(mtb, name, targetdir, fcqfid, startjd, endjd, color):
    mtb1 = mtb[mtb.jdobs > startjd+2458000]
    mtb1 = mtb1[mtb1.jdobs < endjd+2458000]
    ix = mtb1['fcqfid'] == fcqfid
    mtb1 = mtb1[ix]
    
    #Plot Baseline
    plt.figure(figsize=(12,6))
    thistime = (mtb1['jdobs'] - 2458000)
    plt.errorbar(thistime, mtb1['Fmcmc'], mtb1['Fmcmc_unc'], 
                 fmt='.', color=color, label = 'fcqfid = %d, Nobs = %d'%(fcqfid, np.sum(ix)))
    plt.grid(which = 'both', ls=":")
    plt.xlabel('JD - 2458000 (days)')
    plt.ylabel('Fmcmc')
    plt.legend(loc = 'best')
    plt.title(name + ' - Baseline')
    plt.tight_layout()
    plt.show()
    
    
    #First calculate weighted average to compute standard deviation
    fpsf = mtb1['Fmcmc']
    efpsf = mtb1['Fmcmc_unc'] ** (-2)
    m = np.average(fpsf, weights = efpsf)
    
    
    #Remove outliers
    if yes_no('Remove Outliers?\n') == True:
        
        #Compute SD
        sd = np.sqrt(np.average((fpsf - m)**2, weights = efpsf))
        print ('Standard Deviation: ', sd, 'about Fmcmc = ', m)
        
        #Set outlier = True for outliers (3*sd)
        i = abs (mtb1['Fmcmc'] - m) > 3 * sd
        mtb1['outlier'][i] = [True for i in range(mtb1[i].shape[0])]
        
        #Remove outliers from baseline calculation
        mtb.update(mtb1[i])
        mtb1 = mtb1[~i]
        
        #Plot baseline without outliers
        plt.figure(figsize=(12,6))
        ix = mtb1['fcqfid'] == fcqfid
        thistime = (mtb1['jdobs'] - 2458000)
        plt.errorbar(thistime, mtb1['Fmcmc'], mtb1['Fmcmc_unc'], 
                     fmt='.', color=color, label = 'fcqfid = %d, Nobs = %d'%(fcqfid, np.sum(ix)))
        plt.grid(which = 'both', ls=":")
        plt.xlabel('JD - 2458000 (days)')
        plt.ylabel('Fmcmc')
        plt.legend(loc = 'best')
        plt.title(name + ' - Baseline without outliers')
        plt.tight_layout()
        plt.show()
        
    #Compute correct offset and reduced chisq without outliers
    fpsf = mtb1['Fmcmc']
    efpsf = mtb1['Fmcmc_unc'] ** -2
    Nbase = np.sum(ix)
    m = np.average(fpsf, weights = efpsf)
    chi = (m - fpsf)**2/ (mtb1['Fmcmc_unc']**2)
    chisq = np.sum(chi)
    chisq = chisq / (Nbase -1)
    
    #Print Offset and chisq
    print ('Offset: ', m)
    print ('Chisq: ', chisq)

    
    return m, chisq, mtb




def compute_baseline(name, targetdir, mtb):
    fcqfs = np.unique(mtb['fcqfid'].values)

    for fcqfid in fcqfs:
        plt.figure(figsize=(12,6))
        ix = mtb['fcqfid'].values == fcqfid
        if fcqfid % 10 == 1:
            color = 'g'
        elif fcqfid % 10 == 2:
            color = 'r'
        elif fcqfid %10 == 3:
            color = 'orange'
        else:
            color = 'black'
        thistime = (mtb['jdobs'][ix] - 2458000)
        plt.errorbar(thistime, mtb['Fmcmc'][ix], mtb['Fmcmc_unc'][ix], 
                         fmt='.', color=color, label = 'fcqfid = %d, Nobs = %d'%(fcqfid, np.sum(ix)))
        plt.grid(ls=":")
        plt.xlabel('JD - 2458000 (days)')
        plt.ylabel('Fmcmc')
        plt.legend(loc = 'best')
        plt.title(name)
        plt.tight_layout()
        plt.show()
        if yes_no('Compute Offset?\n') == True:
            startjd = int(input("Please enter startjd-2458000:\n"))
            endjd = int(input("Please enter endjd-2458000:\n"))
            offset, chisq, mtb = compute_offset(mtb, name, targetdir, fcqfid, startjd, endjd, color)
            mtb['offset'][ix] = offset
            mtb['chisq'][ix] = chisq
            plt.figure(figsize=(12,6))
            plt.errorbar(thistime, mtb['Fmcmc'][ix] - offset, mtb['Fmcmc_unc'][ix] * np.sqrt(chisq), 
                         fmt='.', color=color, label = 'fcqfid = %d, Nobs = %d'%(fcqfid, np.sum(ix)))
            ax = plt.gca()
            ylims1 = ax.get_ylim()
            plt.ylim(ylims1[0], ylims1[1])
            plt.grid(which = 'both', ls=":")
            plt.xlabel('JD - 2458000 (days)')
            plt.ylabel('Fmcmc')
            plt.legend(loc = 'best')
            plt.title(name + ' - Shifted: With outliers')
            plt.tight_layout()
            plt.show()
            mtb.to_csv(targetdir + 'data/baseline1_' + name + '.csv', index = False, encoding = 'utf8')
        else:
            continue
            
            
            
def apply_shift(targetdir, name, mtb, ffid):
    
    ix = mtb['fcqfid'].values == ffid
    mtb1 = mtb[ix]

    C = mtb1['offset'].unique()
    if len(C) == 1:
        c = C[0]
        print(c)
    else:
        print ('Error: More than one offset values')

    Chi = mtb1['chisq'].unique()
    if len(Chi) == 1:
        chi = Chi[0]
        print(chi)
    else:
        print ('Error: More than one chisq values')

    #Correct flux
    mtb1['Fmcmc'] = mtb1['Fmcmc'] - mtb1['offset']

    #Rescale error in flux
    if chi > 1:
        mtb1['Fmcmc_unc'] = mtb1['Fmcmc_unc'] * np.sqrt(chi)

    #Correct Fratio
    mtb1['Fratio'] = mtb1['Fmcmc']/mtb1['f0']

    #Correct error in Fratio
    mtb1['Fratio_unc'] = np.sqrt((mtb1['Fmcmc_unc']/mtb1['f0']) **2 + (mtb1['Fmcmc'] * mtb1['ef0'] / (mtb1['f0'] ** 2))**2)

#         #Set offset = 0 and chisq = 1
    mtb1['offset'] = 0
    mtb1['chisq'] = 1

    #Update mtb
    mtb.update(mtb1)


    return mtb            
            
       
            
     
