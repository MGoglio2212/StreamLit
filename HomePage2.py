# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 17:23:38 2020

@author: gogliom
"""

import os
os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\App")

print(os.getcwd())

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html



 


import base64
from datetime import date



today = date.today()

image_filename = 'D:\\Altro\\RPA\\Energy\\Iren\\Test CTE\\App\\assets\\ImmagineHome_AppCTE.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

body = html.Div([
    dbc.Row(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={
  'verticalAling':'top',
  'textAlign': 'center',
  'background-image':image_filename,
  'position':'fixed',
  'width':'100%',
  'height':'90%',
  'left':'0px',
}))])


def Navbar():
     navbar = dbc.NavbarSimple(
         [ 
             html.A(
                 dbc.Row(
                     [
                         dbc.Col(html.Img(
                             src="https://images.squarespace-cdn.com/content/v1/5c4b26bb9f87705e624581de/1550421050367-PQYFKQM5AURWX0LLIX9Z/ke17ZwdGBToddI8pDm48kFCzQVAOMm3aybOFU8RXwRoUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYy7Mythp_T-mtop-vrsUOmeInPi9iDjx9w8K4ZfjXt2dgLc23v6ne8lCZ0tjGTRrCPJTJHBxQB4HXmWlMRYygl4CjLISwBs8eEdxAxTptZAUg/Jakala_logo_4col_gradient.png"
                            , style = {
                                 'height': '100%', 'width':'65%',
                                        'float': 'left'
                            })),
                         dbc.Col(dbc.NavItem(dbc.NavLink("Home", href="/home"))),
                         dbc.Col(dbc.NavItem(dbc.NavLink("Test Singolo File", href="/CaricaFile"))),
                         dbc.Col(dbc.NavItem(dbc.NavLink("Test File Multipli", href="/SelezionaCartella"))),

                         
                    ],),style = {'width': '100%', 'vertical-align': 'middle' } , ) 
                     ],#color = 'rgb(5, 40, 80)'  #'#052850' perchè non prende colore?!?!
                 )
     
     return navbar


      
def Homepage2():
    layout = html.Div([
    Navbar(),
    body
    ])
    return layout
