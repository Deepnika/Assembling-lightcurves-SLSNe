#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 5:30 2019

@author: deepnikajain
"""


import os
import requests
import pandas as pd
from astropy.time import Time
import numpy as np
import matplotlib.pyplot as plt


from Coadding.setup import yes_no


def coadd_rem_outliers(targetdir, name, mtb, filt, startjd, endjd):
    try:
        os.stat(targetdir + 'data/coadd_' + name + '.csv')
    except:
        coadd = pd.DataFrame(columns = ['startjd', 'endjd', 'filter', 'Fratio', 
                                        'Fratio_unc', 'SNR', 'jdobs'])
        coadd.to_csv(targetdir + 'data/coadd_' + name + '.csv', index = False, encoding = 'utf8')
    
    
    coadd = pd.read_csv(targetdir + 'data/coadd_' + name + '.csv')
    
    mtb1 = mtb[mtb.jdobs > startjd+2458000]
    mtb1 = mtb1[mtb1.jdobs < endjd+2458000]
    
    ix = mtb1['filter'] == filt
    fratio = mtb1['Fratio'][ix]
    efratio = mtb1['Fratio_unc'][ix] ** (-2)
    f = np.average(fratio, weights = efratio)
    ef = np.sum(efratio) **(-0.5)
    s = f/ef
    if s > 3:
        print('Found a real detection.\n')
        print('Fratio = ', f, '\n')
        print('Fratio_unc = ', ef, '\n')
        print('SNR = ', s, '\n')
        jd = np.median(mtb1['jdobs'][ix], axis = None)
        coadd = coadd.append({'startjd': startjd, 'endjd': endjd, 'filter': filt, 'Fratio': f, 
                              'Fratio_unc': ef, 'SNR': s, 'jdobs': jd}, ignore_index = True)
        
        mtb1['coa'][ix] = [1 for i in range (mtb1[ix].shape[0])]
        mtb.update(mtb1[ix])
    else:
        print ('Not a detection.\n')
        print('SNR = ', s, '\n')
        
    coadd.to_csv(targetdir + 'data/coadd_' + name + '.csv', index = False, encoding = 'utf8')
    
    return f, ef, s, mtb


def coadd(targetdir, name, mtb):
    fil = np.unique(mtb['filter'].values)

    for filt in fil:
        plt.figure(figsize=(12,6))
        ix = mtb['filter'] == filt
        thistime = (mtb['jdobs'][ix] - 2458000)
        plt.plot(thistime, mtb['Fratio'][ix]/mtb['Fratio_unc'][ix], 'rx', label = 'filter = %s, Nobs = %d'%(filt, np.sum(ix)))

        plt.minorticks_on()
        plt.grid(which = 'major', ls = '-', color = 'r')
        plt.grid(which = 'minor', ls = ':', color = 'black')
        plt.xlabel('JD - 2458000 (days)')
        plt.ylabel('SNR')
        plt.title(name + ': ' + filt)
        plt.legend(loc = 'best')
        plt.tight_layout()
        plt.show()
        while (yes_no('Coadd?\n') == True):
            startjd = int(input("Please enter startjd-2458000:\n"))
            endjd = int(input("Please enter endjd-2458000:\n"))

            fratio, fratio_unc, snr, mtb = coadd_rem_outliers(targetdir, name, mtb, filt, startjd, endjd)
            
    return mtb









