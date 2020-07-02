import os, pickle, re
import numpy as np
import pandas as pd


def compare_date(date):
    """
    A function to find if a date is within a year from now
    
    Inputs:
    - date (str), a date in the mm/dd/yyyy format
    
    Returns:
    - bool (str), a bool indicating if the date is 
        within a year from now or not
    """
    other = '4/3/2020'
    m,d,y = date.split('/')
    om,od,oy = other.split('/')
    m = int(m)
    d = int(d)
    y = int(y)
    om = int(om)
    od = int(od)
    oy = int(oy)
    if oy <= y+1:
        if om < m:
            return True
        elif om == m:
            if od < d:
                return True
            else:
                return False
        else: 
            return False
    else:
        return False
# Removing all positive transactions
transactions = transactions[transactions['Transaction Type'] == 'debit']

# Finding all transactions within a year of now
transactions = transactions[transactions['Date'].map(compare_date)]

# Parsing out annual expenses for each specific category
food = transactions[transactions.Category.map(lambda x: x.lower() in ['food & dinging', 'alcohol & bars', 'restaurants', 'fast food'])].Amount.sum()
flights = transactions[transactions.Category.map(lambda x: x.lower() in ['air travel'])].Amount.sum()
hotel = transactions[transactions.Category.map(lambda x: x.lower() in ['hotel'])].Amount.sum()
gas = transactions[transactions.Category.map(lambda x: x.lower() in ['auto & transport', 'gas & fuel'])].Amount.sum()
grocery = transactions[transactions.Category.map(lambda x: x.lower() in ['groceries'])].Amount.sum()
utilities = transactions[transactions.Category.map(lambda x: x.lower() in ['bills & utilities', 'mobile phone', 'internet'])].Amount.sum()
other = transactions.Amount.sum() - food -  flights - hotel - gas - grocery

# Making a dict containing all of the expenses, to be used later
expenses = {
    'flights': flights,
    'hotel':hotel,
    'grocery':grocery,
    'gas':gas,
    'utilities':utilities,
    'restaurants': food,
    'other':other
    
}

expenses


def calculate_rewards(rewards_df, expenses):
    """
    A function to calculate the max rewards for a parsed dataframe.
    TODO: this needs to eventually include net_fee in it's equation.
    
    Inputs:
    - rewards_df (pd.DateFrame), a sliced dataframe with columns
        similar to to_plot
    - expenses (dict), a dictionary containing all of a person's 
        annual expenses
        
    Returns:
    - cash_rewards (float), the annual rewards one would recieve
    """
    cash_rewards = 0
    for category, expense in expenses.items():
        try:
            if isinstance(rewards_df[category], float):
                rate = rewards_df[category] / 100
            else:
                rate = max(rewards_df[category]) / 100
            cash_rewards += rate * expense
        except:
            continue
        
    return cash_rewards