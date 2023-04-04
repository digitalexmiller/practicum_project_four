#!/usr/bin/env python
# coding: utf-8

# # **MLB Pitch Type Analysis**
# 
# ## How velocity and movement effects outcome
# 
# ### This goal of this exercise is to create a web app for users to easily group and display outcomes between pitch types with similar components. The idea is that once a user selects the pitch type, s/he can filter the average pitch by every pitcher by its velocity, horizontal and vertical movement. Once the filters are made, a table of the filtered pitches and a scatterplot of how these pitches perform under various metrics (whiff rate, woba and expected runs/100) will also be made available.
# 
# ### Additionally, a histogram will be made available to display full pitch-types vs. their outcomes.
# 
# #### The velocity slider is a raw number, but the movement sliders are based on a percentage rank of how much each pitch moves based on the pitch type

# In[1]:


#import relevant libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# In[2]:


#read csvs into the data frame and merge input and output csv - optional export command if desired
movement = pd.read_csv('pitch_movement.csv')
outcomes = pd.read_csv('pitch-arsenal-stats.csv')
arsenal = movement.merge(outcomes,on=['pitcher_id','pitch_type','year'])
#arsenal.to_csv('arsenal.csv')


# In[3]:


#check for appropriate data-types, missing values and duplicated rows.
#arsenal.info()
#display(arsenal.describe())
#display(arsenal.duplicated().sum())


# The info method reveals that the data types are appropriate and there are no missing values in any column. <br>
# The duplicated method verifies that there are no duplicated rows.

# In[4]:


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


# These select boxes are necessary to give the data proper context. Comparing pitches across years and components pitch types to each other will make the analysis of very little value.

# In[5]:


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
    value=(float(min_vert),float(max_vert)),
    min_value=float(min_vert),max_value=float(max_vert))

min_break, max_break=arsenal['percent_rank_diff_x'].min(),arsenal['percent_rank_diff_x'].max()

break_range = st.slider(
    "Choose Break % vs. League Average",
    value=(float(min_break),float(max_break)),
    min_value=float(min_break),max_value=float(max_break))


# The sliders make it really easy to get grup similar pitches. When you know your target pitch type, velocity and movement components; you can just select a range around that and easily filter the large data set to similar pitches.

# In[6]:


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


# The filtering and printing of this table produces an easy to read summary of the pitchers that throw comparable pitches

# In[31]:


#create a summary of means for the outputs of the filtered data
summary_stats = {'Mean': [(round(filtered_pitchers['whiff_percent'].mean(),1)), (round(filtered_pitchers['woba'].mean(),3)), (round(filtered_pitchers['run_value_per_100'].mean(),3))]}

summary_stats_df = pd.DataFrame(summary_stats, index=['whiff percent', 'woba', 'run value per 100'])


# In[33]:


st.table(summary_stats_df)


# This table creates a quick and valuable summary of what types of outcome you can generally expect from the given input components. The scatterplot below will give insight to the variance.

# In[7]:


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


# The scatterplot produced here is a very nice way to see correlation between the pitch components of the filtered data and their outcome. It's very interesting to see this displayed graphically with such little effort.

# In[8]:


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


# This histogram is an attempt to give insight as to which pitch types in general produce better results by counting them within the range of outputs.

# #### Conclusions and future update potential
# I'm generally very happy with the app and streamlit. For the most part I was able to achieve the goals that I targetted. I've even used the webapp with friends to test real life comparisons and it seems accurate. <br> Unfortunately, I was unable to add trendlines to the scatterplots. I think there is a bug in the streamlit compatibility because the attribute (trendline="ols") would work with a call on the fig1, but not when called through streamlit. This trendline would make the analysis of the correlation between outputs and inputs much easier. It's something I want to try to explore in the future to update the project with. <br> I'd like to update this dataframw with 2023 pitches as they become available and explore a way for the df to be automatically downloaded via api.

# In[ ]:




