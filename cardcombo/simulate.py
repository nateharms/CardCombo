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
        try:
            if isinstance(db[category], float):
                rate = db[category] / 100
            else:
                rate = max(db[category]) / 100
            cash_rewards += rate * expense
        except:
            continue
        
    return cash_rewards

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
    example_expenses = {'flights': 895.4899999999999,
        'hotel': 9.9,
        'grocery': 1803.92,
        'gas': 336.03999999999996,
        'utilities': 0.0,
        'restaurants': 4069.8500000000004,
        'other': 44067.240000000005}
    rewards_df= pickle.load(open('rewards.pkl', 'rb'))
    calculated_rewards, word_cloud = simulate_all(rewards_df, example_expenses)

    f = open('calculated_rewards.pkl', 'wb')
    pickle.dump(calculated_rewards, f)
    f = open('cloud.pkl', 'wb')
    pickle.dump(word_cloud, f)   