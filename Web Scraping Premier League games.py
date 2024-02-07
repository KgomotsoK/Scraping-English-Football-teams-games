# Getting Premier league data from 2020-2023 games

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Scraping through multiple seasons and teams
years = list(range(2023, 2022, -1))

all_matches = []
# URL where we are scraping data
standings_url = "https://fbref.com/en/comps/9/Premier-Leagues-Stats"

for year in years:
    # Download html document of the site 
    data = requests.get(standings_url)
    # Parse our html
    soup = BeautifulSoup(data.text)
    # Create a seletor for the beautiful soup to select
# Select the tabele from the page
    standings_table = soup.select('table.stats_table')[0]
    # Find all a tags for all teams in the table
    links = standings_table.find_all('a')
    # Find the href of all a-tags 
    links = [l.get('href') for l in links]
    #filter our links so that we have only squad links
    links = [l for l in links if '/squads/' in l]
    #filter our links so that we have only squad links
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")
        
        soup = BeautifulSoup(data.text) 
        links = soup.find_all('a')
        links = [l.get('href') for l in links]
        links = [l for l in links if  l and 'all_comps/shooting/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]
        data = requests.get(team_urls[0])
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        
        try:
            team_data = pd.merge(matches[0], shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], how='outer', on='Date')
            
        except ValueError:
            continue
        
        team_data["Season"] = year
        team_data["Team"] = team_name
            
        all_matches.append(team_data)
        time.sleep(1)
        
print("Done!!") 

match_df = pd.concat(all_matches)
pd.options.display.max_rows = 9999
df = match_df[match_df['Comp'] == "Premier League"]
df.sort_values(by='Date')

match_df.to_csv("./Data/Premier_League_Data.csv")