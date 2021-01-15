# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 15:58:46 2020

@author: gogliom
"""


#https://github.com/LouisdeBruijn/Medium/blob/master/PDF%20retrieval/pdf_retrieval.py 

#questo modo di portar dentro il pdf (alla fine, sotto elements) sembra spacchettare i pdf in base
#ai paragrafi e tira fuori i titoli dei paragrafi.
#Si può usare per tirar fuori nome offerta (prendendo i casi con "h1") ma si può provare 
# anche per le altre cose per cercare di non passare da un paragrafo all'altro



from operator import itemgetter
import fitz
import json
import pandas as pd
import re
import os
import numpy as np

def fonts(doc, granularity=False):
    """Extracts fonts and their usage in PDF documents.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param granularity: also use 'font', 'flags' and 'color' to discriminate text
    :type granularity: bool
    :rtype: [(font_size, count), (font_size, count}], dict
    :return: most used fonts sorted by count, font style information
    """
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles



def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: texts with pre-prended element tags
    """
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s

                    # new block started, indicating with a pipe
                    block_string += "|"

                header_para.append(block_string)

    return header_para



def font_tags(font_counts, styles):
    """Returns dictionary with font sizes as keys and tags as value.
    :param font_counts: (font_size, count) for all fonts occuring in document
    :type font_counts: list
    :param styles: all styles found in the document
    :type styles: dict
    :rtype: dict
    :return: all element tags based on font-sizes
    """
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def main_Pdf_WithStructure(directory, filename):

    Doc = fitz.open(os.path.join(directory, filename))

    font_counts, styles = fonts(Doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(Doc, size_tag)

    return elements 



def Name(directory, filename):
    Structure = main_Pdf_WithStructure(directory, filename)
    Structure = pd.DataFrame(Structure,columns=['text'])
    
    
    #estraggo i numeri dentro <h>
    r1 = '<h\d>'
    regex = [r1]
    
    regex = re.compile('|'.join(regex))
    Structure['Tag'] = Structure.apply(lambda row: regex.findall(row.text), axis = 1) 
    
    Structure['TagNum'] = Structure.apply(lambda row: str(row.Tag)[4:5], axis = 1)

    Structure['text'] = Structure.apply(lambda row: row.text.upper(), axis = 1 )
    #faccio pulizie 
    Structure['text'] = Structure.apply(lambda row: row.text[4:], axis = 1)

    #in alcuni casi (es sinergas) la denominazione offerta commerciale non è in un "<h>", ma in un <p> --> cmq la tengo e gli do valore basso
    Structure = Structure[(Structure['TagNum']!='') | (Structure['text'].str.contains("NOMINAZIONE OFFERTA COMMERCIALE"))]    
    Structure['TagNum'] = np.where(Structure['text'].str.contains("NOMINAZIONE OFFERTA COMMERCIALE"), 0, Structure['TagNum'])
    
    #se inizia con OFFERTA abbasso il tagnum (esempio OFFERTA GREEN LUCE)!
    #anche se contiene offerta lo faccio (ma meno)
    Structure['Start'] = Structure.apply(lambda row: row.text[0:7], axis = 1)
    Structure['StartOfferta'] =  np.where(Structure['Start'] == "OFFERTA", 4, 0)
    Structure['ContainsOfferta'] =  np.where(Structure['text'].str.contains("OFFERTA"), 0, 0)
    Structure['Denominazione'] = np.where(Structure['text'].str.contains('DENOMINAZIONE OFFERTA COMMERCIALE'),2,0)

    #se troppo Lungo penalizzo 
    Structure['Len'] = Structure.apply(lambda row: len(row.text), axis = 1)
    Structure['TooLong'] = np.where(Structure['Len'] > 40, -3, 0)
    
    #se non è tra il primo 20% dei record in alto (in alto), penalizzo
    #Structure = Structure.reset_index()
    Structure['Posizione'] = 0
    Soglia = round(len(Structure) / 5)
    Structure.loc[Structure.index[:Soglia], 'Posizione'] = 1

    Structure['TagNum'] = Structure.apply(lambda row: int(row.TagNum) - row.StartOfferta - row.ContainsOfferta - row.Denominazione - row.Posizione - row.TooLong, axis = 1)


    
    d1 = '\d\d\\\d\d\\\d{2,4}'   #10\10\20 oppure 10\10\2020
    d2 = '\d\d/\d\d/\d{2,4}'     #10/10/20 oppure 10/10/2020
    d3 = '\d\d\\\d\d\\\d{2,4}.AL.\d\d\\\d\d\\\d{2,4}'  #10\10\20 AL 20\20\20 (con anni anche a 4)
    d4 = '\d\d/\d\d/\d{2,4}.AL.\d\d/\d\d/\d{2,4}'     #10/10/20 AL 20/20/20 (con anni anche a 4)
    
    v1 = '\d+\,?\d+'
    
    d = [d4, d3 ,d1, d2, v1]   #le regex potrebbero essere sovrapposte,metto prima 
                            #le più lunghe così se prende quelle si ferma a quella  --> SI DOVREBBE GESTIRE MEGLIO

    regexD = re.compile('|'.join(d))
    
    Structure = Structure[~Structure['text'].str.contains(regexD, na = False)]
    Structure = Structure[~Structure['text'].str.contains("FAC-SIMILE")]
    Structure = Structure[~Structure['text'].str.contains("FACSIMILE")]
    Structure = Structure[~Structure['text'].str.contains("FAC SIMILE")]    
    Structure = Structure[~Structure['text'].str.contains("KWH")]
    Structure = Structure[~Structure['text'].str.contains("800 ")]
    Structure = Structure[~Structure['text'].str.contains("ACQUISTI PER TE")]
    Structure = Structure[~Structure['text'].str.contains("DOVE TROVARCI")]
    Structure = Structure[~Structure['text'].str.contains("SCHEDA DI CONFRONTABILI")]
    Structure = Structure[~Structure['text'].str.contains("SERVIZI AGGIUNTIVI E PROMOZIONI")]
    Structure = Structure[~Structure['text'].str.contains("PROPOSTA DI FORNITURA PER UTENZE DOMESTICHE")]
    
    

    
    Structure['text'] = Structure['text'].str.replace('  ',' ')
    Structure['text'] = Structure['text'].str.replace('CONDIZIONI ECONOMICHE','')
    Structure['text'] = Structure['text'].str.replace('CONDIZIONI TECNICO ECONOMICHE','')
    Structure['text'] = Structure['text'].str.replace("SCHEDA DI CONFRONTABILITA'",'')
    Structure['text'] = Structure['text'].str.replace("|",'')
    Structure['text'] = Structure['text'].str.replace("ENERGIA ELETTRICA",'')
    Structure['text'] = Structure['text'].str.replace("GAS NATURALE",'')
    Structure['text'] = Structure['text'].str.replace("DENOMINAZIONE COMMERCIALE:",'')
    Structure['text'] = Structure['text'].str.replace("DENOMINAZIONE OFFERTA COMMERCIALE:",'')
    Structure['text'] = Structure['text'].str.replace("OFFERTA",'')
    Structure['text'] = Structure['text'].str.replace(":",'')
    Structure['text'] = Structure['text'].str.replace("ENOMINAZIONE",'')
    Structure['text'] = Structure['text'].str.replace("COMMERCIALE",'')
    Structure['text'] = Structure['text'].str.replace("SCHEDA PRODOTTO",'')
    Structure['text'] = Structure['text'].str.replace("ALLEGATO A",'')
    Structure['text'] = Structure['text'].str.replace("ALLEGATO B",'')
    Structure['text'] = Structure['text'].str.replace("CONDIZIONI PARTICOLARI DI FORNITURA",'')
    Structure['text'] = Structure['text'].str.replace("CONDIZIONI DI FORNITURA",'')
    
    
    
    
    Structure['App'] = Structure.apply(lambda row: len(row.text.replace(" ","")), axis = 1)
    Structure = Structure[Structure['App'] > 2]
  
    
    Structure = Structure[Structure['text']!= ""]
    

    Structure = Structure[Structure.TagNum == Structure.TagNum.min()]

    Structure.sort_values(['Len'], ascending=[True])
    Structure = Structure.nsmallest(1, 'TagNum', keep = 'last')   #in base al sort di prima, prendo quello più lungo 
   
    #modifiche puntuali su Engie (nome offerta è un'immagine)
    if "223_E3" in filename:
        Structure['text'] = "Energia 3.0" 
        
        
    return Structure['text']    
