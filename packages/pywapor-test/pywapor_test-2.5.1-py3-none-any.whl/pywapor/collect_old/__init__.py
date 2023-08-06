# -*- coding: utf-8 -*-
"""

This module contains scripts used to download Level 1 data (data directly from web).

Products                      Dates                             Password
CHIRPS (daily)                1981/01/01-now                    -
SRTM                           -                                 -
GLDAS                         2000/01/01-now                    NASA
MCD43 (daily)                 2000/02/24-now                    NASA
MOD11 (daily)                 2000/02/24-now                    NASA
MYD11 (daily)                 2000/02/24-now                    NASA
MYD13 (16-daily)              2000/02/18-now                    NASA
MOD13 (16-daily)              2000/02/18-now                    NASA
MERRA
MSGCPP
GEOS

Examples:
from pyWAPOR import Collect
help(Collect)
dir(Collect)
"""

from pywapor.collect import CHIRPS, MOD11, MYD11, MCD43, MOD13, MYD13, MERRA2, Globcover, GEOS5, SRTM, WAPOR, PROBAV, STATICS, accounts, Landsat, sideloader, downloader

__all__ = ['CHIRPS', 'MOD11', 'MYD11', 'MCD43', 'MOD13', 'MYD13', 'MERRA2', 'SRTM', 'Globcover', 'GEOS5', 'WAPOR' , 'PROBAV', 'STATICS', 'accounts', 'Landsat', 'sideloader', 'downloader']

__version__ = '0.1'
