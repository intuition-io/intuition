#!/usr/bin/python
# -*- coding: utf8 -*-

import re, argparse, sys
import urllib2
from ConfigParser import SafeConfigParser
from xml.dom import minidom, Node

class Rss:
    def __init__(self, url):
        self.cpt_cdata = 0
        self.link = []
        self.title = []
        self.update = []
        self.language = ''
        self.period = ''
        self.description = []
        try:
            url_fd = urllib2.urlopen(url)
        except IOError:
            print '[ERROR] Enable to connect to host:', url
            sys.exit(1)
        #data_category = re.findall('CDATA(.*?)]\>', content)
        self.cdata_content = re.findall('\<p\>(.*?)\</p\>', url_fd.read())
        url_fd.close()
        url_fd = urllib2.urlopen(url)
        try:
            xml_doc = minidom.parse(url_fd)
            self.root_node = xml_doc.documentElement
        except: 
            print '[ERROR] Parsing rss data retrieved' 
            sys.exit(-1)

    def getChannelInfos(self):
        for node in self.root_node.childNodes:
            if ( node.nodeName == "channel" ):
                for item_node in node.childNodes:
                    print item_node.nodeName
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
