#------------------------------ Dependencies ------------------------------#

# base streamlit framework
import streamlit as st

import streamlit_extras

# extra third-party streamlit component - sidebar logo
from streamlit_extras.app_logo import add_logo

# Function: Adds team03 logo into Sidebar
add_logo("assets/team_logo.png", height=0)

# ds modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
#import time
#import math
import statsmodels.api as sm

# from statsmodels.regression.linear_model import OLS
# import statsmodels.regression.linear_model as lm

# from statsmodels.tools.tools import add_constant

#--------------------------------------------------------------------------#



@st.cache_data
def load_data():
    # Load only necessary columns from each dataset

    # Sales CSV (in wide format), contains each items' sales record at each day
    # Take all the wide-format 'd' aka. day columns
    sales_columns = ['id', 'item_id', 'store_id', 'state_id'] + [f'd_{i}' for i in range(1, 1942)]
    sales = pd.read_csv('./sales_train_evaluation.csv', usecols=sales_columns)

    # Prices CSV -> Contains an item's Price, at a specific wm_yr_wk (the week)
    prices_columns = ['item_id', 'store_id', 'wm_yr_wk', 'sell_price']
    prices = pd.read_csv('./sell_prices.csv', usecols=prices_columns)

    # Events CSV -> Omit events for now
    calendar_columns = ['d', 'date', 'wm_yr_wk']
    calendar = pd.read_csv('./calendar.csv', usecols=calendar_columns)

    return sales, prices, calendar







@st.cache_data
# Aggregates the sales and price data at a MONTHLY level
def calculate_monthly_sales_and_prices_optimized(sales, prices, calendar):


    # convert Date column (string) into date_time type
    calendar['date'] = pd.to_datetime(calendar['date'])

    # Use .dt.to_period('M') to get yyyy-mm format, and convert back into string
    calendar['year_month'] = calendar['date'].dt.to_period('M').astype(str)

    # Take only the two needed columns, day and the year-month, this will be used for merging with sales dataset
    # Now we can map to each day of sales, with its respective year-month that it belongs to
    calendar_mapping = calendar[['d', 'year_month']]

    # Melt sales CSV from wide format to long format
    sales_long = pd.melt(sales, id_vars=['item_id', 'store_id', 'state_id'], var_name='d', value_name='sales')

    # Merge calendar with sales, directly mapping each day with its designated year-month
    sales_long = sales_long.merge(calendar_mapping, on='d', how='left')

    # Group data by month, aggregating sales data by the below columns to obtain monthly sales
    monthly_sales = sales_long.groupby(['item_id', 'store_id', 'state_id', 'year_month'], as_index=False)['sales'].sum()

    # Aggregate prices to monthly average prices by mapping weeks to months
    # Use previous calendar dataframe, and map each week identifer to each corresponding monthly period
    calendar_week_mapping = calendar[['wm_yr_wk', 'year_month']].drop_duplicates()

    # Merge prices with above calendar mapping, so each item's pricing at each corresponding week id (wm_yr_wk) is mapped to a year-month identifier
    prices = prices.merge(calendar_week_mapping, on='wm_yr_wk', how='left')

    # Aggregate prices by below columns, to obtain monthly average prices (Average each month's prices for the item)
    monthly_prices = prices.groupby(['item_id', 'store_id', 'year_month'], as_index=False)['sell_price'].mean()

    # Return the aggregated dataframes which will be filtered later
    return monthly_sales, monthly_prices






def main():
    st.title("Price Elasticity Modeling Tool")

    # Load data
    sales, prices, calendar = load_data()
    monthly_sales, monthly_prices = calculate_monthly_sales_and_prices_optimized(sales, prices, calendar)

    # Select an item and state
    item_selected = st.selectbox("Select an Item", options=monthly_sales['item_id'].unique())
    state_selected = st.selectbox("Select a State", options=monthly_sales['state_id'].unique())

    # Merge sales and prices for the selected item and state
    data = monthly_sales.merge(monthly_prices, on=['item_id', 'store_id', 'year_month'], how='left')
    filtered_data = data[(data['item_id'] == item_selected) & (data['state_id'] == state_selected)]


    st.write("Past 13 months' sales volume and average price:")
    st.write(filtered_data[['year_month', 'sales', 'sell_price']].tail(13))

    # Remove rows with zero sales or zero prices
    filtered_data = filtered_data[(filtered_data['sales'] > 0) & (filtered_data['sell_price'] > 0)]

    # Ensure there is price variability
    if filtered_data['sell_price'].nunique() < 2:
        st.write("Not enough price variability to perform regression analysis.")
        return


    # Fit linear regression model
    x = filtered_data['sell_price']
    x = sm.add_constant(x)  # Add a constant term for the intercept
    y = filtered_data['sales']
    result = sm.OLS(y, x).fit()

    # Get elasticity from the regression model
    intercept, slope = result.params

    elasticity = slope * (np.mean(x['sell_price']) / np.mean(y))
    if elasticity < 0:
        st.success(f"This item is Elastic. Price elasticity: {elasticity:.2f}")
    else:
        st.warning(f"This item is Inelastic. Price elasticity: {elasticity:.2f}")

    show_explanation = st.expander("What does this mean?")
    with show_explanation:
            st.info("test")

    # Select discount percentage
    discount_percentage = st.slider("Select a discount percentage", 0.0, 100.0, 5.0)


    # Calculate Base demand 
    # Take the selected month (that we're predicting for)
    selected_date = "2016-05".split("-")
    selected_year = selected_date[0]
    selected_month = selected_date[1]

    # Construct strings for the years prior, at that month
    required_past_years_dates = []
    for year in range(2011,int(selected_year) + 1):
        required_past_years_dates.append(str(year) + "-" + selected_month)

    # Find the sales volumes of the prior years, at that month
    past_selected_volumes = []
    for date in required_past_years_dates:
        sales = data[(data['item_id'] == item_selected) & (data['state_id'] == state_selected) & (data['year_month'] == date)]['sales'].mean()
        past_selected_volumes.append(sales)
    
    # Let our base demand be the average of the prior years' volumes at that month
    base_demand = round(statistics.mean(past_selected_volumes),2)

    st.write(f"Average Base Demand for this item during the latest month, across the past 5 years: {base_demand}")


    # Forecast sales volume based on price elasticity and discount
    predicted_change = elasticity * (-discount_percentage / 100)
    forecasted_sales_volume = base_demand * (1 + predicted_change)
    st.write(f"Predicted sales volume with a {discount_percentage}% discount: {forecasted_sales_volume:.0f} units")



if __name__ == "__main__":
    main()