# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 18:57:18 2021

@author: gogliom
"""


import pandas as pd
import re
from ProvePDF import convert_pdf_to_txt

def Promozioni(Doc):

    ListaPromo = []
    
    KeyWords = ["REGALO", "REGALI", "VOUCHER", "PREMIO", "PREMI", "PROMOZIONE", "PROMOZIONI", "REGOLAMENTO", "CONCORSO", 
                "OPERAZIONE A PREMI", "MANIFESTAZIONE A PREMI", "INZIATIVA", "BUONO", "AMAZON", "GIFT CARD", "FEDELTA'", 
                "RISPARMIO", "PROGRAMMA FEDELTA'", "PROGRAMMA", "VANTAGGIO", "NOVITA'"]
 
    
    
    
  
    for ww in Doc.split(): 
        for kk in KeyWords:
            if ww == kk:
        
               ListaPromo.append(ww) 
    
    ListaPromo = list(dict.fromkeys(ListaPromo))
    
    
    return ListaPromo 

