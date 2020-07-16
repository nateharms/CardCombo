import os, pickle, re
import numpy as np
import pandas as pd
from multiprocessing import Pool



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

def simulate(rewards_df, expenses, num_of_cards):

    to_plot = rewards_df[rewards_df.columns[:-3]]

    # Only looking at credit card with greater than 1% back at everything
    to_plot = to_plot[to_plot.sum(axis=1) > len(to_plot.columns)]

    # Removing cards that have a weirdly high point value
    # These data are either parsed incorrectly or are hotel rewards were
    # the point to cent ratio is high (e.g. many points to a cent)
    to_plot = to_plot[to_plot.sum(axis=1) <= 2*len(to_plot.columns)] 

    card_rewards = []
    cloud_list = []

    for i in range(1000):
        choice = np.random.choice(to_plot.index, num_of_cards)
        card_rewards.append(calculate_rewards(to_plot.loc[choice], expenses))
        cloud_list.append((calculate_rewards(to_plot.loc[choice], expenses), choice))
    return card_rewards, cloud_list

def simulate_all(rewards_df, expenses, range_of_cards=10):
    calculated_rewards = {}
    word_cloud = {}
    for num_of_cards in range(range_of_cards+1):
        card_rewards, cloud_list = simulate(rewards_df, expenses, num_of_cards)
        calculated_rewards[num_of_cards] = card_rewards
        word_cloud[num_of_cards] = cloud_list
    return calculated_rewards, word_cloud


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