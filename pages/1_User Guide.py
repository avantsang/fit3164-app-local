#------------------------------ Dependencies ------------------------------#

# base streamlit framework
import streamlit as st

# extra third-party streamlit component - sidebar logo
from streamlit_extras.app_logo import add_logo

# Function: Adds team03 logo into Sidebar
add_logo("assets/team_logo.png", height=0)

# ds modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

#--------------------------------------------------------------------------#

st.header("User Guide")
st.markdown("*Quickstart for New Users*")

# st.image('assets/software_design.jpg', caption='Sunrise by the mountains')

# st.write("The entirety of the data analysis, modelling, etc. resides inside a Streamlit python script.")
# step1 = st.checkbox("1 - Load, prepare and aggregate the data")
# if step1:
#     st.write("Expand on this")
# step2 = st.checkbox("2 - Takes user inputs from UI (Item, State, Selected Pair of Months)")
# if step2:
#     st.write("Expand on this")
# step3 = st.checkbox("3 - Estimate Price Elasticity based on user inputs")
# if step3:
#     st.write("Expand on this")
# step4 = st.checkbox("4 - If Item is elastic, allow user to specify a discount percentage to apply on the item")
# if step4:
#     st.write("Expand on this")
# step5 = st.checkbox("5 - Predict and display forecasted sales volume based on discount")
# if step5:
#     st.write("Expand on this")


st.subheader("General Interface")
st.write("The left sidebar is your primary method of navigation. \n Simply click on each tab to navigate to the respective page.")

st.subheader("Tab Guide")
# st.markdown("* Home - Landing page and introduciton to Price Elasticity *  User Guide - Information to operate this Web App. * Settings - Configure file/data settings. * Price Elasticity [S] - Simple Model using PED Formula * Price Elasticity [LRM] - Linear Regression Model")
st.markdown("* __Home__ - Landing page and introduciton to Price Elasticity")
st.markdown("* __User Guide__ - Information to operate this Web App")
# st.markdown("* __Settings__ - Configure file/data settings")
st.markdown("* __Price Elasticity [S]__ - Simple Model using PED Formula")
st.markdown("* __Price Elasticity [LRM]__ - Linear Regression Model")

st.write("")

help = st.expander("How to use Price Elasticity Tool")
with help:
    st.markdown("1. Select an Item, either by text search, or selection via. the dropdown box.")
    st.markdown("2. Select a State via. the dropdown box.")
    st.markdown("3. After selecting Item and State, you may explore the presented dataframe, which contains the past 13 months of sales information.")
    st.markdown("4. Select a pair of months for elasticity to be calculated with.")
    st.markdown("5. If the selected item is elastic in the selected state, during the specified months, the elasticity coefficient will be displayed.")
    st.markdown("6. An expandable body of text is interactable for the user to reveal why the item is Elastic or Inelastic")
    st.markdown("7. If the item is elastic, you can specify a discount percentage to apply on the item via. a Slider.")
    st.markdown("8. The Base Demand of the item during the selected month, as well as the calculated predicted sales volume will be presented to the user.")
    st.markdown("9. An expandable body of text is interactable for the user to reveal how the calculation was performed.")