# -*- coding: utf-8 -*-
"""
Created on Fri May 29 23:14:14 2020

@author: gogliom
"""

import os
import pandas as pd
os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\App")
Dir = r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte"
#########################



#########################
# SET DI FILTRI COMPLETO PER BANNER A SINISTRA 
#########################

import pandas as pd 
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from datetime import datetime as dt
from dash.dependencies import Input, Output, State

ListaFile = []


for filename in os.listdir(Dir):
    if filename.endswith(".pdf"):
        ListaFile += [filename]
        Default = ListaFile[0]
        

dropdownFile = html.Div([dcc.Dropdown(
    id = 'filename',
    options = [{'label': i,
                 'value': i
                } for i in ListaFile],
                value=Default,
                searchable = True,
                clearable = False,
            placeholder = "Seleziona un file"
            )])

dropdownCommodity = html.Div([dcc.Dropdown(
    id = 'commodity',
    options = [{'label': i,
                 'value': i
                } for i in ['Energia', 'Gas']],
                value='Energia',
                searchable = True,
                clearable = False,
            placeholder = "Seleziona una commodity"
            )])

SelezionaFolder = html.Div([
        html.P("Inserire percorso della cartella da analizzare"),
        dcc.Textarea(   
            id='textarea-state-example',
            
            value='',
            style={'width': '100%', 'height': '50%'},
            ),
        html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
    
    ])

Button = html.Div([
        html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
        ])

def FilterBanner():
    
    FilterBanner = html.Div(
            
            
                             children = [

                             html.P("Seleziona una commodity:",
                                   className="control_label"),
                             html.Div(dropdownCommodity),
                             html.Br(),
                             html.Br(),

                             html.P("Seleziona un file:",
                                   className="control_label"),
                             html.Div(dropdownFile) ,
                             html.Br(),
                             html.P(Button)
                             
                                     ]   
    
                             )
    
     
    return FilterBanner  



def FilterBanner_SelezionaFolder():
    FilterBanner = html.Div(
            
            
                             children = [

                             html.P("Seleziona una commodity:",
                                   className="control_label"),
                             html.Div(dropdownCommodity),
                             html.Br(),
                             html.Br(),

                             html.P("Inserire il percorso da analizzare:",
                                   className="control_label"),
                             html.Div(SelezionaFolder) ,
                             
                                     ]   
    
                             )

    return FilterBanner

