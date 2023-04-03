#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# In[21]:


movement = pd.read_csv('..\pitch_movement.csv')
outcomes = pd.read_csv('..\pitch-arsenal-stats.csv')
arsenal = movement.merge(outcomes,on=['pitcher_id','pitch_type','year'])
#arsenal.to_csv('arsenal.csv')
arsenal.describe()


# In[11]:


#create a header for the streamlit page with an option to filter the data with two select boxes
#users can decide what year they would like to observes as well as what distinct pitch they would like data on

st.header('MLB pitch comp app')

st.write("""
##### Use velocity and movement filters to discover comparable pitches
""")

year_array = arsenal['year'].unique()
selected_year = st.selectbox(
    "What year would you like to observe?", 
    year_array)

pitch_type_array = arsenal['pitch_type_name'].unique()
pitch_type = st.selectbox(
    'Select Pitch:', 
    pitch_type_array)


# In[14]:


#create sliders for pitch velocity and movement components
#use min/max on the data to limit the sliders

min_velo, max_velo=int(arsenal['avg_speed'].min()),int(arsenal['avg_speed'].max()+1)

velo_range = st.slider(
    "Choose Velocity Range", 
    value=(min_velo,max_velo),
    min_value=min_velo,max_value=max_velo)

min_vert, max_vert=arsenal['percent_rank_diff_z'].min(),arsenal['percent_rank_diff_z'].max()

vert_range = st.slider(
    "Choose Rise/Drop % vs. League Average", 
    value=(min_vert,max_vert),
    min_value=min_vert,max_value=max_vert)

min_break, max_break=arsenal['percent_rank_diff_x'].min(),arsenal['percent_rank_diff_x'].max()

break_range = st.slider(
    "Choose Break % vs. League Average",
    value=(min_break,max_break),
    min_value=min_break,max_value=max_break)


# In[7]:


#filter the original data with the constraints applied from the sliders

filtered_pitchers=arsenal[(
    arsenal.year==selected_year) & (
    arsenal.pitch_type_name==pitch_type) & (
    arsenal.avg_speed<velo_range[1]) & (
    arsenal.avg_speed>velo_range[0]) & (
    arsenal.percent_rank_diff_z<vert_range[1]) & (
    arsenal.percent_rank_diff_z>vert_range[0]) & (
    arsenal.percent_rank_diff_x<break_range[1]) & (
    arsenal.percent_rank_diff_x>break_range[0])]

st.table(filtered_pitchers)


# In[24]:


#offer a scatter plot to chart the relationship between the components of a pitch and the results of the pitch

st.header('Outcome analysis')
st.write("""
###### Use the filtered data to plot an outcome statistic vs. velocity or a movement metric
z = vertical movement, x = horizontal movement
""")


fig1_x_axis=['avg_speed','percent_rank_diff_z','percent_rank_diff_x']
fig1_y_axis=['whiff_percent','run_value_per_100','woba']

fig1_x_choice = st.selectbox(
    'Input Metric: ', 
    fig1_x_axis)
fig1_y_choice = st.selectbox(
    'Output Metric: ', 
    fig1_y_axis)

fig1 = px.scatter(
    filtered_pitchers, 
    x=fig1_x_choice, 
    y=fig1_y_choice,
    hover_data=['name'])

fig1.update_layout(
title="<b> {} vs {} </b>".format(fig1_y_choice, fig1_x_choice))

st.plotly_chart(fig1)


# In[13]:


#offer an interactive histogram to let users see how the distribution of outcomes differs by pitch type

st.header('What pitches are getting the results?')
st.write("""
###### Use the full data set to map out a distribution of each pitch type vs. its outcome
""")


fig2_x_axis=fig1_y_axis

fig2_choice = st.selectbox(
    'Outcome Metric: ',
    fig2_x_axis)

fig2 = px.histogram(arsenal, x=fig2_choice, color='pitch_type')

fig2.update_layout(
title="<b> Distribituion of Pitch Types by {} </b>".format(fig2_choice))

st.plotly_chart(fig2)

