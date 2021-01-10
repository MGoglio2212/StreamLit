# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 20:06:54 2020

@author: gogliom
"""
import re

### MODIFICA DEL 2 GENNAIO 2021 --> CERCO LE PAROLE SENZA CHE ABBIANO \b prima e dopo (quindi siano separato da boundaries)
### come nella funzione sotto che tieni (xxx)
    


def ClassifyDoc(Doc):
    word = "ENERGIA"
    Count_Energia = 0
    Count_Energia = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    
    word = "LUCE"
    Count_Luce = 0
    Count_Luce = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    word = "KW"
    Count_Kw = 0
    Count_Kw = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    word = "GAS"
    Count_Gas = 0
    Count_Gas = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
            
    word = "SMC"
    Count_Smc = 0
    Count_Smc = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    #se trovo enel energia tolgo da energia (perchè se no anche nelle offerte gas ne trovo sempre)
    word = "ENEL ENERGIA"
    Count_EnelEnergia = 0
    Count_EnelEnergia = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    word = "AUTORITÀ DI REGOLAZIONE PER ENERGIA"
    Count_Autorita = 0
    Count_Autorita = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))
    
    
    word = "MERCATO LIBERO  DELL’ENERGIA"
    Count_Mercato = 0
    Count_Mercato = sum(1 for _ in re.finditer(r'%s' % re.escape(word), Doc))  
    
    
    Energia_Tot = Count_Energia + Count_Kw + Count_Luce - Count_EnelEnergia - Count_Autorita - Count_Mercato
    Gas_Tot = Count_Gas + Count_Smc
             
    if Energia_Tot > Gas_Tot  :
        return "Energia"
    elif Gas_Tot > Energia_Tot :
        return "Gas"
    elif Energia_Tot == Gas_Tot :
        return "Unknown"
    

def xxx(Doc):
    word = "ENERGIA"
    Count_Energia = 0
    Count_Energia = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Doc))
    
    
    word = "LUCE"
    Count_Luce = 0
    Count_Luce = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Doc))
    
    word = "KW"
    Count_Kw = 0
    Count_Kw = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Doc))
    
    word = "GAS"
    Count_Gas = 0
    Count_Gas = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Doc))
            
    word = "SMC"
    Count_Smc = 0
    Count_Smc = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Doc))
    
    Energia_Tot = Count_Energia + Count_Kw + Count_Luce
    Gas_Tot = Count_Gas + Count_Smc
             
    if Energia_Tot > Gas_Tot  :
        return "Energia"
    elif Gas_Tot > Energia_Tot :
        return "Gas"
    elif Energia_Tot == Gas_Tot :
        return "Unknown"