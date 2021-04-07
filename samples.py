#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 05 1:40 2019

@author: deepnikajain
"""
import os


def get_names(base):
    with open(os.path.join(os.path.dirname(__file__), 'samples.txt'),'r') as f:
        lines = f.read().splitlines()
        samples = []
        for x in lines:
            path = base + '/SLSNe/' + x + '/' + 'lightcurves/final_lightcurve_' + x + '.csv'
            if os.path.exists(path) == False:
                samples.append(x)
        print ('Remaining sources: %s' %samples)
        f.close()
    return (samples)