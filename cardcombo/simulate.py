import os, pickle, re
import numpy as np
import pandas as pd
from multiprocessing import Pool

COLUMNS = ['flights', 'hotel', 'grocery', 'gas', 'dining', 'other']

def calculate_rewards(db, expenses):
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
        rate = 0
        added = []
        try:
            for _ in range(4): # 4 quarters in a year
                index = db[db.index.map(lambda x: x not in added)][category].idxmax()
                rate += db.loc[index][category] /400
                if db.loc[index].rotating == True:
                    added.append(index)
            cash_rewards += rate * expense
        except:
            continue
        
    return cash_rewards - db.annual_fee.sum()

def simulate(db, expenses, num_of_cards, cards_to_consider=[]):

    card_rewards = []
    for i in range(250):
        # Selecting new cards 
        choice = sorted(np.random.choice(db.index[db.index.map(lambda x: x not in cards_to_consider)], num_of_cards, replace=False))
        # Calculating the rewards
        card_rewards.append((calculate_rewards(db.loc[choice + cards_to_consider], expenses), choice + cards_to_consider))

    return card_rewards

def simulate_all(db, expenses, cards_to_consider=[], credit=800, range_of_cards=5):

    # Getting cards below the user's credit score
    db = db[(db.req_credit <= credit)] 

    # Looping through the range of possible cards and calculating the rewards
    calculated_rewards = {}
    for num_of_cards in range(range_of_cards+1):
        card_rewards = simulate(db, expenses, num_of_cards, cards_to_consider)
        calculated_rewards[num_of_cards] = card_rewards
    return calculated_rewards


if __name__ == '__main__':
    example_expenses = {
        'flights': 800,
        'hotel': 800,
        'grocery': 250*12,
        'gas': 100*12,
        'restaurants': 250*12,
        'other': 150*12}
    rewards_df = pickle.load(open('../db.pkl', 'rb'))
    calculated_rewards = simulate_all(rewards_df, example_expenses)
    