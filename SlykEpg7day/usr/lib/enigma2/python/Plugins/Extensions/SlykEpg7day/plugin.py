#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigEnableDisable, ConfigClock, ConfigSelection, ConfigText, ConfigSelectionNumber
from enigma import getDesktop, eTimer
from Plugins.Plugin import PluginDescriptor
import time
import sys
import twisted.python.runtime

try:
    from multiprocessing.pool import ThreadPool
    hasMultiprocessing = True
except:
    hasMultiprocessing = False

try:
    from concurrent.futures import ThreadPoolExecutor
    if twisted.python.runtime.platform.supportsThreads():
        hasConcurrent = True
    else:
        hasConcurrent = False
except:
    hasConcurrent = False

pythonFull = float(str(sys.version_info.major) + "." + str(sys.version_info.minor))
pythonVer = sys.version_info.major

screenwidth = getDesktop(0).size()

autoStartTimer = None

"""
hdr = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}
"""

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

regionlist = [
    ("Atherstone", _("Atherstone")),
    ("BorderEngland", _("Border England")),
    ("BorderScotland", _("Border Scotland")),
    ("Brighton", _("Brighton")),
    ("CentralMidlands", _("Central Midlands")),
    ("ChannelIsles", _("Channel Isles")),
    ("Dundee", _("Dundee")),
    ("EastMidlands", _("East Midlands")),
    ("Essex", _("Essex")),
    ("Gloucester", _("Gloucester")),
    ("Grampian", _("Grampian")),
    ("Granada", _("Granada")),
    ("HTVWales", _("HTV Wales")),
    ("HTVWest", _("HTV West")),
    ("HTVWestThamesValley", _("HTV West / Thames Valley")),
    ("HenleyOnThames", _("Henley On Thames")),
    ("Humber", _("Humber")),
    ("London", _("London")),
    ("LondonEssex", _("London / Essex")),
    ("LondonThamesValley", _("London / Thames Valley")),
    ("LondonKent", _("London Kent")),
    ("MeridianEast", _("Meridian East")),
    ("MeridianNorth", _("Meridian North")),
    ("MeridianSouth", _("Meridian South")),
    ("MeridianSouthEast", _("Meridian South East")),
    ("Merseyside", _("Merseyside")),
    ("Norfolk", _("Norfolk")),
    ("NorthEastMidlands", _("North East Midlands")),
    ("NorthWestYorkshire", _("North West Yorkshire")),
    ("NorthYorkshire", _("North Yorkshire")),
    ("NorthernIreland", _("Northern Ireland")),
    ("Oxford", _("Oxford")),
    ("RepublicofIreland", _("Republic of Ireland")),
    ("RidgeHill", _("Ridge Hill")),
    ("Scarborough", _("Scarborough")),
    ("ScottishEast", _("Scottish East")),
    ("ScottishWest", _("Scottish West")),
    ("Sheffield", _("Sheffield")),
    ("SouthLakeland", _("South Lakeland")),
    ("SouthYorkshire", _("South Yorkshire")),
    ("Tees", _("Tees")),
    ("ThamesValley", _("Thames Valley")),
    ("Tring", _("Tring")),
    ("Tyne", _("Tyne")),
    ("Wales", _("Wales")),
    ("WestAnglia", _("West Anglia")),
    ("WestDorset", _("West Dorset")),
    ("Westcountry", _("Westcountry"))
]

regionbouquets = {
    "Atherstone": [4101, 19],
    "BorderEngland": [4101, 12],
    "BorderScotland": [4102, 36],
    "Brighton": [4103, 65],
    "CentralMidlands": [4101, 3],
    "ChannelIsles": [4104, 34],
    "Dundee": [4102, 39],
    "EastMidlands": [4101, 20],
    "Essex": [4101, 2],
    "Gloucester": [4101, 24],
    "Grampian": [4102, 35],
    "Granada": [4101, 7],
    "HTVWest": [4101, 4],
    "HTVWestThamesValley": [4103, 63],
    "HenleyOnThames": [4103, 70],
    "Humber": [4101, 29],
    "London": [4101, 1],
    "LondonEssex": [4101, 18],
    "LondonThamesValley": [4103, 66],
    "LondonKent": [4103, 64],
    "MeridianEast": [4101, 11],
    "MeridianNorth": [4103, 68],
    "MeridianSouth": [4101, 5],
    "MeridianSouthEast": [4101, 10],
    "Merseyside": [4103, 45],
    "Norfolk": [4101, 21],
    "NorthEastMidlands": [4103, 62],
    "NorthWestYorkshire": [4101, 8],
    "NorthYorkshire": [4101, 26],
    "NorthernIreland": [4104, 33],
    "Oxford": [4103, 71],
    "RepublicofIreland": [4104, 50],
    "RidgeHill": [4103, 41],
    "Scarborough": [4103, 61],
    "ScottishEast": [4102, 38],
    "ScottishWest": [4102, 37],
    "Sheffield": [4103, 60],
    "SouthLakeland": [4101, 28],
    "SouthYorkshire": [4103, 72],
    "Tees": [4103, 69],
    "ThamesValley": [4101, 9],
    "Tring": [4101, 27],
    "Tyne": [4101, 13],
    "Wales": [4104, 32],
    "WestAnglia": [4101, 25],
    "WestDorset": [4103, 67],
    "Westcountry": [4101, 6]
}

schedulelist = [("daily", _("Daily")), ("monday", _("Monday")), ("tuesday", _("Tuesday")), ("wednesday", _("Wednesday")), ("thursday", _("Thursday")), ("friday", _("Friday")), ("saturday", _("Saturday")), ("sunday", _("Sunday"))]


config.plugins.SlykEpg7day = ConfigSubsection()
cfg = config.plugins.SlykEpg7day
cfg.enabled = ConfigEnableDisable(default=False)
cfg.wakeup = ConfigClock(default=((7 * 60) + 9) * 60)  # 7:00
cfg.epgDescDays = ConfigSelectionNumber(default=3, stepwidth=1, min=1, max=7, wraparound=True)
cfg.lamedb = ConfigYesNo(default=False)
cfg.rytec = ConfigSelection(default='rytec', choices=[('unique', _('Unique IDs')), ('rytec', _('Match Rytec IDs'))])
cfg.timeshift = ConfigSelectionNumber(default=0, stepwidth=1, min=-7, max=7, wraparound=True)
cfg.ukcable = ConfigYesNo(default=False)
cfg.compress = ConfigYesNo(default=False)
cfg.region = ConfigSelection(default='London', choices=regionlist)
cfg.schedule = ConfigSelection(default='daily', choices=schedulelist)

config.plugins.extra_slykepg7day = ConfigSubsection()
config.plugins.extra_slykepg7day.last_import = ConfigText(default="none")


CONFIG_PATH = '/etc/SlykEpg7day'


class AutoStartTimer:

    def __init__(self, session):
        self.session = session
        self.epgtimer = eTimer()
        self.epgtimer.callback.append(self.onTimer)
        self.update()

    def getWakeTime(self):
        if cfg.enabled.value:
            clock = cfg.wakeup.value
            nowt = time.time()
            now = time.localtime(nowt)
            return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday, clock[0], clock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
        else:
            return -1

    def update(self, atLeast=0):
        self.epgtimer.stop()
        wake = self.getWakeTime()
        now = int(time.time())
        if wake > 0:
            if wake < now + atLeast:
                # Tomorrow.
                wake += 24 * 3600
            next = wake - now
            if next > 3600:
                next = 3600
            if next <= 0:
                next = 60
            self.epgtimer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def onTimer(self):
        self.epgtimer.stop()
        now = int(time.time())
        wake = self.getWakeTime()
        atLeast = 0
        if abs(wake - now) < 60:
            self.runUpdate()
            atLeast = 60
        self.update(atLeast)

    def runUpdate(self):
        print('\n *********** Import Slyk EPG 7 Day ************ \n')
        from . import main
        self.session.open(main.SlykEpg7Day_Main, "auto")


def autostart(reason, session=None, **kwargs):
    global autoStartTimer
    if reason == 0 and session is not None and autoStartTimer is None:
        autoStartTimer = AutoStartTimer(session)

def main(session, **kwargs):
    from . import main
    session.open(main.SlykEpg7Day_Main, "manual")


def Plugins(**kwargs):

    iconFile = 'icons/slykepg7day.png'
    if screenwidth.width() > 1280:
        iconFile = 'icons/slykepg7dayFHD.png'

    description = _('Download Real Sky UK 7 Day EPG - By KiddaC')
    pluginname = _('Slyk EPG 7 Day')

    return [PluginDescriptor(name=pluginname, description=description, where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
            PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconFile, fnc=main)]
