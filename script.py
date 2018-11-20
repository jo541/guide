import re
import feedparser
from datetime import date
from xml.etree.ElementTree import Element, SubElement, ElementTree
import ConfigParser
import os

scriptdir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.ConfigParser()
config.read(os.path.join(scriptdir, 'config.ini'))

# Lecture et recuperation des infos dans le fichier M3U
with open(config.get('File','m3u_path'), 'r+') as file:
    dataForGuid = {}
    dataForChannel = {}
    for line in iter(file.readline, ''):
        if "#EXTINF" in line:
            chanelInformation = re.findall(r'"(.*?)"', line)
            dataForGuid.update({chanelInformation[0]: {'name':chanelInformation[1],'group':chanelInformation[3]}})
            dataForChannel.update({chanelInformation[1]: {'icon': chanelInformation[2], 'id': chanelInformation[0]}})

# Formatage de la date pour le lien
now = date.today().strftime('%d-%m-%Y')
# Recuperation du programme TV sur le flux RSS
tvProgramme = feedparser.parse('https://webnext.fr/epg_cache/programme-tv-rss_%s.xml' % now)

# Object Xml
tv = Element('tv')

# Creation des balises channel
for name, value in dataForChannel.items():
    channel = SubElement(tv, 'channel')
    channel.set('id', value['id'])
    dname = SubElement(channel, 'display-name')
    dname.set('lang', 'fr')
    dname.text = name
    icon = SubElement(channel, 'icon')
    icon.set('src', value['icon'])

# Creation des balises differents balises pour les informations des programmes.
for i, entrie in enumerate(tvProgramme.entries):
    titleSplit = entrie.title.split('|')
    # Recuperation du titre
    if titleSplit:
        title = titleSplit[0].strip()
    else:
        title = ""
    # Creation des programmes pour chaque channel
    for key, value in dataForGuid.items():
        # Recheche du lien entre le flux rss des programme et les chanels repris du M3U
        if title and title.lower().replace(' ', '') in key.lower().replace(' ', ''):
            # Formatage de la date pour la balise
            now = date.today().strftime('%Y%m%d')
            hour, minute = titleSplit[1].strip().split(':')
            if i < len(tvProgramme.entries) :
                hour_to = tvProgramme.entries[i+1].title.split('|')[1].strip()
                hour1, minute1 = hour_to.split(':')
            else:
                hour1, minute1 = [23,59]# L'heure maximum et Minuit
            dateFormated = "%s%s%s%s %s" % (now, hour, minute, '00', '+0100')
            dateFormatedstop = "%s%s%s%s %s" % (now, hour1, minute1, '00', '+0100')
            # Creation de la balise Programme
            programme = SubElement(tv, 'programme')
            programme.set('start', dateFormated)
            programme.set('stop', dateFormatedstop)
            programme.set('channel', key)
            # creation de la baliseTitle
            titleElem = SubElement(programme, 'title')
            titleElem.text = titleSplit[2].strip()
            # creation de la balise Description
            desc = SubElement(programme, 'desc')
            desc.set('lang', 'fr')
            desc.text = entrie.summary
            # Creation de la balise Categorie
            category = SubElement(programme, 'category')
            category.set('lang', 'fr')
            category.text = entrie.category

# Generation du fichier XML
ElementTree(tv).write(config.get('File','xml_path'), encoding='utf-8', xml_declaration=True)


