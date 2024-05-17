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



st.title("Price Elasticity of Demand & Pricing Optimiser for Walmart Retail Products")

st.caption("FIT3164 DS - Pricing Optimisation and Analysis Project")

st.subheader("Features")
st.markdown("1. Estimate price elasticity for items in the dataset \n 2. Use Price Elasticty to forecast sales volume if the user chooses to apply a discount to the item")

st.subheader("What is Price Elasticity?")
st.markdown("Price Elasticity is a measurement of: \n\n **Change in an item's demand** (or sales volume), in relation to a **change in its price**. \n\n If an item is :green[**Elastic**], a change in price yields a large change in demand. \n\n If an item is :red[**Inelastic**], a change in price yields little, to no change in demand.")

elasticity = st.expander("What's the formula for Price Elasticity?", expanded=True)
with elasticity:
    st.latex(r'''
                \text{Price Elasticity of Demand} = \left(\frac{\text{Percentage change in quantity demanded}}{\text{Percentage change in price}}\right)
             ''')
    
interpret = st.expander("How do I interpret the Elasticity Coefficient?", expanded=True)
with interpret:
    st.write("Example - If an item's elasticity coefficient is -2.22, it would mean the following:")
    st.info("A 10% decrease in the item's price, will increase its sales demand by 22.2%.")
    st.write("")
    st.write("General Types of Price Elasticity")
    st.markdown("* __Infinity__ - Perfectly Elastic - Changes in price result in demand declining to zero")
    st.markdown("* __Less than 0__ - Elastic - Changes in price yield a significant change in demand")
    st.markdown("* __Greater than 0__ - Inelastic - Changes in price yield insignificant change in demand")
    st.markdown("* __Zero__ - Changes in price yield no change in demand")    
# st.subheader("What have we produced?")
# st.write("A webapp that estimates price elasticity of items, and predictes sales volume given a discount.")
# st.markdown("1. Developed a linear regression model using the formula to estimate individual items' price elasticity \n 2. Predicted future sales volume, by taking the 30 most recent days of sales as our base demand, the price elasticity, and a user-specified discount")


# 

# experimentation = st.checkbox("In Experimentation:")
# if experimentation:
#     lstm = st.checkbox("LSTM model to predict base demand")
#     if lstm:
#         st.write("test")
#     events = st.checkbox("Observe seasonality through events")
#     if events:
#         st.write("test")



# st.subheader("Inputs and Outputs")