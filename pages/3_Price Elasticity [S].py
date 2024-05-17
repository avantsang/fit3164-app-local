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
#import statistics
#import time
#import math

#--------------------------------------------------------------------------#



@st.cache_data
def load_data():
    # Load only necessary columns from each dataset

    # Sales CSV (in wide format), contains each items' sales record at each day
    # Take all the wide-format 'd' aka. day columns
    sales_columns = ['id', 'item_id', 'store_id', 'state_id'] + [f'd_{i}' for i in range(1, 1942)]
    sales = pd.read_csv('https://storage.googleapis.com/pricing-optimisation-data/original/sales_train_evaluation.csv', usecols=sales_columns)

    # Prices CSV -> Contains an item's Price, at a specific wm_yr_wk (the week)
    prices_columns = ['item_id', 'store_id', 'wm_yr_wk', 'sell_price']
    prices = pd.read_csv('https://storage.googleapis.com/pricing-optimisation-data/original/sell_prices.csv', usecols=prices_columns)

    # Events CSV -> Omit events for now
    calendar_columns = ['d', 'date', 'wm_yr_wk']
    calendar = pd.read_csv('https://storage.googleapis.com/pricing-optimisation-data/original/calendar.csv', usecols=calendar_columns)

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

    
    special_case = False
    premium_case = False

    st.title("Price Elasticity Modeling Tool")


    # ------------------------------------ 1. Load, Prepare and Aggregate Data ------------------------------------ #

    # Load data
    sales, prices, calendar = load_data()
    monthly_sales, monthly_prices = calculate_monthly_sales_and_prices_optimized(sales, prices, calendar)


    # ------------------------------------ 2.a Take user INPUT for Item and State ---------------------------------- #

    # Select an item and state
    item_selected = st.selectbox("Select an Item", options=monthly_sales['item_id'].unique())
    print(f"ITEM User Input: {item_selected}")
    state_selected = st.selectbox("Select a State", options=monthly_sales['state_id'].unique())
    print(f"STATE User Input: {state_selected}")

                    # ------------ Filter dataset based on INPUT Item and State ------------ #

    # Merge the monthly-aggregated sales and prices dataframes
    data = monthly_sales.merge(monthly_prices, on=['item_id', 'store_id', 'year_month'], how='left')
    # Take the 13 most recent months, filtered by user's input of Item and State
    filtered_data = data[(data['item_id'] == item_selected) & (data['state_id'] == state_selected)].tail(13)
    filtered_data_w_revenue = data[(data['item_id'] == item_selected) & (data['state_id'] == state_selected)].tail(13)


                    # -------------------- OUTPUT Filtered Dataframe --------------------- #

    

    filtered_data_w_revenue['monthly_revenue'] = filtered_data_w_revenue['sales'] * filtered_data_w_revenue['sell_price']

    # Step 2: Aggregate total revenue by price
    total_revenue_by_price = filtered_data_w_revenue.groupby('sell_price')['monthly_revenue'].sum()

    max_revenue_price = total_revenue_by_price.idxmax()
    max_revenue = total_revenue_by_price.max()



    st.info(f"Historic Optimal Price: {max_revenue_price:.2f}, with a total revenue of {max_revenue:.2f}")
    st.write("Past 13 months' sales volume and average price:")
    st.dataframe(filtered_data_w_revenue[['year_month', 'item_id', 'state_id', 'sales', 'sell_price', 'monthly_revenue']].tail(13))

    


    # ------------------------------------ 2.b. Take user INPUT for pair of months ---------------------------------- #

    # Select two adjacent months to calculate elasticity
    months = filtered_data['year_month'].astype(str).tolist()
    selected_months = st.radio("Select two adjacent months to calculate price elasticity", 
                               options=list(zip(months[:-1], months[1:])))
    start_month, end_month = selected_months

                    # -------------- Take the selected pair, declare for later use -------------- #
    start_data = filtered_data[filtered_data['year_month'] == start_month].iloc[0]
    end_data = filtered_data[filtered_data['year_month'] == end_month].iloc[0]


    # ----------------------------------------- Inelasticty Explanations ----------------------------------------- #

    numerator_zero = f"This item, in {state_selected}, during {start_month} and {end_month} is Inelastic due to there being no change in sales volume. \n\nThis means that during this specific period, changes in price yield little to no change in demand.\n\n Economically, this suggest that consumers are potentially not particularly sensitive to changes in this item's price. \n\n For example, this good may be a necessity, so it must be purchased regardless of price changes."
    denominator_zero = f"This item, in {state_selected}, during {start_month} and {end_month} is Inelastic due to there being no change in sales price.  \n\nMathematically, this means that the calculation of price elasticity yields an undefined result, which means Inelasticty."
    numerator_and_denominator_zero = f"This item, in {state_selected}, during {start_month} and {end_month} is Inelastic due to there being no change in sales volume and sales price.  \n\nThis inidicates that at the price the item is currently set at, the consumers aren't senstive "
    numerator_and_denominator_same = f"This item, in {state_selected}, during {start_month} and {end_month} is Inelastic. \n\nMathematically, this means that the calculation of price elasticity yields an undefined result, which means Inelasticty. \n\nEconomically, this may suggest that consumers are satisfied with the current pricing of the item."
    zero_sales_same_price = f"This item, in {state_selected}, during {start_month} and {end_month} is Inelastic due to there being no change in sales volume and sales price.  \n\nMathematically, this means that the calculation of price elasticity yields an undefined result, which means Inelasticty. \n\nEconomically, as there were no sales of this item during the two selected months, it may suggest that this item is not in demand during this period."




    


    # ------------------------------------ Pre-Validate Potential to be Inelastic ------------------------------------ #



    # Pre-examines the selected pair of months, and if inelastic, display specific reason why
    
    # state elasticty status as elastic first, then change according to conditional statements validated after
    elasticity_status = "Elastic"

    # if sales volume is zero, and sell price stayed the same
    if start_data['sales'] == 0 and end_data['sales'] == 0 and round(end_data['sell_price'],2) - round(start_data['sell_price'],2) == 0:
        elasticity_status = "Inelastic"
        st.error(f"The selected item is {elasticity_status} in {state_selected} during {start_month} and {end_month} \n")
        show_explanation = st.expander("Why is this the case and what does this mean?")
        with show_explanation:
            st.warning(zero_sales_same_price)
    # if sales volume stayed the same, but sell price changed
    elif end_data['sales'] - start_data['sales'] == 0 and round(end_data['sell_price'],2) - round(start_data['sell_price'],2) != 0:
        elasticity_status = "Inelastic"
        st.error(f"The selected item is {elasticity_status} in {state_selected} during {start_month} and {end_month} \n")
        show_explanation = st.expander("Why is this the case and what does this mean?")
        with show_explanation:
            st.warning(numerator_zero)
    
    # if sales volume stayed the same, and sales price stayed the same
    elif end_data['sales'] - start_data['sales'] == 0 and round(end_data['sell_price'],2) == round(start_data['sell_price'],2): # end_data['sell_price'] - start_data['sell_price'] == 0:
        elasticity_status = "Inelastic"
        st.error(f"The selected item is {elasticity_status} in {state_selected} during {start_month} and {end_month} \n")
        show_explanation = st.expander("Why is this the case and what does this mean?")
        with show_explanation:
            st.warning(numerator_and_denominator_same)

    # if sales volume changed, and sales price stayed the same
    elif end_data['sales'] - start_data['sales'] != 0 and round(end_data['sell_price'],2) == round(start_data['sell_price'],2): #end_data['sell_price'] - start_data['sell_price'] == 0:
        elasticity_status = "Inelastic"
        st.error(f"The selected item is {elasticity_status} in {state_selected} during {start_month} and {end_month} \n")
        show_explanation = st.expander("Why is this the case and what does this mean?")
        with show_explanation:
            st.warning(denominator_zero)
    elif start_data['sales'] == 0: # round(end_data['sell_price'],2) == round(start_data['sell_price'],2) or :
        elasticity_status = "Elastic"
        special_case = True
    elif end_data['sales'] > start_data['sales'] and round(end_data['sell_price'],2) > round(start_data['sell_price'],2):
        elasticity_status = "Elastic"
        special_case = True
        premium_case = True





    # ------------------------------------ 3. Calculate Price elasticity ------------------------------------ #


    
    if elasticity_status == "Elastic":
        # Proceed with calculating price elasticty IF it's not a special case, or if it's a premium case
        if special_case == False or (special_case == True and premium_case == True):
            # Calculate price elasticity using the formula and previously calculated values
            pct_change_sales = (end_data['sales'] - start_data['sales']) / start_data['sales']
            pct_change_price = (end_data['sell_price'] - start_data['sell_price']) / start_data['sell_price']

            elasticity = pct_change_sales / pct_change_price


            # ------------------------------------ Messages for Special Cases ------------------------------------ #

            #Show special message for when the item is elastic, and is a premium case
            if premium_case == True:
                elasticity_status = "Elastic"
                st.success(f"The selected item is {elasticity_status} with a Price elasticity of {elasticity:.2f}. \n\n However, this is a rare case. During this month, an increase in price also led to an increase in sales. A potential explanation for why this happened, may be that the item is a luxury item where the increase in price led to an increase in desirability, or there was a unique market situation.")
            # misc fallback conditions
            # for when elasticity value is inelastic(=1 < e < 0), as well as perfectly inelastic (=0)
            if elasticity <= 0 and elasticity >-1:
                st.error(f"The selected item is Inelastic in {state_selected} during {start_month} and {end_month}")
            if elasticity < -1 and premium_case == False:
                elasticity_status = "Elastic"
                st.success(f"The selected item is {elasticity_status}. Price elasticity: {elasticity:.2f}")
            elif elasticity > -1 and premium_case == False:
                elasticity_status = "Inelastic"
                st.success(f"The selected item is {elasticity_status}. Price elasticity: {elasticity:.2f}")
        elif special_case == True:
            elasticity_status = "Elastic"
            st.success(f"The selected item is {elasticity_status}.  \n\nHowever, as the sales volume in {start_month} was Zero, elasticity cannot be calculated as dividing by zero is undefined. \n\nThis may potentially suggest that the item is highly elastic as there was a signicant change in sales volume when price was changed.")




    # ------------------------------------ 4. Select Discount Percentage ------------------------------------ #

    # Select discount percentage (ONLY allow if price elastic)
    # Condition1 : The item is elastic and not a case where start_month sales are 0 and end_month sales are not 0
    # (or) Condition2 : The item is elastic and it's a premium case (luxury good)
    if (elasticity_status == "Elastic" and special_case == False) or (elasticity_status == "Elastic" and premium_case == True):
        show_explanation = st.expander("What does this mean?")
        with show_explanation:
            st.info(f"This means that for this item, changes in price will yield a significant change in demand. \n More specifically, a 1% decrease in price will result in a {abs(round(elasticity,2))}% increase in quantity demanded.")
        
        discount_percentage = st.slider("Select a discount percentage", 0.0, 100.0, 5.0)
        print(f"Discount Percentage Selected: {discount_percentage}")



        # ------------------------------------ Calculate Base Demand ------------------------------------ #


        # Calculate Base demand 
        # Take the selected month (that we're predicting for)
        selected_date = end_data['year_month'].split("-")
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
        base_demand = round(np.mean(past_selected_volumes),2)


        
        # base_demand = filtered_data.tail(1)['sales'].mean() ## * 14
        st.write(f"Average Base Demand for this item during the {selected_month}'th month of the year, across the past 5 years: {base_demand}")


        # ------------------------- 5. Forecast Sales Volume & Display as OUTPUT -------------------------- #


        # Forecast sales volume based on price elasticity and discount
        predicted_change = elasticity * (-discount_percentage / 100)
        forecasted_sales_volume = abs(base_demand * (1 + predicted_change))
        st.write(f"Predicted sales volume with a {discount_percentage}% discount: {forecasted_sales_volume:.0f} units")
        show_calculation = st.expander("How was this calculated?")
        with show_calculation:
            st.info(f"Elasticity: {elasticity:.2f} \n\n Base demand (Average daily sales volume in the most recent month): {base_demand} \n\n Discount Percentage selected: {discount_percentage}% \n\n Calculation: \n\n Elasticty * -1(Discount Percentage) = Predicted Change \n\n {elasticity:.2f} * -1({discount_percentage}%) = {round(predicted_change,2)} \n\n Base Demand * 1 + Predicted Change = Predicted Sales Volume \n\n {base_demand} * 1 + {round(predicted_change,2)} = {round(forecasted_sales_volume,2)} \n\n Take the absolute value.")

if __name__ == "__main__":
    main()
