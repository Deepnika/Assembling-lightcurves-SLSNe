#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue July 2 1:30 2019

@author: deepnikajain
"""



import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plotlc(mtb, y, name, targetdir):
    fcqfs = np.unique(mtb['fcqfid'].values)

    colors_g = ['limegreen', 'c', 'skyblue', 'green']
    colors_r = ['r', 'm', 'pink', 'black', 'darkgreen' ]
    colors_i = ['gold', 'orange', 'y', 'blue', 'c']

    plt.figure(figsize=(12,6))
    for fcqfid in fcqfs:
        ix = mtb['fcqfid'].values==fcqfid
        if y == 'Fratio':
            yerr = 'Fratio_unc'
            offset = np.zeros(mtb[ix].shape[0])
        elif y == 'Fmcmc':
            yerr = 'Fmcmc_unc'
            offset = np.array(mtb['offset'][ix])
            
        if fcqfid % 10 ==1:
            color=colors_g[0]
            colors_g = colors_g[1:]
        elif fcqfid % 10 == 2:
            color=colors_r[0]
            colors_r = colors_r[1:]
        else:
            color=colors_i[0]
            colors_i = colors_i[1:]
            
        thistime = (mtb['jdobs'][ix] - 2458000)
        plt.errorbar(thistime, mtb[y][ix] - offset, mtb[yerr][ix], 
                         fmt='.', color=color, label = 'fcqfid = %d, Nobs = %d'%(fcqfid, np.sum(ix)))

    ax = plt.gca()
    ylims1 = ax.get_ylim()
    plt.ylim(ylims1[0], ylims1[1])
    plt.grid(ls=":")
    plt.xlabel('JD - 2458000 (days)')
    plt.ylabel(y)
    plt.legend(loc = 'best')
    plt.title(name)
    plt.tight_layout()
    
#     plt.savefig(targetdir + name+'_fig_lc'+'.pdf')
    
    
def jdref_plot(targetdir, name, mtb, y1, y2):
    ffids = np.unique(mtb['fcqfid'].values)
    
    for ffid in ffids:
        ix = mtb['fcqfid'].values == ffid
        plt.figure(figsize=(12,6))
        plt.plot(mtb['jdobs'][ix], 'k.', label = 'JD obs')
        plt.plot(mtb['jdref_start'][ix], 'g.', label = 'JD start')
        plt.plot(mtb['jdref_end'][ix], 'rx', label = 'JD end')

        plt.grid(which = 'major', ls=":")
        plt.ylabel('JD - 2458000 (days)')
        plt.legend(loc = 'best')
        plt.title(name + ': %d' %(ffid))
        plt.tight_layout()
        plt.ylim(2458000 + y1, 2458000 + y2)
        plt.savefig(targetdir + name + '_' + str(ffid) + '.pdf') 
        plt.show()
    
    
def plot_mag(mtb, name, targetdir, x1, x2):
    
    filterid = np.unique(mtb['filter'].values)

    colors = ['c', 'skyblue', 'm', 'pink', 'black', 'darkgreen', 'y']

    plt.figure(figsize=(12,6))
    for fid in filterid:
        ix = mtb['filter'].values == fid
        if fid == 'r':
            color = 'r'
        elif fid == 'g':
            color = 'g'
        elif fid == 'i':
            color = 'orange'
        elif fid == 'z':
            color = 'blue'
        else:
            color = colors[0]
            colors = colors[1:]
        mtb1 = mtb[ix]
        ii = mtb1['upperlim'] == False
        mtb2 = mtb1[ii]
        ic = mtb2['coa'] == 2
        if np.sum(ic) > 0:
            thistime = (mtb2['jdobs'][ic] - 2458000)
            plt.errorbar(thistime, mtb2['mag'][ic], mtb2['emag'][ic], 
                         fmt = 'o', color=color, fillstyle = 'none', label = 'coadd, filter = %s, Nobs = %d'%(fid, np.sum(ic)))
        
        ic = np.any([mtb2['coa'] == 0, mtb2['coa'] == 1], axis = 0)
        thistime = (mtb2['jdobs'][ic] - 2458000)
        plt.errorbar(thistime, mtb2['mag'][ic], mtb2['emag'][ic], 
                         fmt = '.', color=color, label = 'filter = %s, Nobs = %d'%(fid, np.sum(ix)))
        
        iq = mtb1['upperlim'] == True
        time = (mtb1['jdobs'][iq] - 2458000)
        time = np.array(time)
        l = mtb1['limmag'][iq]
        l = np.array(l)
        dx = np.zeros(mtb1[iq].shape[0])
        dy = np.array([0.05] * mtb1[iq].shape[0])
        for i in range(len(l)):
            plt.arrow(time[i], l[i], dx[i], dy[i], color = color, head_width=2, head_length=0.09, 
                      linestyle = 'dashdot')
    
    ax = plt.gca()
    ylims1 = ax.get_ylim()
    plt.ylim(ylims1[1], ylims1[0])
    plt.xlim(x1, x2)
    plt.grid(ls=":")
    plt.xlabel('JD - 2458000 (days)')
    plt.ylabel('magnitude')
    plt.legend(loc = 'best')
    plt.title(name)
    plt.tight_layout()
#     plt.savefig(targetdir + name+'_fig_lc'+'.pdf')

    
    

def plot_fil(mtb, name, targetdir, x1, x2):
    filterid = np.unique(mtb['filter'].values)

    colors = ['c', 'skyblue', 'm', 'pink', 'black', 'darkgreen', 'y']

    plt.figure(figsize=(12,6))
    for fid in filterid:
        ix = mtb['filter'].values == fid
        if fid == 'r':
            color = 'r'
        elif fid == 'g':
            color = 'g'
        elif fid == 'i':
            color = 'orange'
        elif fid == 'z':
            color = 'blue'
        else:
            color = colors[0]
            colors = colors[1:]
            
        thistime = (mtb['jdobs'][ix] - 2458000)
        plt.errorbar(thistime, mtb['Fratio'][ix], mtb['Fratio_unc'][ix], 
                         fmt='.', color=color, label = 'filter = %s, Nobs = %d'%(fid, np.sum(ix)))

        
    ax = plt.gca()
    ylims1 = ax.get_ylim()
    plt.ylim(ylims1[0], ylims1[1])
    plt.xlim(x1, x2)
    plt.grid(ls=":")
    plt.xlabel('JD - 2458000 (days)')
    plt.ylabel('Fratio')
    plt.legend(loc = 'best')
    plt.title(name)
    plt.tight_layout()

    