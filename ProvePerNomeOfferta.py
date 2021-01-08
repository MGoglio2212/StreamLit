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
import pandas as pd
import re
import os
import numpy as np


def Name(Doc):
    Structure = Doc
    Structure = pd.DataFrame(Structure,columns=['text'])
    
    
    #estraggo i numeri dentro <h>
    r1 = '<h\d>'
    regex = [r1]
    
    regex = re.compile('|'.join(regex))
    Structure['Tag'] = Structure.apply(lambda row: regex.findall(row.text), axis = 1) 
    
    Structure['TagNum'] = Structure.apply(lambda row: str(row.Tag)[4:5], axis = 1)
    Structure = Structure[Structure['TagNum']!='']
    
    #faccio pulizie 
    Structure['text'] = Structure.apply(lambda row: row.text.upper(), axis = 1)
    Structure['text'] = Structure.apply(lambda row: row.text[4:], axis = 1)
    
    #se inizia con OFFERTA abbasso il tagnum (esempio OFFERTA GREEN LUCE)!
    #anche se contiene offerta lo faccio (ma meno)
    Structure['Start'] = Structure.apply(lambda row: row.text[0:7], axis = 1)
    Structure['StartOfferta'] =  np.where(Structure['Start'] == "OFFERTA", 4, 0)
    Structure['ContainsOfferta'] =  np.where(Structure['text'].str.contains("OFFERTA"), 1, 0)
    
    #se non è tra il primo 20% dei record in alto (in alto), penalizzo
    #Structure = Structure.reset_index()
    Structure['Posizione'] = 0
    Soglia = round(len(Structure) / 5)
    Structure.loc[Structure.index[:Soglia], 'Posizione'] = 1

    Structure['TagNum'] = Structure.apply(lambda row: int(row.TagNum) - row.StartOfferta - row.ContainsOfferta - row.Posizione, axis = 1)


    
    d1 = '\d\d\\\d\d\\\d{2,4}'   #10\10\20 oppure 10\10\2020
    d2 = '\d\d/\d\d/\d{2,4}'     #10/10/20 oppure 10/10/2020
    d3 = '\d\d\\\d\d\\\d{2,4}.AL.\d\d\\\d\d\\\d{2,4}'  #10\10\20 AL 20\20\20 (con anni anche a 4)
    d4 = '\d\d/\d\d/\d{2,4}.AL.\d\d/\d\d/\d{2,4}'     #10/10/20 AL 20/20/20 (con anni anche a 4)
    
    
    d = [d4, d3 ,d1, d2]   #le regex potrebbero essere sovrapposte,metto prima 
                            #le più lunghe così se prende quelle si ferma a quella  --> SI DOVREBBE GESTIRE MEGLIO

    regexD = re.compile('|'.join(d))
    
    Structure = Structure[~Structure['text'].str.contains(regexD, na = False)]
    Structure = Structure[~Structure['text'].str.contains("FAC-SIMILE")]
    Structure = Structure[~Structure['text'].str.contains("KWH")]
    Structure = Structure[~Structure['text'].str.contains("800 ")]
    

    
    Structure['text'] = Structure['text'].str.replace('CONDIZIONI ECONOMICHE','')
    Structure['text'] = Structure['text'].str.replace('CONDIZIONI TECNICO ECONOMICHE','')
    Structure['text'] = Structure['text'].str.replace("SCHEDA DI CONFRONTABILITA'",'')
    Structure['text'] = Structure['text'].str.replace("|",'')
    Structure['text'] = Structure['text'].str.replace("ENERGIA ELETTRICA",'')
    Structure['text'] = Structure['text'].str.replace("GAS NATURALE",'')
    Structure['text'] = Structure['text'].str.replace("OFFERTA",'')
    Structure['text'] = Structure['text'].str.replace("DENOMINAZIONE COMMERCIALE:",'')
    Structure['text'] = Structure['text'].str.replace(":",'')
    
    Structure['App'] = Structure.apply(lambda row: len(row.text.replace(" ","")), axis = 1)
    Structure = Structure[Structure['App'] > 2]
  
    
    Structure = Structure[Structure['text']!= ""]
    

    Structure = Structure[Structure.TagNum == Structure.TagNum.min()]
    Structure = Structure.head(1)
    

        
    return Structure['text']    
