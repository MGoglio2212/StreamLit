# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 22:40:24 2020

@author: gogliom
"""


'''
Doc = convert_pdf_to_txt( r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\AbEnergie6MesiGreenGas.pdf")
Doc = Doc.upper()
      
'''

##### BISOGNA IMPORTARE FUNZIONE CONVERT_PDF_TO_TEXT DA ALTRO PROGRAMMA!

import pandas as pd
import re
from ProvePDF import convert_pdf_to_txt

def CodiceOfferta(Doc):

    #lista di codici che vengono fuori con le regular expression ma che sono sbagliati
    CandidatiErrati = ['REABO-481345', #iscrizione alla camera di commercio di wekiwi
                       'BX100', #sigla in scheda confrontabilità
                       'BOLLETTA2',
                       'F1',
                       'F2',
                       'F3',
                       'F0',
                       'F23',
                       'PF0',
                       'PF1',
                       'PF2',
                       'PF3',
                       'PF23',
                       'MHIEWPR77DBP8DFC6',
                       'C2X1'
                       ]
    
    #prima cerco reg exp con trattini e underscore
    #d1 = '[A-Z]+\d*-*_*\w*\d+\w*'  
    d1 = '[A-Z]+[\d_-]+[A-Z\d_-]+' 
    
    
    d = [d1]  
    regexNum = re.compile('|'.join(d))
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    PossiblePrice = pd.DataFrame(NumberTuples, columns = ['Price', 'Position'])
    
    #filtro però che regex debba avere almeno un numero & un carattere 
    d2_1 = '\d'
    d = [d2_1]  
    regexNum = re.compile('|'.join(d))
    

    PossiblePrice['Num'] = PossiblePrice.apply(lambda row: regexNum.findall(row.Price), axis = 1)
    PossiblePrice = PossiblePrice[PossiblePrice['Num'].astype(bool)]  #filtro via le liste vuote

    d2_2 = '[A-Z]'
    d = [d2_2]  
    regexNum = re.compile('|'.join(d))    

    PossiblePrice['Char'] = PossiblePrice.apply(lambda row: regexNum.findall(row.Price), axis = 1)
    PossiblePrice = PossiblePrice[PossiblePrice['Char'].astype(bool)]

    
    
    #se c'è almeno 1 con underscore o trattini, prendo quello
    PossiblePrice['SpecUnderscore'] = PossiblePrice.apply(lambda row: "_" in row.Price, axis = 1)
    PossiblePrice['SpecTrattino'] = PossiblePrice.apply(lambda row: "-" in row.Price, axis = 1)
    PossiblePrice['Lunghezza'] = PossiblePrice.apply(lambda row: len(row.Price), axis = 1)
    
    PossiblePrice = PossiblePrice[~PossiblePrice['Price'].isin(CandidatiErrati)]
    PossiblePrice = PossiblePrice[~PossiblePrice['Price'].str.contains('SHOP')]
    PossiblePrice = PossiblePrice[PossiblePrice['Lunghezza'] >= 5]
     
    Cod = PossiblePrice[PossiblePrice['SpecUnderscore'] == True].nlargest(1, 'Lunghezza')
    if len(Cod) == 0:   
        Cod = PossiblePrice[PossiblePrice['SpecTrattino'] == True].nlargest(1, 'Lunghezza')
    
        if len(Cod) == 0:
            Cod = PossiblePrice.nlargest(1, 'Lunghezza')

  
  
    return Cod['Price']