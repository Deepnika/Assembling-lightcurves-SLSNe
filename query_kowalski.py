#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 3:15 2019

@author: deepnikajain
"""



import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table
from penquins import Kowalski


from Coadding.keypairs import get_keypairs

DEFAULT_AUTHs = get_keypairs()
DEFAULT_AUTH_kowalski = DEFAULT_AUTHs[1]



def query_kowal(name, lowjd, upjd):
    k = Kowalski(username=DEFAULT_AUTH_kowalski[0], password=DEFAULT_AUTH_kowalski[1], verbose=False)
    qu = {"query_type": "general_search", 
          "query": "db['ZTF_alerts'].find({'objectId': {'$eq': '%s'}, 'candidate.jd': {'$gt': '%d'}, \
          'candidate.jd': {'$lt': '%d'}, {'candidate.jd': 1, 'candidate.fid': 1,   \
          'candidate.programid': 1, 'candidate.field': 1, 'candidate.magzpsci': 1, 'candidate.magzpsciunc': 1,})"%(name, lowjd, upjd)}

    r = k.query(query=qu)
    
    return r
    
    
    
def get_kdata(targetdir, name, r):
    if 'result_data' in list(r.keys()):
        rdata = r['result_data']
        rrdata = rdata['query_result']  
        n = len(rrdata)

        jd = []
        fid = []
        programid = []
        fieldid = []
        mag = []
        magzp = []
        magzp_unc = []

        for i in range(n):
            if rrdata[i]['candidate']['programid'] == 1:
                jd.append(rrdata[i]['candidate']['jd'])
                fid.append(rrdata[i]['candidate']['fid'])
                programid.append(rrdata[i]['candidate']['programid'])
                fieldid.append(rrdata[i]['candidate']['field'])
#                 mag.append(rrdata[i]['candidate']['magpsf'])
                magzp.append(rrdata[i]['candidate']['magzpsci'])
                magzp_unc.append(rrdata[i]['candidate']['magzpsciunc'])

        jd = np.array(jd)
        fid = np.array(fid)
        programid = np.array(programid)
        fieldid = np.array(fieldid)
        mag = np.array(mag)
        magzp = np.array(magzp)
        magzp_unc = np.array(magzp_unc)

        k_data = Table([jd, fid, programid, fieldid, mag, magzp, magzp_unc], \
                       names = ['jdobs', 'fid', 'programid', 'fieldid', 'mag', 'magzp', 'magzp_unc'])
        kdata = k_data.to_pandas()
        kdata.to_csv(targetdir + 'data/kowalski_data_' + name + '.csv', index = False, encoding = 'utf8')
    
    
    else:
        print(('Kowalski query is not succesful for %s'%name))

    kdata = kdata.drop_duplicates()
    kdata.sort_values(['jdobs'], inplace = True)
    p = kdata.shape
    
    
    if 'result_data' in list(r.keys()):
        rdata = r['result_data']
        rrdata = rdata['query_result']  
        n = len(rrdata)

        jd = []
        fid = []
        programid = []
        fieldid = []
        mag = []
        magzp = []
        magzp_unc = []

        for i in range(n):
            if rrdata[i]['prv_candidates'] != None:
                m = len(rrdata[i]['prv_candidates'])
                for j in range(m):
                    if 'magzpsci' in list(rrdata[i]['prv_candidates'][j].keys()):
                        if rrdata[i]['prv_candidates'][j]['magpsf'] != None:
                            if rrdata[i]['prv_candidates'][j]['programid'] == 1:
                                jd.append (rrdata[i]['prv_candidates'][j]['jd'])
                                fid.append (rrdata[i]['prv_candidates'][j]['fid'])
                                programid.append (rrdata[i]['prv_candidates'][j]['programid'])
                                fieldid.append (rrdata[i]['prv_candidates'][j]['field'])
#                                 mag.append (rrdata[i]['prv_candidates'][j]['magpsf'])
                                magzp.append (rrdata[i]['prv_candidates'][j]['magzpsci'])
                                magzp_unc.append (rrdata[i]['prv_candidates'][j]['magzpsciunc'])

        jd = np.array(jd)
        fid = np.array(fid)
        programid = np.array(programid)
        fieldid = np.array(fieldid)
        mag = np.array(mag)
        magzp = np.array(magzp)
        magzp_unc = np.array(magzp_unc)

        k_data = Table([jd, fid, programid, fieldid, mag, magzp, magzp_unc], \
                       names = ['jdobs', 'fid', 'programid', 'fieldid', 'mag', 'magzp', 'magzp_unc'])
        kdata1 = k_data.to_pandas()
        kdata1.to_csv(targetdir + 'data/kowalski_data1_' + name + '.csv', index = False, encoding = 'utf8')

    
    else:
        print(('Kowalski query is not succesful for %s'%name))

    kdata1 = kdata1.drop_duplicates()
    kdata1.sort_values(['jdobs'], inplace = True)
    q = kdata1.shape
    
    
    kdata = kdata.append(kdata1)
    kdata = kdata.drop_duplicates()
    kdata.sort_values(['jdobs'], inplace = True)
    
    return p, q, kdata



