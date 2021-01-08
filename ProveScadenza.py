# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:35:21 2020

@author: gogliom
"""

'''
Doc = convert_pdf_to_txt( r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Pdf_Splitted\Acea_Come_Noi_CE_DOM_subset_Gas.pdf")
Doc = Doc.upper()
      
'''

##### BISOGNA IMPORTARE FUNZIONE CONVERT_PDF_TO_TEXT DA ALTRO PROGRAMMA!

import pandas as pd
import re
from ProvePDF import convert_pdf_to_txt

def Scadenza(Doc):

    PossiblePrice = []
    Base = []
    
    #Doc = convert_pdf_to_txt(Doc)
    #Doc = Doc.upper()
    
    #le inserisco come regular expression perchè mettendo . come any character (spezi,"E", a capo..)
    r1 = 'CONDIZIONI.{,40}VALID'
    r2 = 'ADESION.{,10}ENTRO'
    r3 = 'ADESION.{,10}FINO'
    r4 = 'VALID.{,5}FINO'
    r5 = 'SOTTOSCRIVIBIL.{,30}'
    r6 = 'VALID.{,5}DA.{,15}A\s'
    r7 = 'ENTRO IL'
    #r8 = 'DAL\s.{,15}AL\s'
    
    
    
    regex = [r1,r2,r3,r4,r5,r6,r7]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
    
    
    #prendo possibili date
    d1 = '\d\d\\\d\d\\\d{2,4}'   #10\10\20 oppure 10\10\2020
    d2 = '\d\d/\d\d/\d{2,4}'     #10/10/20 oppure 10/10/2020
    d3 = '\d\d\\\d\d\\\d{2,4}.AL.\d\d\\\d\d\\\d{2,4}'  #10\10\20 AL 20\20\20 (con anni anche a 4)
    d4 = '\d\d/\d\d/\d{2,4}.AL.\d\d/\d\d/\d{2,4}'     #10/10/20 AL 20/20/20 (con anni anche a 4)
    
    
    d = [d4, d3 ,d1, d2]   #le regex potrebbero essere sovrapposte,metto prima 
                            #le più lunghe così se prende quelle si ferma a quella  --> SI DOVREBBE GESTIRE MEGLIO
    regexNum = re.compile('|'.join(d))
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    
    
    '''
    APPROCCIO IN BASE AL QUALE CERCO €/KWH E PRENDO PAROLA PRECEDENTE, MA IN ALCUNI CASI NELLE TABELLE NON E ESPLICITATA
    EURO/KWH VICINO AL NUMERO
    ii = 0
    for ww in Doc.split():
        if "€/KWH" in ww or "EURO/KWH" in ww:
            pw = Doc.split()[ii-1]
            po = Doc.find(Doc.split()[ii-1]+" "+Doc.split()[ii])
            nn = pd.DataFrame({'Price': [pw], 'Position': [po]})
            PossiblePrice = PossiblePrice.append(nn) 
            #Positions = Positions + list(ii-1)        
        ii = ii + 1 
    #estraggo i numeri 
    PossiblePrice['Price'] = PossiblePrice.apply(lambda row: re.findall('-?\d*\,.?\d+', str(row.Price)), axis=1)
    #elimino eventuali stringe vuote
    PossiblePrice = PossiblePrice[PossiblePrice['Price'].apply(lambda row: len(row)) > 0]
    '''
    
    
    
    Base['key'] = 0
    PossiblePrice['key'] = 0
    
    Prezzo = Base.merge(PossiblePrice, how='outer')
    Prezzo['dist'] = Prezzo.apply(lambda row: row.Position - row.PositionBase, axis = 1)
    #FILTRO PER LE DISTANZE POSITIVE (IL NUMERO VIENE DOPO LA PAROLA, OPPURE NEGATIVE MOLTO PICCOLE DOVE QUINDI LA BASE VIENE IMMEDIATAMENTE DOPO )
    Prezzo = Prezzo[Prezzo['dist'] > 0]
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')

    
    return Prezzo['Price']