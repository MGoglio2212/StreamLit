# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:35:21 2020

@author: gogliom
"""

'''
Doc = convert_pdf_to_txt( r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\EnelLuce30.pdf")
Doc = Doc.upper()
      
'''

##### BISOGNA IMPORTARE FUNZIONE CONVERT_PDF_TO_TEXT DA ALTRO PROGRAMMA!

import pandas as pd
import re
from ProvePDF import convert_pdf_to_txt
import numpy as np

def Durata(Doc):

    PossiblePrice = []
    Base = []
    
    #Doc = convert_pdf_to_txt(Doc)
    #Doc = Doc.upper()
    
    #le inserisco come regular expression perchè mettendo . come any character (spezi,"E", a capo..)
    r1 = 'DURATA'
    r2 = 'VALIDIT'
    r3 = 'RINNOV'
    r4 = 'PER.{,5}MESI'
    r5 = 'PER.{,5}ANN'
    
    regex = [r1,r2,r3,r4,r5]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
   
    
    #prendo numeri interi (mesi o anni)
    d1 = r'\s\d{1,2}\s'   
    
    
    d = [d1]   #le regex potrebbero essere sovrapposte,metto prima 
                            #le più lunghe così se prende quelle si ferma a quella  --> SI DOVREBBE GESTIRE MEGLIO
    regexNum = re.compile('|'.join(d))
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    PossiblePrice['Price'] = PossiblePrice['Price'].str.extract('(\d+)').astype(int)
    PossiblePrice = PossiblePrice[PossiblePrice['Price'].isin(['1', '2', '3', '4', '6','12','18','24','36'])]
    
    
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
    
    Durata = Base.merge(PossiblePrice, how='outer')
    Durata['dist'] = Durata.apply(lambda row: row.Position - row.PositionBase, axis = 1)
    #FILTRO PER LE DISTANZE POSITIVE (IL NUMERO VIENE DOPO LA PAROLA, OPPURE NEGATIVE MOLTO PICCOLE DOVE QUINDI LA BASE VIENE IMMEDIATAMENTE DOPO )
    Durata = Durata[Durata['dist'] > - 30]
    
    
    
    #verifico se nei 40 caratteri prima o dopo c'è riferimento a mese o anno 
    dur1_m = r'\bMESE\b'
    dur2_m = r'\bMESI\b'
    dur_m = [dur1_m, dur2_m]  
    regexDur_m = re.compile('|'.join(dur_m))

    dur1_a = r'\bANNO\b'
    dur2_a = r'\bANNI\b'
    dur_a = [dur1_a, dur2_a]  
    regexDur_a = re.compile('|'.join(dur_a))


    Durata['Intorno'] = Durata.apply(lambda row: Doc[row.Position-40:row.Position+40], axis = 1)
    Durata['Mese'] = np.where(Durata['Intorno'].str.contains(regexDur_m),1,0)
    Durata['Anno'] = np.where(Durata['Intorno'].str.contains(regexDur_a),1,0)
    
    #filtro per le durata possibili (6, 12, 18, 24 mesi -- 1, 2 anni)
    Dm = Durata[(Durata['Mese'] == 1) & (Durata['Price'].isin(['6','12','18','24']))]
    Da = Durata[(Durata['Anno'] == 1) & (Durata['Price'].isin(['1','2']))]
    Durata = Dm.append(Da)
    
    Durata = Durata.nsmallest(1, 'dist')
    
    if Durata['Anno'].all() == 1:
        Durata['Price'] = Durata['Price'].apply(str) + ' anno'    
    elif Durata['Mese'].all() == 1:
        Durata['Price'] = Durata['Price'].apply(str) + ' mesi'
    else:
        Durata['Price'] = Durata['Price'].apply(str) + ' anno'

    #print(Prezzo)
    return Durata['Price']