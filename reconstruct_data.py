#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 3:30 2019

@author: deepnikajain
"""


import os
import requests
import pandas as pd
from astropy.time import Time
import numpy as np


from Coadding.keypairs import get_keypairs


DEFAULT_AUTHs = get_keypairs()
DEFAULT_AUTH_marshal = DEFAULT_AUTHs[0]




def generate_final_fpsf_file(name, targetdir):
    try: 
        os.stat(targetdir + 'data/final_forced_psf_fit_' + name + '.csv')
    except:
        mtb = pd.read_csv(targetdir + 'data/forced_psf_fit_' + name + '.csv')  
        f0 = 10 ** ( 0.4 * mtb['zp'])
        ef0 = f0 * np.log(10) * 0.4 * mtb['ezp']
        mtb.drop(mtb.iloc[:, [3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 25, 26, 27, 28, 29]], 
                 axis = 1, inplace = True)
        n = mtb.shape[0]


        date = [None]*n
        absmag = np.zeros(n)
        mag = np.zeros(n)
        emag = np.zeros(n)
        limmag = np.zeros(n)
        upperlim = [False for i in range(n)]
        instrument = ['P48+ZTF']*n
        source = ['IPAC']*n
        refsys = ['None']*n
        issub = [True for i in range(n)]
        isdiffpos = [True for i in range(n)]
        offset = np.zeros(n)


        mtb.insert(0, 'date', date)
        mtb.insert(4, 'absmag', absmag)
        mtb.insert(5, 'mag', mag)
        mtb.insert(6, 'emag', emag)
        mtb.insert(7, 'limmag', limmag)
        mtb.insert(15, 'upperlim', upperlim)
        mtb.insert(17, 'instrument', instrument)
        mtb.insert(18, 'source', source)
        mtb.insert(19, 'refsys', refsys)
        mtb.insert(20, 'issub', issub)
        mtb.insert(21, 'isdiffpos', isdiffpos)
        mtb.insert(22, 'offset', offset)
        mtb.insert(23, 'f0', f0)
        mtb.insert(24, 'ef0', ef0)

        mtb = mtb[['date', 'jdobs', 'filter', 'seeing', 'absmag', 'mag', 'emag', 'limmag', 'Fmcmc', 'Fmcmc_unc', 
                  'Fratio', 'Fratio_unc', 'jdref_start', 'jdref_end', 'fcqfid', 'upperlim', 'programid', 'instrument', 
                  'source', 'refsys', 'issub', 'isdiffpos', 'offset', 'f0', 'ef0']]

        #Calculating date..
        times = mtb['jdobs']
        t = Time(times, format = 'jd', scale = 'utc')
        mtb['date'] = Time(t.iso, out_subfmt = 'date')
        
        #Correct the filter format
        ig = mtb['filter'] == "b'g'"
        ir = mtb['filter'] == "b'r'"
        ii = mtb['filter'] == "b'i'"
        
        mtb['filter'][ig] = 'g'
        mtb['filter'][ir] = 'r'
        mtb['filter'][ii] = 'i'
        
        #Setting upperlim
        t = mtb['Fratio'].values < 5 * mtb['Fratio_unc'].values
        n = mtb[t].shape[0]
        mtb['upperlim'][t] = [True for i in range(n)]
        
        #Setting isdiffpos
        t = mtb['Fmcmc'].values < 0
        n = mtb[t].shape[0]
        mtb['isdiffpos'][t] = [False for i in range(n)]
        
        #Correct fcqfid for comparison
        f = np.array(mtb['fcqfid'])
        f = f - (f%10000) + (f%10)
        mtb['fcqfid'] = f
        
        mtb.to_csv(targetdir + 'data/final_forced_psf_fit_' + name + '.csv', index = False, encoding = 'utf8')
    
    mtb = pd.read_csv(targetdir + 'data/final_forced_psf_fit_' + name + '.csv')
    
    return mtb




def generate_final_marshal_file(name, targetdir):
    try: 
        os.stat(targetdir + 'data/final_marshal_' + name + '.csv')
    except:
        marshal = pd.read_csv(targetdir + 'data/marshal_' +name+ '.csv')
        marshal.drop(marshal.iloc[:, [12]], axis = 1, inplace = True)
        marshal = marshal.drop_duplicates()
        
        #Drop limits
        nd = np.any([marshal['mag'] == 99, marshal['emag'] == 99], axis = 0)
        marshal = marshal[~nd]
        
        #Drop programid == 2 or 3
        r = np.any([marshal['programid'] == '2', marshal['programid'] == '3', \
                   marshal['programid'] == '2.', marshal['programid'] == '3.'], axis = 0)
        marshal = marshal[~r]
        
        n = marshal.shape[0]

        seeing = np.zeros(n)
        Fmcmc = np.zeros(n)
        Fmcmc_unc = np.zeros(n)
        Fratio = np.zeros(n)
        Fratio_unc = np.zeros(n)
        jdref_start = np.zeros(n)
        jdref_end = np.zeros(n)
        fcqfid = np.zeros(n)
        upperlim = [False for i in range(n)]
        source = ['Marshal']*n
        offset = np.zeros(n)
        f0 = np.zeros(n)
        ef0 = np.zeros(n)

        marshal.insert(3, 'seeing', seeing)
        marshal.insert(9, 'Fmcmc', Fmcmc)
        marshal.insert(10, 'Fmcmc_unc', Fmcmc_unc)
        marshal.insert(11, 'Fratio', Fratio)
        marshal.insert(12, 'Fratio_unc', Fratio_unc)
        marshal.insert(13, 'jdref_start', jdref_end)
        marshal.insert(14, 'jdref_end', jdref_end)
        marshal.insert(15, 'fcqfid', fcqfid)
        marshal.insert(16, 'upperlim', upperlim)
        marshal.insert(18, 'source', source)
        marshal.insert(22, 'offset', offset)
        marshal.insert(23, 'f0', f0)
        marshal.insert(24, 'ef0', ef0)


        marshal = marshal[['date', 'jdobs', 'filter', 'seeing', 'absmag', 'mag', 'emag', 'limmag', 'Fmcmc', 'Fmcmc_unc', 
                  'Fratio', 'Fratio_unc', 'jdref_start', 'jdref_end', 'fcqfid', 'upperlim', 'programid', 'instrument', 
                  'source', 'refsys', 'issub', 'isdiffpos', 'offset', 'f0', 'ef0']]

        #programid datatype change
        marshal['programid'][marshal.programid == 'None'] = '4'
        marshal['programid'] = marshal['programid'].astype('float64')
        
        
        #Computation of Fratio and Fratio_unc
        
        marshal['mag'] = abs(marshal['mag'])
        marshal['emag'] = abs(marshal['emag'])
        
        
        marshal['Fratio'] = 10**(-marshal['mag'].values/2.5)
        marshal['Fratio_unc'] = (marshal['emag'].values * np.log(10) * marshal['Fratio'].values)/2.5
        
        #Checking isdiffpos flag
        pos = marshal['isdiffpos'] == True
        marshal['Fratio'][~pos] = -1 * marshal['Fratio'][~pos]
        
        #Setting fcqfid as filterid
        ig = marshal['filter'] == 'g'
        ir = marshal['filter'] == 'r'
        ii = marshal['filter'] == 'i'
        iz = marshal['filter'] == 'z'
        
        marshal['fcqfid'][ig] = 1
        marshal['fcqfid'][ir] = 2
        marshal['fcqfid'][ii] = 3
        marshal['fcqfid'][iz] = 4
        
        #Setting upperlim
        t = marshal['Fratio'].values < 5 * marshal['Fratio_unc'].values
        n = marshal['upperlim'][t].shape[0]
        marshal['upperlim'][t] = [True for i in range(n)]
        
        
        marshal.to_csv(targetdir + 'data/final_marshal_' + name + '.csv', index = False, encoding = 'utf8')

    marshal = pd.read_csv(targetdir + 'data/final_marshal_' + name + '.csv')
    
    return marshal



def analyze_marshal(marshal, mtb):
    marshal.sort_values(['jdobs'], inplace = True)
    mtb.sort_values(['jdobs'], inplace = True)
    
    mtb_msip = mtb['programid'] == 1 
    mtb1 = mtb[mtb_msip]
    max_jd_fpsf = mtb1['jdobs'].max()

    marshal_msip = marshal['programid'] == 1
    marshal1 = marshal[marshal_msip]
    max_jd_marshal = marshal1['jdobs'].max()

    if max_jd_marshal > max_jd_fpsf:
        new = marshal1['jdobs'].values > max_jd_fpsf
        marshal1 = marshal1[new]
        jd = np.array(marshal1['jdobs'])
    else:
        print ("No new data for programid = 1")
        
    return jd, marshal1



def generate_baseline_file(name, targetdir, mtb, marshal):
    try:
        os.stat(targetdir + 'data/baseline_' + name + '.csv')
    except:
        mtb_msip = mtb['programid'] == 1 
        mtb1 = mtb[mtb_msip]
        max_jd_fpsf = mtb1['jdobs'].max()
        
        marshal_msip = marshal['programid'] == 1

        marshal1 = marshal[marshal_msip]
        max_jd_marshal = marshal1['jdobs'].max()

        if max_jd_marshal > max_jd_fpsf:
            new = marshal1['jdobs'].values > max_jd_fpsf
            marshal1 = marshal1[new]
            baseline = pd.concat([mtb, marshal1])
        else:
            print ("No new data for programid = 1")
            baseline = mtb
            
        n = baseline.shape[0]
        outlier = [False for i in range(n)]
        baseline.insert(23, 'outlier', outlier)
        
        chisq = np.zeros(n)
        baseline.insert(24, 'chisq', chisq)
     
        baseline.to_csv(targetdir + 'data/baseline_' + name + '.csv', index = False, encoding = 'utf8')

    baseline = pd.read_csv(targetdir + 'data/baseline_' + name + '.csv')
    
    return baseline




def generate_combined_file(name, targetdir, baseline, marshal):
    try:
        os.stat(targetdir + 'data/combined_' + name + '.csv')
    except:
        marshal_other = marshal['programid'] == 4
        marshal1 = marshal[marshal_other]
        marshal1 = marshal1.drop(marshal1.iloc[:, [0, 3, 4, 8, 9, 12, 13, 14, 22]], axis = 1)
        
        n = marshal1.shape[0]
        SNR = np.zeros(n)
        baseline.insert(14, 'SNR', SNR)
        coa = [False for i in range(n)]
        baseline.insert(15, 'coa', coa)
        combined = pd.concat([baseline1, marshal1])

        combined.to_csv(targetdir + 'data/combined_' + name + '.csv', index = False, encoding = 'utf8')

    combined = pd.read_csv(targetdir + 'data/combined_' + name + '.csv')
    
    return combined




def calculate_mag(mtb):
    fratio = mtb['Fratio']
    efratio = mtb['Fratio_unc']
    snr = mtb['SNR']
    n = mtb.shape[0]
    
    neg = snr.values < 3
    non_neg = snr.values >= 3
    
    mtb['mag'][neg] = [99 for i in range (mtb[neg].shape[0])]
    mtb['emag'][neg] = [99 for i in range (mtb[neg].shape[0])]
    mtb['limmag'][neg] = -2.5 * np.log10(5*efratio[neg].values)
                        
    mtb['mag'][non_neg] = -2.5 * np.log10(fratio[non_neg].values)
    mtb['emag'][non_neg] = -2.5 * efratio[non_neg].values / (np.log(10) * fratio[non_neg].values)
    mtb['limmag'][non_neg] = [99 for i in range (mtb[non_neg].shape[0])]
    
    mtb.update(mtb[neg])
    mtb.update(mtb[non_neg])
    
    return mtb