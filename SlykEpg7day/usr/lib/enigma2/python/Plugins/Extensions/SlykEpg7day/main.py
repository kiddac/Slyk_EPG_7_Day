#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from .plugin import cfg, screenwidth, regionbouquets
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import configfile, getConfigListEntry
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from enigma import eTimer
from multiprocessing.pool import ThreadPool
from os import system
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import datetime
import json
import os
import enigma
import csv
import unicodedata
import re
import sys

pythonVer = 2
if sys.version_info.major == 3:
    pythonVer = 3

if pythonVer == 3:
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request

try:
    from cStringIO import StringIO
except:
    from io import StringIO

haslzma = False

try:
    import lzma
    print('\nlzma success')
    haslzma = True

except ImportError:

    try:
        from backports import lzma
        print('\nbackports lzma success')
        haslzma = True

    except ImportError:
        print('\nlzma failed')
        pass


class SlykEpg7Day_Main(ConfigListScreen, Screen):

    def __init__(self, session, runtype):
        self.runtype = runtype

        if self.runtype == "manual":

            if screenwidth.width() > 1280:
                skin = """
                    <screen name="SlykEpgSetup" position="center,center" size="1200,762" title="Slyk EPG 7 Day Downloader" >

                        <widget name="description" position="45,0" size="1110,120" font="Regular;30" valign="top" transparent="1" foregroundColor="#6dcff6" />

                        <widget name="config" textOffset="15,0" position="30,120" size="1140,504" font="Regular;30" secondfont="Regular;30"  itemHeight="72" enableWrapAround="1"  scrollbarMode="showOnDemand" transparent="1" />

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/key_red.png" position="30,e-40" size="9,42" zPosition="1" />
                        <widget source="key_red" render="Label" position="48,e-40" size="225,42" font="Regular;30" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1" />

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/key_green.png"  position="273,e-40" size="9,42" zPosition="1" />
                        <widget source="key_green" render="Label" position="291,e-40" size="225,42" font="Regular;30" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1" />

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/key_yellow.png" position="516,e-40" size="9,42" zPosition="1" />
                        <widget source="key_yellow" render="Label" position="534,e-40" size="225,42" font="Regular;30" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1"/>

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/key_blue.png" position="759,e-40" size="9,42" zPosition="1" />
                        <widget source="key_blue" render="Label" position="777,e-40" size="225,42" font="Regular;30" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1"/>

                        <widget name="status" position="45,e-120" size="1110,42" font="Regular;30" valign="center" transparent="1" foregroundColor="#6dcff6" />
                    </screen>"""

            else:
                skin = """
                    <screen name="SlykEpgSetup" position="center,center" size="800,508" title="Slyk EPG 7 Day Downloader" >

                        <widget name="description" position="40,0" size="760,80" font="Regular;20" valign="top" transparent="1" foregroundColor="#6dcff6" />

                        <widget name="config" textOffset="10,0" position="20,80" size="780,336" font="Regular;20" secondfont="Regular;20"  itemHeight="48" enableWrapAround="1"  scrollbarMode="showOnDemand" transparent="1" />


                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/hd-key_red.png" position="20,e-26" size="6,28" zPosition="1" />
                        <widget source="key_red" render="Label" position="32,e-26" size="150,28" font="Regular;20" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1" />

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/hd-key_green.png"  position="182,e-26" size="6,28" zPosition="1" />
                        <widget source="key_green" render="Label" position="194,e-26" size="150,28" font="Regular;20" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1" />

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/hd-key_yellow.png" position="344,e-26" size="6,28" zPosition="1" />
                        <widget source="key_yellow" render="Label" position="356,e-26" size="150,28" font="Regular;20" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1"/>

                        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SlykEpg7day/images/hd-key_blue.png" position="506,e-26" size="6,28" zPosition="1" />
                        <widget source="key_blue" render="Label" position="518,e-26" size="150,28" font="Regular;20" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" halign="left" zPosition="1"/>

                        <widget name="status" position="40,e-80" size="760,28" font="Regular;30" valign="center" transparent="1" foregroundColor="#6dcff6" />
                    </screen>"""

        Screen.__init__(self, session)
        self.session = session

        if self.runtype == "manual":
            self.skin = skin
            self.setup_title = 'Slyk EPG 7 Day Downloader'

            self.onChangedEntry = []

            self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {
                'cancel': self.cancel,
                'save': self.save,
                'red': self.cancel,
                'green': self.save,
                'yellow': self.manual
            }, -2)

            self['key_red'] = StaticText('Cancel')
            self['key_green'] = StaticText('Save')
            self['key_yellow'] = StaticText('Download')
            self['key_blue'] = StaticText('')

            self['status'] = Label('')
            self['description'] = Label('')

            self.list = []
            ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

            self.initConfig()
            self.createSetup()

            self.pause = 100
            self.running = False

            self.updateTimer = enigma.eTimer()
            self.updateTimer.callback.append(self.updateStatus)
            self.updateTimer.start(1000)

            self.updateStatus()

            self.onLayoutFinish.append(self.__layoutFinished)

        if self.runtype == "auto":
            self.pause = 100
            self.running = False
            self['status'] = Label('')
            self.auto()

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def initConfig(self):
        self.cfg_region = getConfigListEntry('Primary Sky Region'), cfg.region, _('Select the main region for your EPG.')
        self.cfg_enabled = getConfigListEntry('Automatic import Slyk EPG'), cfg.enabled, _('Select to automatically download EPG data daily.')
        self.cfg_wakeup = getConfigListEntry('Automatic start time'), cfg.wakeup, _('Select the daily download time.\nSelect a random unique time and not on the hour like 8:00am.\nHelp prevent server overload.')
        self.cfg_epgDescDays = getConfigListEntry('Load EPG descriptions up to X days'), cfg.epgDescDays, _('Select the maximum number of days you would like to download EPG data for. 1 - 7 days.')
        self.cfg_timeshift = getConfigListEntry('EPG timeshift offset'), cfg.timeshift, _('Adjust the timeshift according to UK Daylight Saving Time and/or your local timezone.\nUK: Summer = 1, Winter = 0')
        self.cfg_lamedb = getConfigListEntry('Use provided Sat 28.2e lamedb file'), cfg.lamedb, _('Select this option if you do not have 28.2e satellite feeds. i.e UK Cable with no satellite/None UK/IPTV only.')
        self.cfg_rytecIDs = getConfigListEntry('XMLTV Channel ID references'), cfg.rytec, _("Select whether to try and match Rytec's original EPG IDs or whether just to create unique IDs for the XMLTV files.")
        self.cfg_compress = getConfigListEntry('Compress XMLTV programme data (slower)'), cfg.compress, _('Select to compress the XMLTV files if harddrive space is limited.')

    def createSetup(self):
        self.list = []
        self.list.append(self.cfg_region)

        self.list.append(self.cfg_enabled)

        if cfg.enabled.value is True:
            self.list.append(self.cfg_wakeup)

        self.list.append(self.cfg_epgDescDays)
        self.list.append(self.cfg_timeshift)
        self.list.append(self.cfg_lamedb)
        self.list.append(self.cfg_rytecIDs)
        self.list.append(self.cfg_compress)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def newConfig(self):
        cur = self["config"].getCurrent()
        if cur == self.cfg_enabled:
            self.createSetup()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.newConfig()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.newConfig()

    def save(self):
        if self.running is True:
            return
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            configfile.save()

    def cancel(self, answer=None):
        if self.running is True:
            return

        if answer is None:
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancel, MessageBox, ('Really close without saving settings?'))
            else:
                self.close()
        elif answer:
            for x in self['config'].list:
                x[1].cancel()

            self.close()

    def clear_caches(self):
        system("echo 1 > /proc/sys/vm/drop_caches")
        system("echo 2 > /proc/sys/vm/drop_caches")
        system("echo 3 > /proc/sys/vm/drop_caches")

    def manual(self):
        if self.running is True:
            return
        self.running = True
        self.clear_caches()

        self.timer = eTimer()
        self.statusDescription = "Reading Lamedb files..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.loadLamedbFile)

    def auto(self):
        self.running = True
        self.clear_caches()
        self.timer = eTimer()
        self.statusDescription = "Reading Lamedb files..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.loadLamedbFile)

    def loadLamedbFile(self):
        self.lamedb = []
        lamedbsat = []
        lamedbfiles = []

        if cfg.lamedb.value is True:
            lamedbfiles = ['/etc/enigma2/lamedb', '/etc/enigma2/SlykEpg7day/lamedb']
        else:
            lamedbfiles = ['/etc/enigma2/lamedb']

        ignorefile = '/etc/enigma2/SlykEpg7day/ignore-list.txt'
        if os.path.isfile(ignorefile):
            with open(ignorefile) as f:
                try:
                    ignorelist = json.load(f)
                except ValueError as e:
                    print(str(e) + '\n******** broken ignore-list.txt file ***********')
                    print('\n******** check ignore-list.txt file with https://jsonlint.com ********')

        satTransponders = []

        for lamedb in lamedbfiles:
            services = False
            transponders = False

            if os.path.isfile(lamedb):

                with open(lamedb, 'r') as f:
                    for line in f:

                        if line.startswith('transponders'):
                            transponders = True
                            continue

                        if transponders:
                            if line.startswith('end'):
                                transponders = False
                                continue

                            line1 = line
                            line2 = next(f)
                            line3 = next(f)

                            dvbline = line1.strip()
                            dataline = line2.strip()

                            # check for 28.2e sat
                            if dataline.startswith('s'):
                                if':282:' in dataline:

                                    dvbline = dvbline.split(':')
                                    namespace = dvbline[0]

                                    if namespace not in satTransponders:
                                        satTransponders.append(namespace)

                        if line.startswith('services'):
                            services = True
                            continue

                        if services:
                            if line.startswith('end'):
                                break

                            line1 = line
                            line2 = next(f)
                            line3 = next(f)

                            DBVStreamData = line1.strip()
                            ChannelName = line2.strip()

                            # normalize channel name
                            piconChannelName = ChannelName

                            if pythonVer == 2:
                                piconChannelName = unicodedata.normalize('NFKD', unicode(piconChannelName, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
                            elif pythonVer == 3:
                                piconChannelName = unicodedata.normalize('NFKD', piconChannelName).encode('ASCII', 'ignore').decode('ascii')

                            piconChannelName = re.sub('[^a-z0-9]', '', piconChannelName.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())

                            # if 28.2e tranpsonder in service line add to list

                            if any(x in DBVStreamData for x in satTransponders):
                                if not ChannelName.isdigit() and ChannelName != "" and ChannelName not in ignorelist and "XXX" not in ChannelName and '2:0:0' not in DBVStreamData and "0x" not in ChannelName:
                                    lamedbsat.append([DBVStreamData, ChannelName, piconChannelName])

            else:
                print("file read error")

        # remove duplicate service refs and sort by channel name
        s = list()
        for sublist in lamedbsat:
            if sublist not in s:
                s.append(sublist)

        lamedbsat = s
        lamedbsat.sort(key=lambda x: x[1])
        del s

        self.lamedb = lamedbsat

        if not os.path.exists('/etc/enigma2/SlykEpg7day/output'):
            os.makedirs('/etc/enigma2/SlykEpg7day/output')

        # write csv output
        with open('/etc/enigma2/SlykEpg7day/output/lamddbsat.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(['DBVStreamData', 'Original Name', 'Picon Name'])
            for item in lamedbsat:
                writer.writerow([item[0], item[1], item[2]])

        with open('/etc/enigma2/SlykEpg7day/output/lamddb.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(['DBVStreamData', 'Original Name', 'Picon Name'])
            for item in self.lamedb:
                writer.writerow([item[0], item[1], item[2]])

        # print("SlykEPG: List of sat namespaces: %s" % (satTransponders))
        # print("SlykEPG: Corresponding Lamedb sat entries: %s" % (len(self.lamedb)))

        self.timer = eTimer()
        self.statusDescription = "Downloading Sky regions data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.downloadRegions)

    def downloadRegions(self):
        response = ''
        # all current regions
        regionsUrl = 'http://epgservices.sky.com/0.0.0/api/2.1/regions/json/'

        try:
            response = urlopen(regionsUrl, timeout=10)
        except Exception as e:
            print(e)
            self.urlList = []
            pass

        downloadRegionList = []

        if response != '':

            bouquet = ''
            subbouquet = ''
            self.regions = json.load(response)
            for region in self.regions['regions']:
                if 'b' in region and 'sb' in region and 't' in region:
                    bouquet = region['b']
                    subbouquet = region['sb']
                    if region['t'] != 'SD':
                        downloadRegionList.append([bouquet, subbouquet])

            self.urlList = ['http://epgservices.sky.com/5.1.1/api/2.1/region/json/%s/%s' % (region[0], region[1]) for region in downloadRegionList]

        self.timer = eTimer()
        self.statusDescription = "Downloading basic channel data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.getJson)

    def fetch_url(self, url, i):
        # print(url[i])
        response = ''
        try:
            response = urlopen(url[i], timeout=10)
        except Exception as e:
            print(e)
            print("***********  url failed % s" % url[i])
            return None

        if response != '':
            return response, url[i]

    def log_result(self, result):
        if result[0] is not None:

            # add in region bouquets IDs and name
            region = result[1].split("/")
            sb = region[-1]
            b = region[-2]

            temp = json.load(result[0])

            for channel in temp['init']['channels']:
                channel['b'] = b
                channel['sb'] = sb

                for region in self.regions['regions']:

                    if str(channel['b']) == str(region['b']) and str(channel['sb']) == str(region['sb']):
                        channel['n'] = region['n'] + " " + region['t']
                        break

            self.channelsBasic.append(temp)
        else:
            print("log_result is none.")

    # use pooling to download json files concurrently for faster downloads.
    def getJson(self):
        self.channelsBasic = []
        urllength = len(self.urlList)

        pool = ThreadPool(8)
        for i in range(urllength):
            pool.apply_async(self.fetch_url, args=(self.urlList, i), callback=self.log_result)

        pool.close()
        pool.join()

        # cleanup
        del self.urlList
        del self.regions

        self.timer = eTimer()
        self.statusDescription = "Combining channel data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.combineJsonFiles)

    def combineJsonFiles(self):
        # print("**** combineJsonFiles ***")
        regionb = regionbouquets.get(cfg.region.value)

        """
        with open('/etc/enigma2/SlykEpg7day/channelsBasic.json', 'w') as f:
            json.dump(self.channelsBasic, f)
            """

        self.channels_all = [channels['init']['channels'] for channels in self.channelsBasic]

        """
        with open('/etc/enigma2/SlykEpg7day/channels_json.json', 'w') as f:
            json.dump(self.channels_all, f)
            """

        # move selected sky region to top of lists.
        x = 0
        for channels in self.channels_all:
            if channels[0]['b'] == str(regionb[0]) and channels[0]['sb'] == str(regionb[1]):
                self.channels_all.insert(0, self.channels_all.pop(x))
                break
            x += 1

        for i in range(len(self.channels_all)):
            self.channels_all[0] = list({x['c'][0]: x for x in self.channels_all[i] + self.channels_all[0]}.values())

        self.channels_all = self.channels_all[0]

        """
        with open('/etc/enigma2/SlykEpg7day/combinedepgdata3.json', 'w') as f:
            json.dump(self.channels_all, f)
            """

        # cleanup
        del self.channelsBasic

        self.timer = eTimer()
        self.statusDescription = "Cleaning Up data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.removeUnusedFields1)

    def removeUnusedFields1(self):
        # print ("****** removeUnusedFields ****")

        for channel in self.channels_all:
            temp1 = channel['c'][0]
            temp2 = channel['t']
            temp3 = channel['lcn']
            temp4 = channel['b']
            temp5 = channel['sb']

            channel.clear()
            channel['sid'] = temp1
            channel['t'] = temp2
            channel['lcn'] = temp3
            channel['b'] = temp4
            channel['sb'] = temp5

            # add new fields
            channel['refs'] = []
            channel['program'] = []

        """
        with open('/etc/enigma2/SlykEpg7day/combinedepgdata4.json', 'w') as f:
            json.dump(self.channels_all, f)
            """

        self.timer = eTimer()
        self.statusDescription = "Building EPG IDs..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.makeEpgID)

    def makeEpgID(self):
        regionb = regionbouquets.get(cfg.region.value)

        for channel in self.channels_all:
            if channel['t'] == "ITV" and channel['b'] == str(regionb[0]) and channel['sb'] == str(regionb[1]):
                channel['primary'] = True
                channel['original'] = channel['t']
                continue

            if channel['t'] == "ITV+1" and channel['b'] == str(regionb[0]) and channel['sb'] == str(regionb[1]):
                channel['primary'] = True
                channel['original'] = channel['t']
                continue

            if channel['t'] == "ITV HD" and channel['b'] == str(regionb[0]) and channel['sb'] == str(regionb[1]):
                channel['primary'] = True
                channel['original'] = channel['t']
                continue

            if channel['t'] == "STV" and channel['sid'] == 6220:
                channel['primary'] = True
                channel['original'] = channel['t']
                continue

            if channel['t'] == "STV HD" and channel['sid'] == 4055:
                channel['primary'] = True
                channel['original'] = channel['t']
                continue

        for channel in self.channels_all:

            # ITV Regions
            if channel['sid'] == 6089:
                channel['t'] = "ITV Anglia East"
            elif channel['sid'] == 1045:
                channel['t'] = "ITV Anglia HD"
            elif channel['sid'] == 6128:
                channel['t'] = "ITV +1 Anglia"
            elif channel['sid'] == 6110:
                channel['t'] = "ITV Border"
            elif channel['sid'] == 1061:
                channel['t'] = "ITV Border England HD"
            elif channel['sid'] == 1020:
                channel['t'] = "ITV Border Scotland"
            elif channel['sid'] == 6381:
                channel['t'] = "ITV Anglia West"
            elif channel['sid'] == 6300:
                channel['t'] = "ITV Central"
            elif channel['sid'] == 6503:
                channel['t'] = "ITV Central West HD"
            elif channel['sid'] == 6145:
                channel['t'] = "ITV +1 Central"
            elif channel['sid'] == 6011:
                channel['t'] = "ITV Central East"
            elif channel['sid'] == 6200:
                channel['t'] = "ITV Channel Isles"
            elif channel['sid'] == 6130:
                channel['t'] = "ITV Granada"
            elif channel['sid'] == 6505:
                channel['t'] = "ITV Granada HD"
            elif channel['sid'] == 6355:
                channel['t'] = "ITV +1 Granada"
            elif channel['sid'] == 6143:
                channel['t'] = "ITV Meridian North"
            elif channel['sid'] == 6142:
                channel['t'] = "ITV Meridian East"
            elif channel['sid'] == 6390:
                channel['t'] = "ITV Tyne Tees"
            elif channel['sid'] == 1043:
                channel['t'] = "ITV Tyne Tees HD"
            elif channel['sid'] == 6126:
                channel['t'] = "ITV +1 Tyne Tees"
            elif channel['sid'] == 6020:
                channel['t'] = "ITV Wales"
            elif channel['sid'] == 6501:
                channel['t'] = "ITV Wales HD"
            elif channel['sid'] == 6012:
                channel['t'] = "ITV +1 Wales"
            elif channel['sid'] == 6030:
                channel['t'] = "ITV West"
            elif channel['sid'] == 1063:
                channel['t'] = "ITV Westcountry West HD"
            elif channel['sid'] == 6127:
                channel['t'] = "ITV +1 West"
            elif channel['sid'] == 6040:
                channel['t'] = "ITV West Country"
            elif channel['sid'] == 1062:
                channel['t'] = "ITV Westcountry SW HD"
            elif channel['sid'] == 6125:
                channel['t'] = "ITV +1 West Country"
            elif channel['sid'] == 6140:
                channel['t'] = "ITV Meridian South"
            elif channel['sid'] == 6502:
                channel['t'] = "ITV Meridian South HD"
            elif channel['sid'] == 6365:
                channel['t'] = "ITV +1 Meridian"
            elif channel['sid'] == 6161:
                channel['t'] = "ITV Yorkshire East"
            elif channel['sid'] == 1044:
                channel['t'] = "ITV Yorkshire HD"
            elif channel['sid'] == 6065:
                channel['t'] = "ITV +1 Yorkshire"
            elif channel['sid'] == 6160:
                channel['t'] = "ITV Yorkshire West"
            elif channel['sid'] == 6000:
                channel['t'] = "ITV London"
            elif channel['sid'] == 6504:
                channel['t'] = "ITV London HD"
            elif channel['sid'] == 6155:
                channel['t'] = "ITV +1 London"

            # STV Regions
            elif channel['sid'] == 6325:
                channel['t'] = "STV Dundee"
            elif channel['sid'] == 1167:
                channel['t'] = "STV Dundee HD"
            elif channel['sid'] == 6210:
                channel['t'] = "STV Grampian"
            elif channel['sid'] == 1168:
                channel['t'] = "STV Grampian HD"
            elif channel['sid'] == 6371:
                channel['t'] = "STV Scotland East"
            elif channel['sid'] == 1170:
                channel['t'] = "STV Scotland East HD"
            elif channel['sid'] == 6220:
                channel['t'] = "STV Scotland West"
            elif channel['sid'] == 4055:
                channel['t'] = "STV Scotland West HD"

            # self.epgid = channel['t'].encode('utf8')

            # normalize channel name

            self.epgid = str(channel['t'])

            if pythonVer == 2:
                self.epgid = unicodedata.normalize('NFKD', unicode(self.epgid, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
            elif pythonVer == 3:
                self.epgid = unicodedata.normalize('NFKD', self.epgid).encode('ASCII', 'ignore').decode('ascii')

            self.epgid = re.sub('[^a-z0-9]', '', self.epgid.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())

            # match rytec extensions
            if cfg.rytec.value == 'rytec':

                if channel['t'] == 'Adult Channel' or channel['t'] == 'Television X HD':
                    self.epgid = '%s.ero' % self.epgid

                elif channel['t'] == '3e' or channel['t'] == 'eir Sport 1 HD' or channel['t'] == 'eir Sport 2 HD' or channel['t'] == 'RTÉ One' or channel['t'] == 'RTÉ2' \
                    or channel['t'] == 'RTÉ One+1' or channel['t'] == 'RTÉ News Now' or channel['t'] == 'RTÉjr' or channel['t'] == 'RTÉ2 HD' or channel['t'] == 'RTÉ One HD' \
                        or channel['t'] == 'TG4 HD' or channel['t'] == 'TG4':
                    self.epgid = '%s.ie' % self.epgid

                elif channel['t'] == 'Al Jazeera Eng' or channel['t'] == 'Al Jazeera HD' or channel['t'] == 'BBC NEWS' or channel['t'] == 'BBC NEWS HD' \
                        or channel['t'] == 'Bloomberg HD' or channel['t'] == 'CNN HD' or channel['t'] == 'CNN' or channel['t'] == 'TRT World HD' or channel['t'] == 'TRT World':
                    self.epgid = '%s.nws' % self.epgid

                elif channel['t'] == 'Arirang TV HD':
                    self.epgid = '%s.kr' % self.epgid

                elif channel['t'] == 'CGTN HD' or channel['t'] == 'CGTN':
                    self.epgid = '%s.cn' % self.epgid

                elif channel['t'] == 'FRANCE 24 HD':
                    self.epgid = '%s.fr' % self.epgid

                elif channel['t'] == 'NHK World HD':
                    self.epgid = '%s.jp' % self.epgid

                elif channel['t'] == 'EWTN Catholic' or channel['t'] == 'GOD Channel' or channel['t'] == 'MTV MUSIC' or channel['t'] == 'Record TV HD':
                    self.epgid = '%s.eu' % self.epgid

                else:
                    self.epgid = '%s.uk' % self.epgid

            else:
                # use unique slyk id extension
                self.epgid = '%s.slyk' % self.epgid

            channel['ID'] = self.epgid

        self.timer = eTimer()
        self.statusDescription = "Adding Lamedb service refs to EPG data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.addLamedbRefToChannelsJson)

    def addLamedbRefToChannelsJson(self):
        # print("***** addLamedbRefToChannelsJson *****")
        # load regional-refs
        manualrefslist = []
        if os.path.isfile('/etc/enigma2/SlykEpg7day/manual-refs.txt'):
            with open('/etc/enigma2/SlykEpg7day/manual-refs.txt') as f:
                try:
                    manualrefslist = json.load(f)
                except ValueError as e:
                    print(str(e) + '\n******** broken regional-refs.txt ***********')
                    print('\n******** check /etc/enigma2/SlykEpg7day/manual-refs.txt file with https://jsonlint.com ********')

        for channel in self.channels_all:
            if channel['t'] in manualrefslist:
                if manualrefslist[channel['t']] not in channel['refs']:
                    channel['refs'].append(manualrefslist[channel['t']])
                    channel['manual'] = True

        try:
            for channel in self.channels_all:

                if 'manual' in channel and 'primary' not in channel:
                    if channel['manual'] is True:
                        continue
                else:
                    piconname = str(channel['t'])

                    if pythonVer == 2:
                        piconname = unicodedata.normalize('NFKD', unicode(piconname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
                    elif pythonVer == 3:
                        piconname = unicodedata.normalize('NFKD', piconname).encode('ASCII', 'ignore').decode('ascii')

                    piconname = re.sub('[^a-z0-9]', '', piconname.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())

                    for line in self.lamedb:
                        if line[2] == "itv" and "ffff0000" in str(line[0]) and "primary" in channel:
                            if channel['original'] == "ITV":
                                if line[0] not in channel['refs']:
                                    channel['refs'].append(line[0])

                        if line[2] == "itvhd" and "ffff0000" in str(line[0]) and "primary" in channel:
                            if channel['original'] == "ITV HD":
                                if line[0] not in channel['refs']:
                                    channel['refs'].append(line[0])

                        if line[2] == "itvplus1" and "ffff0000" in str(line[0]) and "primary" in channel:
                            if channel['original'] == "ITV+1":
                                if line[0] not in channel['refs']:
                                    channel['refs'].append(line[0])

                        if line[2] == "stv" and "ffff0000" in str(line[0]) and "primary" in channel:
                            if channel['original'] == "STV":
                                if line[0] not in channel['refs']:
                                    channel['refs'].append(line[0])

                        if line[2] == "stvhd" and "ffff0000" in str(line[0]) and "primary" in channel:
                            if channel['original'] == "STV HD":
                                if line[0] not in channel['refs']:
                                    channel['refs'].append(line[0])

                        if piconname == line[2]:
                            if line[0] not in channel['refs']:
                                channel['refs'].append(line[0])
                                break

                        # catch some older channel names
                        if piconname == 'skygreats' and line[2] == 'skysuperhero':
                            if line[0] not in channel['refs']:
                                channel['refs'].append(line[0])
                                break

                        if piconname == 'skygreatshd' and line[2] == 'skysuperherohd':
                            if line[0] not in channel['refs']:
                                channel['refs'].append(line[0])
                                break

                        if piconname == 'truestories' and line[2] == 'skydrama':
                            if line[0] not in channel['refs']:
                                channel['refs'].append(line[0])
                                break

                        if piconname == 'trueStorieshd' and line[2] == 'skydramahd':
                            if line[0] not in channel['refs']:
                                channel['refs'].append(line[0])
                                break
        except Exception as e:
            print(e)
        # cleanup

        del self.lamedb

        """
        ###################################################################################
        with open('/etc/enigma2/SlykEpg7day/combinedepgdata6.json', 'w') as f:
            json.dump(self.channels_all, f)
            """

        # example output
        # {"c": [3147, 507, 16, 1], "refs": ["cf9b:011a0000:083a:0002:25:0:0"], "program": [], "t": "NHK World HD", "ID": "nhkworldhd.slyk"}

        self.timer = eTimer()
        self.statusDescription = "Downloading full channel data..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.getChannelRefList)

    def getChannelRefList(self):
        print("**** getChannelRefList ****")
        # create lists of all the channel numbers
        self.channelRefs = [channel['sid'] for channel in self.channels_all if 'sid' in channel]

        # example output
        # [3147, 1836, 1333, 3206, 3620, 6241, 1019, 1035, 4063, 3753, 5701, 3414, .... ]

        # print("unique sids %s " % self.channelRefs)

        self.timer = eTimer()
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.createEPGDataChunks)

    def create_chunks(self, list_name, n):
        # print("***** create_chunks ****")
        for i in range(0, len(list_name), n):
            yield list_name[i:i + n]

    def fetch_url2(self, url, i):
        # print(url[i])
        response = ''
        try:
            response = urlopen(url[i], timeout=20)
            return json.load(response)

        except Exception as e:
            print(e)
            print("***********  url failed % s" % url[i])
            pass
            return None

        """
        if response != '':
            return json.load(response)
            """

    def log_epg_result(self, result):

        if result is not None:
            # remove unnecessary fields

            if 'channels' in result:
                if isinstance(result['channels'], dict):
                    templist = []
                    templist.append(result['channels'])
                    result['channels'] = templist

                for channel in result['channels']:

                    if 'program' in channel:
                        if isinstance(channel['program'], dict):
                            # print("**** program data was dict ****")
                            # print(channel['channelid'])
                            channel['program'] = [channel['program']]

                        if 'channeltype' in channel:
                            del channel['channeltype']

                        if 'genre' in channel:
                            del channel['genre']

                        for event in channel['program']:

                            start = ''
                            dur = ''
                            ptitle = ''
                            shortDesc = ''

                            if 'start' in event:
                                start = str(event['start'])
                            if 'dur' in event:
                                dur = str(event['dur'])
                            if 'title' in event:
                                ptitle = str(event['title'])
                            if 'shortDesc' in event:
                                shortDesc = str(event['shortDesc'])

                            event.clear()
                            event['start'] = start
                            event['dur'] = dur
                            event['title'] = ptitle
                            event['shortDesc'] = shortDesc

                    else:
                        print("program missing")
                        print(json.dumps(result))

                try:
                    self.result_list.append(result)
                except ValueError as e:
                    print(e)
                    pass
                except Exception as e:
                    print(e)
                    pass

                for channel in self.channels_all:
                    for entry in self.result_list:
                        for x in entry['channels']:
                            if x['channelid'] == str(channel['sid']):
                                channel['program'].append(x['program'])
                                # del x
                                break

                self.result_list = []

            else:
                print("channels missing")

        else:
            print("log_epg_result. download error")

    def createEPGDataChunks(self):
        # print("*** createEPGDataChunks ***")
        self.EPGUrlDownloadList = []
        #  maximum of 20 channels data can be downloaded at once so chunk channel lists into batches of 20.
        channelChunkRefs = []
        channelChunkRefs = list(self.create_chunks(self.channelRefs, 10))
        channelChunkRefsLength = len(channelChunkRefs)

        # print("channelChunkLength %s" % channelChunkRefsLength)
        # print("channelChunkRefs %s" %   channelChunkRefs)

        for c in range(0, channelChunkRefsLength):

            for d in range(0, int(cfg.epgDescDays.value)):

                # strip the [] from the list of chunked channels
                channels = (",".join(str(e) for e in channelChunkRefs[c]))

                epgtime = datetime.date.today() + datetime.timedelta(days=d)
                duration = 60 * 24   # 1 day

                epgtime = epgtime.strftime('%Y%m%d%H%M')  # yyyymmddhhmm

                # example output
                # http://epgservices.sky.com/tvlistings-proxy/TVListingsProxy/tvlistings.json?channels=2002,2003&time=201905192100&dur=1440&detail=2'
                url = 'http://epgservices.sky.com/tvlistings-proxy/TVListingsProxy/tvlistings.json?channels=%s&time=%s&dur=%s&detail=2' % (channels, epgtime, duration)
                self.EPGUrlDownloadList.append(url)

        with open('/etc/enigma2/SlykEpg7day/epgurllist.json', 'w') as f:
            json.dump(self.EPGUrlDownloadList, f)

        # cleanup
        del self.channelRefs

        self.timer = eTimer()
        self.statusDescription = "Downloading individual programme schedules..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.downloadEPGdata)

    def downloadEPGdata(self):
        print("*** downloadepgdata ***")
        # self.count = 0
        urllength = len(self.EPGUrlDownloadList)
        self.result_list = []
        pool = ThreadPool(20)

        for i in range(0, urllength):
            pool.apply_async(self.fetch_url2, args=(self.EPGUrlDownloadList, i), callback=self.log_epg_result)

        # results = pool.imap_unordered(self.fetch_url2, self.EPGUrlDownloadList)

        """
        for result in results:
            if result:

                if 'channels' in result:
                    if isinstance(result['channels'], dict):
                        templist = []
                        templist.append(result['channels'])
                        result['channels'] = templist

                    for channel in result['channels']:

                        if 'program' in channel:

                            if isinstance(channel['program'], dict):
                                print("**** program data was dict ****")
                                print(channel['channelid'])
                                channel['program'] = [channel['program']]

                            if 'channeltype' in channel:
                                del channel['channeltype']

                            if 'genre' in channel:
                                del channel['genre']

                            for event in channel['program']:
                                start = ''
                                dur = ''
                                title = ''
                                shortDesc = ''
                                if 'start' in event:
                                    start = event['start'].encode('utf8')
                                if 'dur' in event:
                                    dur = event['dur'].encode('utf8')
                                if 'title' in event:
                                    ptitle = event['title'].encode('utf8')
                                if 'shortDesc' in event:
                                    shortDesc = event['shortDesc'].encode('utf8')

                                event.clear()

                                event['start'] = start
                                event['dur'] = dur
                                event['title'] = ptitle
                                event['shortDesc'] = shortDesc

                        else:
                            print("program missing")
                            print(json.dumps(result))

                    try:
                        self.result_list.append(result)
                    except ValueError as e:
                        print(e)
                        pass
                    except Exception as e:
                        print(e)
                        pass

                    for channel in self.channels_all:
                        for entry in self.result_list:
                            for x in entry['channels']:
                                if x['channelid'] == str(channel['sid']):
                                    channel['program'].append(x['program'])
                                    # del x
                                    break

                    self.result_list = []

                else:
                    print("channels missing")

            else:
                print("log_epg_result. download error")
                """

        pool.close()
        pool.join()

        self.timer = eTimer()
        self.statusDescription = "Building XMLTV channel file..."
        self.updateStatus()
        self.timer.start(self.pause, 1)

        self.timer.callback.append(self.buildXMLTVChannelFile)

    def purge(self, dir, pattern):
        for f in os.listdir(dir):
            file_path = os.path.join(dir, f)
            if os.path.isfile(file_path):
                if re.search(pattern, f):
                    os.remove(file_path)

    def buildXMLTVChannelFile(self):
        print(" *** buildxmltvchannelfile ***")

        with open('/etc/enigma2/SlykEpg7day/combinedepgdata.json', 'w') as f:
            # print(self.channels_all)
            json.dump(self.channels_all, f)

        # remove old files
        self.purge('/etc/epgimport', 'slykepg7day.xml')
        self.purge('/etc/epgimport', 'slykepg7day.xz')
        self.purge('/etc/epgimport', 'slykepg7day.channels.xml')
        self.purge('/etc/epgimport', 'slykepg7day.sources.xml')

        filepath = '/etc/epgimport/'
        epgfilename = 'slykepg7day.channels.xml'
        channelpath = filepath + epgfilename

        # <!-- 28.2E --><channel id="nhkworldhd.slyk">1:0:19:cf9b:83a:2:11a0000:0:0:0:</channel><!-- NHK World HD -->

        res = "<?xml version='1.0' encoding='utf-8'?>\n"
        res += '<channels>\n'

        for channel in self.channels_all:
            number_of_lamedb_refs = len(channel['refs'])

            for i in range(0, number_of_lamedb_refs):
                serviceref = channel['refs'][i]

                # convert serviceref lamedb format to epgimport format
                serviceref_split = serviceref.split(':')
                if serviceref_split[4] == '25':
                    servicetype = 19
                else:
                    servicetype = 1

                serviceref_switch = '1:0:%s:%s:%s:%s:%s:0:0:0:' % (servicetype, serviceref_split[0].lstrip('0'), serviceref_split[2].lstrip('0'), serviceref_split[3].lstrip('0'), serviceref_split[1].lstrip('0'))

                res += '<!-- 28.2E --><channel id="%s">%s</channel><!-- %s -->\n' % (channel['ID'], serviceref_switch, channel['t'])

        res += "</channels>\n"

        with open(channelpath, 'w') as f:
            f.write(res)

        self.timer = eTimer()
        self.statusDescription = "Building XMLTV source file..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.buildXMLTVSourceFile)

    def buildXMLTVSourceFile(self):
        # print("*** buildxmltvsourcefile ***")
        if not os.path.exists('/etc/epgimport'):
            os.makedirs('/etc/epgimport')

        filepath = '/etc/epgimport/'
        epgfilename = 'slykepg7day.channels.xml'
        channelpath = filepath + epgfilename

        filename = 'slykepg7day.sources.xml'
        sourcepath = filepath + filename

        with open(sourcepath, 'w') as f:
            xml_str = '<?xml version="1.0" encoding="utf-8"?>\n'
            xml_str += '<sources>\n'
            xml_str += '<sourcecat sourcecatname="Slyk EPG 7 day">\n'
            xml_str += '<source type="gen_xmltv" nocheck="1" channels="%s">\n' % (channelpath)
            xml_str += '<description>Slyk EPG 7 day</description>\n'
            if haslzma is False or cfg.compress.value is False:
                xml_str += '<url>/etc/epgimport/slykepg7day.xml</url>\n'
            else:
                xml_str += '<url>/etc/epgimport/slykepg7day.xz</url>\n'
            xml_str += '</source>\n'
            xml_str += '</sourcecat>\n'
            xml_str += '</sources>\n'
            f.write(xml_str)

        self.timer = eTimer()
        self.statusDescription = "Building XMLTV programme schedule file..."
        self.updateStatus()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.buildXMLTVProgramsFile)

    def buildXMLTVProgramsFile(self):
        # print("*** build xmltvprogramsfile ***")

        with open('/etc/enigma2/SlykEpg7day/combinedepgdata.json', 'w') as f:
            json.dump(self.channels_all, f)

        filepath = '/etc/epgimport/'
        epgfilename = 'slykepg7day.xml'
        channelpath = filepath + epgfilename
        xzchannelpath = '/etc/epgimport/slykepg7day.xz'

        res = StringIO()

        res.write("<?xml version='1.0' encoding='utf-8'?>\n")
        res.write('<tv generator-info-name="KiddaC-Slyk EPG 7 Day" generator-info-url="https://www.linuxsat-support.com/board/1462-kiddac-skins/">\n')

        for channel in self.channels_all:

            res.write('  <channel id="%s">\n' % (channel['ID']))
            res.write('    <display-name lang="en"><![CDATA[%s]]></display-name>\n' % (channel['t']))
            res.write('  </channel>\n')

        if haslzma is False or cfg.compress.value is False:
            with open(channelpath, 'a+') as f:
                f.write(res.getvalue())
        else:
            obj = lzma.LZMAFile(xzchannelpath, mode="ab", preset=1)
            obj.write(res.getvalue())
            obj.close()

        channelChunkAll = []
        channelChunkAll = list(self.create_chunks(self.channels_all, 50))
        channelChunkAllLength = len(channelChunkAll)

        for c in range(0, channelChunkAllLength):

            for channel in channelChunkAll[c]:
                res = StringIO()
                if 'program' in channel:
                    for program in channel['program']:
                        for day in program:

                            """
                            if 'title' not in day:
                                print("buildXMLTVProgramsFile title missing")
                                print("current program %s" % json.dumps(day))
                            if 'start' not in day:
                                print("buildXMLTVProgramsFile start missing")
                                print("current program %s" % json.dumps(day))
                            if 'dur' not in day:
                                print("buildXMLTVProgramsFile dur missing")
                                print("current program %s" % json.dumps(day))
                            if 'shortDesc' not in day:
                                print("buildXMLTVProgramsFile shortDesc missing")
                                print("current program %s" % json.dumps(day))
                                """

                            timeshift = cfg.timeshift.value * 100
                            if timeshift < 0:
                                plusone = "-0%s" % (timeshift)
                            else:
                                plusone = "+0%s" % (timeshift)

                            startshort = int(day['start']) / 1000
                            startconvert = datetime.datetime.fromtimestamp(startshort).strftime("%Y%m%d%H%M%S")

                            stopshort = startshort + int(day['dur'])
                            stopconvert = datetime.datetime.fromtimestamp(stopshort).strftime("%Y%m%d%H%M%S")

                            try:
                                start = '%s %s' % (startconvert, plusone)
                                stop = '%s %s' % (stopconvert, plusone)
                            except Exception as e:
                                print(e)

                            res.write('  <programme start="%s" stop="%s" channel="%s">\n' % (start, stop, channel['ID']))
                            res.write('    <title lang="en"><![CDATA[%s]]></title>\n' % (day['title']))
                            res.write('    <desc lang="en"><![CDATA[%s]]></desc>\n' % (day['shortDesc']))
                            res.write('  </programme>\n')

                else:
                    print("buildXMLTVProgramsFile program missing")

                if haslzma is False or cfg.compress.value is False:
                    with open(channelpath, 'a+') as f:
                        f.write(res.getvalue())
                else:
                    obj = lzma.LZMAFile(xzchannelpath, mode="ab", preset=1)
                    obj.write(res.getvalue())
                    obj.close()

        res = "</tv>\n"

        if haslzma is False or cfg.compress.value is False:
            with open(channelpath, 'a+') as f:
                f.write(res)
        else:
            obj = lzma.LZMAFile(xzchannelpath, mode="ab", preset=1)
            obj.write(res)
            obj.close()

        self.finished()

    def updateStatus(self):
        text = "Status: ---"
        if self.running:
            text = "Status: %s" % (self.statusDescription)
        self["status"].setText(text)

    def finished(self):
        del self.channels_all
        configfile.save()
        self.session.openWithCallback(self.done, MessageBox, 'Finished: Set your sources in EPG Importer plugin.\nUncheck UK Rtyec and select SlykEPG.', MessageBox.TYPE_INFO, timeout=30)
        self.running = False

    def done(self, answer=None):
        self.clear_caches()
        self.close()
