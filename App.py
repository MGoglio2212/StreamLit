# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 18:36:11 2020

@author: gogliom
"""



import streamlit as st 


start_x = st.sidebar.slider("Start X", value= 24, key='sx')
start_y = st.sidebar.slider("Start Y", value= 332, key='sy')
finish_x = st.sidebar.slider("Finish X", value= 309, key='fx')
finish_y = st.sidebar.slider("Finish Y", value= 330, key='fy')


uploaded_file = st.file_uploader("Choose an image", ["jpg","jpeg","png"]) #image uploader
st.write('Or')
use_default_image = st.checkbox('Use default maze')