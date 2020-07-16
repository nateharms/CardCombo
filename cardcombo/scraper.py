import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import pickle

parent_url = 'https://www.cardratings.com/credit-card-list.html'
res = requests.get(parent_url)
html_page = res.content
soup = BeautifulSoup(html_page, 'html.parser')
cc_urls = []
for link in soup.find_all('a', href=True):
    if 'cardratings.com/credit-card/' in link.get('href'):
        print(link.get('href'))
        cc_urls.append(link.get('href'))


def get_rewards_from_string(string):
    """
    A function to read through a string and pick out the rewards
    for specific categories based on associated words. These 
    associated word may be incomplete.
    
    Inputs:
    - string (str), a string containing the rewards for a credit card
    
    Outputs:
    - rewards (dict), a dictionary with keys of categories and values
        of points earned per dollar spent
    """
    key_words = {
        'flights':['flights', 'airlines','travel', 'air', 'southwest', 'fly'],
        'hotel': ['travel', 'hotel'] ,
        'grocery':['supermarket', 'grocery', 'groceries'],
        'gas':['station', 'gas'],
        'utilities':['telephone', 'shipping', 'internet', 'cabel'],
        'restaurants':['restaurants', 'dining'],
        'other':['select', 'rotating']
    }
    rewards_dict = {}
    all_15 =  False
    if not isinstance(string, str):
        # a catch all incase if string fed in is faulty
        rewards = {
            'flights':0,
            'hotel':0,
            'grocery':0,
            'gas':0,
            'utilities':0,
            'restaurants':0,
            'other':0 
        }
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
                        # Cards with a 1.5 multiplier are often 1.5% 
                        # cash back at everything
                        all_15 =  True
                    rewards_dict[category] = multiplyer
                except:
                    continue
        if category not in rewards_dict.keys():
            rewards_dict[category] = 0
    
    if all_15:
        # This is a 1.5% back on all purchases card
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
    
    Inputs:
    - string (str), a string containing a $dollar amount
    
    Output (float), the dollar amount of the annual fee
    """
    try:
        return float(re.search('\$\d+', string).group()[1:])
    except AttributeError:
        return 0.
    
def get_annual_bonus(string):
    """
    A function to look through a string and try and find the annual 
    bonuses that you get with a particular card that offsets the annual
    fee of those cards
    
    Inputs:
    - string (str), a string that contians a description of the card bonuses
    
    Outputs:
    - credits (float), the dollar amount of the annual bonus
    """
    credits = 0
    for line in string.split('\n'):
        credit_words = ['saving', 'credits'] # we want to see these words in a sentence
        comparitive_words = ['higher', 'lower', 'worse', 'better'] # we don't want to see these words
        if any(map(lambda x: x in line.lower(), credit_words)) and not any(map(lambda x: x in line, comparitive_words)):
            try:
                credits += max([float(credit[1:]) for credit in re.findall('\$\d+', line) if float(credit[1:]) >= 50])
            except ValueError:
                pass
    return credits

def get_rewards_info_from_url(url):
    """
    A function that will request the html data from a url and find
    the rewards, annual fee, and annual bonuses for that link. This
    function isn't 100% working (issues with annual fee and bonus). But
    can parse out the rewards.
    
    Inputs:
    - url (str), a string representation of the url
    
    Outputs:
    - title (str), the title of the post
    - rewards (dict), a dictionary containing the rewards, annual_fee
        annual_bonus, and net_fee
    """
    
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    title = soup.title.text
    print(title)
    print(url)
    if '400' in title:
        rewards = {
            'flights':0,
            'hotel':0,
            'grocery':0,
            'gas':0,
            'utilities':0,
            'restaurants':0,
            'other':0 
        }
        rewards['annual_fee'] = 0
        rewards['annual_bonus'] = 0
        rewards['net_fee'] = 0
        return None, rewards
        
    d = soup.find('div', itemprop='description')
    try:
        df = pd.read_html(d.decode())[0].T.set_index(0)
    except:
        rewards = {
            'flights':0,
            'hotel':0,
            'grocery':0,
            'gas':0,
            'utilities':0,
            'restaurants':0,
            'other':0 
        }
        rewards['annual_fee'] = 0
        rewards['annual_bonus'] = 0
        rewards['net_fee'] = 0
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


if __name__ == '__main__':
    parent_url = 'https://www.cardratings.com/credit-card-list.html'
    res = requests.get(parent_url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    cc_urls = []
    for link in soup.find_all('a', href=True):
        if 'cardratings.com/credit-card/' in link.get('href'):
            print(link.get('href'))
    total_rewards = {}
    for cc_url in cc_urls:
        if cc_url == "https://www.cardratings.com/credit-card/connect-classic":
            continue # known to be broken url
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

    # Currently don't trust the annual fee and bonus section, 
    # so we're going to process based on the rewards alone

    # TODO: Find accurate net_fee for all cards and use that when 
    # calculating rewards
    to_plot = rewards_df[rewards_df.columns[:-3]]

    # Only looking at credit card with greater than 1% back at everything
    to_plot = to_plot[to_plot.sum(axis=1) > len(to_plot.columns)]

    # Removing cards that have a weirdly high point value
    # These data are either parsed incorrectly or are hotel rewards were
    # the point to cent ratio is high (e.g. many points to a cent)
    to_plot = to_plot[to_plot.sum(axis=1) <= 2*len(to_plot.columns)] 
    to_plot