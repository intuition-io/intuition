#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re, argparse, sys
import urllib2
#from ConfigParser import SafeConfigParser
from xml.dom import minidom, Node

sys.path.append(..)
from utils.LogSubsystem import LogSubsystem
import sqlite3 as sql
#from Utilities import DatabaseSubSystem
#TODO: use above module

class Rss:
    def __init__(self, name, source, url, logger=None):
        if logger == None:
          logSys = LogSubSystem(__name__, "debug")
          self._logger = logSys.getLog()
        else:
          self._logger = logger
        self.name = name
        self.cpt_cdata = 0
        self.source = source
        self.link = []
        self.title = []
        self.update = []
        self.description = []
        self.language = ''
        self.period = ''
        try:
            url_fd = urllib2.urlopen(url)
        except IOError:
            self._logger.error('** Enable to connect to host: %s' % url)
            sys.exit(1)
        #data_category = re.findall('CDATA(.*?)]\>', content)
        self.cdata_content = re.findall('\<p\>(.*?)\</p\>', url_fd.read())
        url_fd.close()
        url_fd = urllib2.urlopen(url)
        try:
            xml_doc = minidom.parse(url_fd)
            self.root_node = xml_doc.documentElement
        except: 
            self._logger.error('** Parsing rss data retrieved' )
            sys.exit(-1)

    def getChannelInfos(self):
        for node in self.root_node.childNodes:
            if ( node.nodeName == "channel" ):
                for item_node in node.childNodes:
                    self._logger.debug(item_node.nodeName)
                    if (item_node.nodeName != 'item'):
                        self.link.append(self.getText(item_node, 'link', self.link))
                        self.title.append(self.getText(item_node, 'title', self.title))
                        self.update.append(self.getText(item_node, 'lastBuildDate', self.update))
                        self.language = self.getText(item_node, 'language', self.language)
                        self.period = self.getText(item_node, 'sy:updateFrequency', self.period)
                        self.description.append(self.getText(item_node, 'description', self.description))
                        return 0
        return -1

    def getFeeds(self, description="off", link="off", update="off"):
        for node in self.root_node.childNodes:
            if ( node.nodeName == "channel" ):
                for item_node in node.childNodes:
                    if (item_node.nodeName == 'item'):
                        title_tmp = ''
                        link_tmp = ''
                        update_tmp = ''
                        description_tmp = ''
                        old_cpt = self.cpt_cdata
                        for last_child in item_node.childNodes:
                            if (last_child.nodeName == 'description'):
                                    self.cpt_cdata = self.cpt_cdata + 1
                                    description_tmp = self.getText(last_child, 'description', description_tmp)
                            title_tmp = self.getText(last_child, 'title', title_tmp)
                            link_tmp = self.getText(last_child, 'link', link_tmp)
                            update_tmp = self.getText(last_child, 'pubDate', update_tmp)
                        self.title.append(title_tmp)
                        if ( update == "on" ):
                            self.update.append(update_tmp[:-6])
                        if ( link == "on" ):
                            self.link.append(link_tmp)
                        if (old_cpt != self.cpt_cdata) and ( description == "on" ):
                            try:
                                self.description.append(self.cdata_content[self.cpt_cdata-1])
                            except:
                                self.description.append(description_tmp)

    def getText(self, item_node, tag, backup_value):
        text = ''
        temp_text = ''
        old_start = 0
        if (item_node.nodeName == tag):
            for text_node in item_node.childNodes:
                if (text_node.nodeType == Node.TEXT_NODE):
                    text += text_node.nodeValue
            if (len(text)>0):
                for k in re.finditer('\<(.*?)\>|\>', text):
                    temp_text += text[old_start:k.start()]
                    old_start = k.end()
                if (old_start != 0):
                    text = temp_text
                return text
            else:
                return 'no value'
        else:
            return backup_value

    def updateDb(self, database):
        self._logger.info('Updating rss database...')
        table = self.name + 'Rss'
        buffer = 'drop table if exists ' + table
        buffer = buffer.strip()
        self.connection = sql.connect(database)
        with self.connection:
            self.connection.row_factory = sql.Row
            self.cursor = self.connection.cursor()
            self.cursor.execute(buffer)
            buffer = 'create table ' + table + '(id integer primary key, source text, title text, date text, link text, description text)'
            buffer = buffer.strip()
            self.cursor.execute(buffer)
            buffer = 'insert into ' + table + ' values(?, ?, ?, ?, ?, ?)'
            buffer = buffer.strip()
            for i in range(0, len(self.title)):
                data = (i, self.source, self.title[i], self.update[i], self.link[i], self.description[i].strip())
                self.cursor.execute(buffer, data)
