import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import pickle

# Opening us the website that contains links to reviews
parent_url = 'https://www.cardratings.com/credit-card-list.html'
res = requests.get(parent_url)
html_page = res.content
soup = BeautifulSoup(html_page, 'html.parser')
cc_urls = []
for link in soup.find_all('a', href=True):
    if 'cardratings.com/credit-card/' in link.get('href'):
        cc_urls.append(link.get('href'))

def get_rewards_from_string(string):
    """
    A function to read through a string and pick out the rewards
    for specific categories based on associated words. 
    """
    key_words = {
        'flights':['flights', 'airlines','travel', 'air', 'southwest', 'fly'],
        'hotel': ['travel', 'hotel'] ,
        'grocery':['supermarket', 'grocery', 'groceries'],
        'gas':['station', 'gas'],
        'utilities':['telephone', 'shipping', 'internet', 'cabel'],
        'restaurants':['restaurants', 'dining'],
        'other':[]
    }
    rewards_dict = {}
    all_15 =  False
    if not isinstance(string, str):
        # a catch all incase if string fed in is faulty
        rewards = {'flights':0,'hotel':0,'grocery':0,'gas':0,'utilities':0,'restaurants':0,'other':0 }
        return rewards
        
    for category, key_word_list in key_words.items():     
        for sentence in string.replace('U.S.', 'US').split('. '):
            if any(map(lambda x: x in sentence.lower(), key_word_list)):
                try:
                    multiplyer = float(re.search('(\d+(?:\.\d+)?)', sentence).group())
                    if multiplyer > 15:
                        # This isn't a reward point value
                        continue
                    if multiplyer == 1.5:
                        # Cards with a 1.5 multiplier are 1.5
                        # cash back at everything
                        all_15 =  True
                    rewards_dict[category] = multiplyer
                except:
                    continue
        if category not in rewards_dict.keys():
            rewards_dict[category] = 0
    
    if all_15:
        for category in rewards_dict:
            rewards_dict[category] = 1.5
    if any(map(lambda x: x >= 1, rewards_dict.values())):
        # Cards with any rewards are assumed to have 1 point back
        # in all other categories, setting rewards for everything else to 1
        for category in rewards_dict.keys():
            if rewards_dict[category] == 0:
                rewards_dict[category] = 1
        
    return rewards_dict

def get_annual_fee(string):
    """
    A function to find the annual fee (or dollar amount) in a string
    """
    try:
        return float(re.search('\$\d+', string).group()[1:])
    except AttributeError:
        return 0.
    
def get_annual_bonus(string):
    """
    A function to find the annual bonuses that you get with a particular card
    """
    credits = 0
    for line in string.split('\n'):
        credit_words = ['saving', 'credits'] # we want to see these words
        comparitive_words = ['higher', 'lower', 'worse', 'better'] # we don't want to see these words
        if any(map(lambda x: x in line.lower(), credit_words)) and not any(map(lambda x: x in line, comparitive_words)):
            try:
                credits += max([float(credit[1:]) for credit in re.findall('\$\d+', line) if float(credit[1:]) >= 50])
            except ValueError:
                pass
    return credits

def get_rewards_info_from_url(url):
    """
    A function that will find the rewards, annual fee, and annual bonuses for a url. This
    function has issues with annual fee and bonus. 
    """
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    title = soup.title.text
    if '400' in title:
        rewards = {'flights':0,'hotel':0,'grocery':0,'gas':0,'utilities':0,'restaurants':0,'other':0,'annual_fee':0,'annual_bonus':0,'net_fee':0}
        return None, rewards
        
    d = soup.find('div', itemprop='description')
    try:
        df = pd.read_html(d.decode())[0].T.set_index(0)
    except:
        rewards = {'flights':0,'hotel':0,'grocery':0,'gas':0,'utilities':0,'restaurants':0,'other':0,'annual_fee':0,'annual_bonus':0,'net_fee':0}
        return title, rewards
    if 'Rewards' in df.index:
        rewards = get_rewards_from_string(df[1]['Rewards'])
        try:
            rewards['annual_fee'] = get_annual_fee(df[1]['Annual Fee'])
        except KeyError:
            rewards['annual_fee'] = 0
            for line in d.text.split('\n'):
                if 'annual fee' in line.lower():
                    rewards['annual_fee'] = get_annual_fee(line)
                    break
        rewards['annual_bonus'] = get_annual_bonus(d.text)
        rewards['net_fee'] = rewards['annual_fee'] - rewards['annual_bonus']
    else:
        rewards = get_rewards_from_string(d.text)
        rewards['annual_fee'] = 0
        rewards['annual_bonus'] = 0
        rewards['net_fee'] = 0
    return title, rewards

if not os.path.exists('rewards.pkl'): 
    # If we've run this before, we're gonna read in a pickle file
    total_rewards = {}
    for cc_url in cc_urls:
        if cc_url == "https://www.cardratings.com/credit-card/connect-classic": continue # known to be broken url
        title, rewards = get_rewards_info_from_url(cc_url)
        if title: # cleaning up the title
            title_string = ''
            review = False
            for t in title.split():
                if '-' in t.lower() or 'review' in t.lower():
                    break
                title_string += t + ' '
            total_rewards[title_string.strip()] = rewards
    # Making and saving the dataframe
    rewards_df = pd.DataFrame(total_rewards).T
    f = open('rewards.pkl', 'wb')
    pickle.dump(rewards_df, f)
else:
    f = open('rewards.pkl', 'rb')
    rewards_df = pickle.load(f)

# TODO: Find accurate net_fee for all cards
to_plot = rewards_df[rewards_df.columns[:-3]]
# Only looking at credit card with greater than 1% back at everything
to_plot = to_plot[to_plot.sum(axis=1) > len(to_plot.columns)]
# Removing cards that have a weirdly high point value
to_plot = to_plot[to_plot.sum(axis=1) <= 2*len(to_plot.columns)] 

# From my own annual expenses over the last 12 months. Plz don't share <3
transactions = pd.read_csv('transactions-3.csv')
transactions['Date'][0]
def compare_date(date):
    """
    A function to find if a date is within a year from now
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
# Removing deposits
transactions = transactions[transactions['Transaction Type'] == 'debit']
# Finding all transactions within a year of now
transactions = transactions[transactions['Date'].map(compare_date)]
# Parsing out annual expenses for each specific category
food = transactions[transactions.Category.map(lambda x: x in ['Food & Dining', 'Alcohol & Bars', 'Restaurants', 'Fast Food'])].Amount.sum()
flights = transactions[transactions.Category.map(lambda x: x in ['Air Travel'])].Amount.sum()
hotel = transactions[transactions.Category.map(lambda x: x in ['Hotel'])].Amount.sum()
gas = transactions[transactions.Category.map(lambda x: x in ['Auto & Transport', 'Gas & Fuel'])].Amount.sum()
grocery = transactions[transactions.Category.map(lambda x: x in ['Groceries'])].Amount.sum()
utilities = transactions[transactions.Category.map(lambda x: x in ['Bills & Utilities', 'Mobile Phone', 'Internet'])].Amount.sum()
other = transactions.Amount.sum() - food -  flights - hotel - gas - grocery
# Final expenses
expenses = {
    'flights': flights,
    'hotel':hotel,
    'grocery':grocery,
    'gas':gas,
    'utilities':utilities,
    'restaurants': food,
    'other':other 
}

def calculate_rewards(rewards_df, expenses):
    """
    A function to calculate the max rewards for a parsed dataframe.
    TODO: this needs to eventually include net_fee in it's equation.
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

# Given that there are many different combinations of cards, we're going to be solving this stochasticly.
if os.path.exists('calculated_rewards.pkl') and os.path.exists('cloud.pkl'):
    f = open('calculated_rewards.pkl', 'rb')
    calculated_rewards = pickle.load(f)
    f = open('cloud.pkl', 'rb')
    word_cloud = pickle.load(f)
else:
    calculated_rewards = {}
    word_cloud = {}
    for card_number in range(11): #0-10 cards
        card_rewards = []
        cloud_list = []

        for i in range(1000):
            choice = np.random.choice(to_plot.index, card_number)
            card_rewards.append(calculate_rewards(to_plot.loc[choice], expenses))
            cloud_list.append((calculate_rewards(to_plot.loc[choice], expenses), choice))
        calculated_rewards[card_number] = card_rewards
        word_cloud[card_number] = cloud_list

    f = open('calculated_rewards.pkl', 'wb')
    pickle.dump(calculated_rewards, f)
    f = open('cloud.pkl', 'wb')
    pickle.dump(word_cloud, f)