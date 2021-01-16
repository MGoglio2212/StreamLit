# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:25:26 2020

@author: gogliom
"""

######

# CERCO UNA LISTA DI POSSIBILI MODI CON CUI CHIAMARE PREZZO MATERIA PRIMA
# PROVO A RECUPERARE PREZZO MATERIA PRIMA
# CREO UN CARTESIANO E CALCOLO DISTANZA TRA OGNI POSSIBILE COPPIA NOME-PREZZO
# PRENDO VALORE CON DISTANZA MINORE 

#Doc = "D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Energit-Casa-Web.pdf"

import pandas as pd
import re
import numpy as np

def PrezzoComponenteGAS(Doc):
    
    PossiblePrice = []
    Base = []
    
    
    #Doc = convert_pdf_to_txt(Doc)
    #Doc = Doc.upper()
    
    #le inserisco come regular expression perchè non so quanti spazi ci sono e se magari c'è una new line (\s+)
    r1 = 'CORRISPETTIVO\s+GAS'
    r2 = 'COMPONENTE\s+PREZZO\s+ENERGIA'
    r3 = 'PREZZO\s+GAS'
    r4 = 'PREZZO.{0,10}COMPONENTE.{0,10}ENERGIA'
    r5 = 'COMPONENTE\s+GAS'
    r6 = 'PREZZO.{0,10}GAS'
    r7 = 'CORRISPETTIVO\s+PREZZO\s+FISSO'
    r8 = 'SPESA.{0,10}MATERIA.{0,10}GAS.{0,10}NATURALE'
    r9 = 'PREZZO.{0,20}MATERIA.{0,20}PRIMA'
    r10 = 'COSTI.{0,40}MATERIA.{0,20}PRIMA'
    r11 = 'PREZZO.{0,5}NETTO'
    regex = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
       
    
    #prendo i numeri positivi  
    #regexNum1 = r'-?\d*\,.?\d+'
    #regexNum2 = r'-?\d*\..?\d+'
    
    regexNum1 = r'\d+\,.?\d+'
    regexNum2 = r'\d+\..?\d+'
    
    
    regexNum = [regexNum1, regexNum2]
    
    regexNum = re.compile('|'.join(regexNum))
    
    
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    #converto in numero
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri < 1 e positivi
    PossiblePrice = PossiblePrice[(PossiblePrice['Price_NUM'] > 0.04) & (PossiblePrice['Price_NUM'] < 0.5)]
    
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
    Prezzo = Prezzo[Prezzo['dist'] > - 25]
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')
    
    Doc[2000:2200]
    

    return Prezzo['Price_NUM']
    
import regex as re  #ATTENZIONE! DEVO IMPORTARE 3RD PARTY REGEX MODULO PERCHè QUESTO SUPPORTA I "NEGATIVE LOOKAHEAD
                    #DI LUNGHEZZA VARIABILE --> DEVO PRENDERE "VERDE" CHE NON SIA PRECEDUTO DA NUMERO O DA N° E QUESTO 
                    #E' UN NEGATIVE LOOKAHEAD DI LUNGHEZZA VARIABILE CHE VA IN ERRORE SU MODULO STANDARD DI RE
                    #CFR (https://www.reddit.com/r/learnpython/comments/d5g4ow/regex_match_pattern_not_preceded_by_either_of_two/)  


def TipoPrezzo_GAS(Doc):
    # VERIFICO VARIABILITA' PREZZO     
    v1 = r'\bPSV\b'
    v2 = r'^(?=.*\bPREZZO\b)(?=.*\bACQUISTO\b)(?=.*\bGAS\b).*$'
    #v3 = r'^(?=.*\bMERCATO\b)(?=.*\bINGROSSO\b).*$'
    #v4=  r'^(?=.*\bMERCATI\b)(?=.*\bINGROSSO\b).*$'
    v5 = r'\bPFOR\b'
    v6 = r'\bOTC\b'

    
    regexVar = [v1, v2, v5, v6]
    
    regexVar = re.compile('|'.join(regexVar))
    
    PriceExplanation= []
    PriceExplanation = [m.start() for m in regexVar.finditer(Doc)]
    

    '''
    for i in Doc.split('\n'):
        if regexVar.match(i):
            PriceExplanation.append(i)
    '''
    #  VERIFICO SE SI PARLA DI COME VIENE CALCOLATO IL PREZZO DELLA COMPONENTE ENERGIA
    
    f1 = r'(?<!PLACET.{1,30})PREZZ.{1,30}GAS.{1,50}FISS'
    f2 = r'(?<!PLACET.{1,30})PREZZ.{1,30}GAS.{1,50}INVARIABIL'
    f3 = r'(?<!PLACET.{1,30})PREZZO.{1,30}FISSO'
    f4 = r'PREZZO INVARIABILE'
    f5 = r'(?<!SPREAD.{1,130}|PARAMETRO.{1,20})FISS.{1,10}INVARIABIL'
    

    regexFix = [f1, f2, f3, f4, f5]
    
    regexFix = re.compile('|'.join(regexFix))
    
    PriceFix= []
    PriceFix = [m.start() for m in regexFix.finditer(Doc)]
    
    Prezzo = pd.DataFrame(columns = ['TipoPrezzo'])
   
    if len(PriceExplanation) == 0 or len(PriceFix) > 0:
        Prezzo.at[0,'TipoPrezzo'] = 'Fisso'
    else:
        Prezzo.at[0,'TipoPrezzo'] = 'Variabile'

    return Prezzo['TipoPrezzo']



