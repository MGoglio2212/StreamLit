# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 20:06:54 2020

@author: gogliom
"""
import re


def ClassifyDoc(Doc):
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
    
