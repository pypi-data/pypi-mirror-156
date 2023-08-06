# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
Module: Collect/MYD11
"""
import pywapor
import sys
from pywapor.collect.MYD11.DataAccess import DownloadData
from pywapor.general.logger import log

def main(Dir, latlim, lonlim, Startdate, Enddate, Waitbar = 1, hdf_library = None, remove_hdf = 1, buffer_dates = False):
    """
    This function downloads MYD11 daily data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    username -- "" string giving the username of your NASA account (https://urs.earthdata.nasa.gov/)
    password -- "" string giving the password of your NASA account
    Waitbar -- 1 (Default) will print a waitbar
    hdf_library -- string, if all the hdf files are already stored on computer
                    define directory to the data here
    remove_hdf -- 1 (Default), if 1 remove all the downloaded hdf files in the end
    """
    username, password = pywapor.collect.accounts.get("NASA")

    log.info(f"--> Downloading MYD11.")
    files = DownloadData(Dir, Startdate, Enddate, latlim, lonlim, username, password, Waitbar, hdf_library, remove_hdf)

    return files

if __name__ == '__main__':
    main(sys.argv)