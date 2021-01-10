# -*- coding: utf-8 -*-
"""
Created on Wed May 27 19:07:03 2020

@author: gogliom
"""

#https://towardsdatascience.com/create-a-multipage-dash-application-eceac464de91




import dash_bootstrap_components as dbc
import dash_html_components as html


def Navbar():
     navbar = dbc.NavbarSimple(
         [ 
             html.A(
                 dbc.Row(
                     [
                         dbc.Col(html.Img(
                             src="https://images.squarespace-cdn.com/content/v1/5c4b26bb9f87705e624581de/1550421050367-PQYFKQM5AURWX0LLIX9Z/ke17ZwdGBToddI8pDm48kFCzQVAOMm3aybOFU8RXwRoUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYy7Mythp_T-mtop-vrsUOmeInPi9iDjx9w8K4ZfjXt2dgLc23v6ne8lCZ0tjGTRrCPJTJHBxQB4HXmWlMRYygl4CjLISwBs8eEdxAxTptZAUg/Jakala_logo_4col_gradient.png"
                            , style = {
                                 'height': '110%', 'width':'65%',
                                        'float': 'left'
                            })),
                         dbc.Col(dbc.NavItem(dbc.NavLink("Home", href="/home"))),
                         dbc.Col(dbc.NavItem(dbc.NavLink("Test!", href="/CaricaFile"))),
                         
                    ],),style = {'width': '100%' } , ) 
                     ],#color = 'rgb(5, 40, 80)'  #'#052850' perchè non prende colore?!?!
                                 
)
     
     return navbar
 
