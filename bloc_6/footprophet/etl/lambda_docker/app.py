import json
import requests
import pandas as pd
import datetime
from functools import reduce

##############
# Create a game dataset from the inbound file
########
class Dataset:
    GAMES_FOR_STATS = 5
    def __init__(self, data):
        self.raw_results = []
        self.processed_results = []

        for idx, row in data.iterrows():
            try:
                row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%Y')
            except:
                try:
                    row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%y')
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}"+':'+row)
                    break
            self.raw_results.append(row)

        for result in self.raw_results: 
            try:
                home_statistics = self.get_statistics(result['HomeTeam'], result['Date'])
                if home_statistics is None:
                    continue
    
                away_statistics = self.get_statistics(result['AwayTeam'], result['Date'])
                if away_statistics is None:
                    continue
    
                processed_result = {
                    'result': result['FTR'],
                    'home_team': result['HomeTeam'],
                    'away_team': result['AwayTeam'],
                    'odds_home': float(result['B365H']),
                    'odds_draw': float(result['B365D']),
                    'odds_away': float(result['B365A']),
                }
    
                for label, statistics in [('home', home_statistics), ('away', away_statistics)]:
                    for key in statistics.keys():
                        processed_result[label + '_' + key] = statistics[key]
    
                self.processed_results.append(processed_result)
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}"+':'+result)
                break
    

    # Filter results to only contain matches played in by a given team, before a given date
    def filter(self, team, date):
        def filter_fn(result):
            return (
                result['HomeTeam'] == team or
                result['AwayTeam'] == team
            ) and (result['Date'] < date)

        return list(filter(filter_fn, self.raw_results))

    # Calculate team statistics
    def get_statistics(self, team, date, matches=GAMES_FOR_STATS):
        recent_results = self.filter(team, date)
        
        if len(recent_results) < matches:
            return None

        # This function maps a result to a set of performance measures roughly scaled between -1 and 1
        def map_fn(result):
            if result['HomeTeam'] == team:
                team_letter, opposition_letter = 'H', 'A'
            else:
                team_letter, opposition_letter = 'A', 'H'

            return {
                'wins': 1 if result['FTR'] == team_letter else 0,
                'draws': 1 if result['FTR'] == 'D' else 0,
                'losses': 1 if result['FTR'] == opposition_letter else 0,
                'goals': int(result['FT{}G'.format(team_letter)]),
                'opposition_goals': int(result['FT{}G'.format(opposition_letter)]),
                'shots': int(result['{}S'.format(team_letter)]),
                'shots_on_target': int(result['{}ST'.format(team_letter)]),
                'opposition_shots': int(result['{}S'.format(opposition_letter)]),
                'opposition_shots_on_target': int(result['{}ST'.format(opposition_letter)]),
            }

        def reduce_fn(x, y):
            result = {}
            for key in x.keys():
                result[key] = x[key] + y[key]
            return result

        return reduce(reduce_fn, map(map_fn, recent_results[-matches:]))

#####
#  Compute best score for each time, 
#  this data is used as an input for the prediction model
################
def compute_stats(df):
    teams = df['home_team'].unique()
    teams_stat = pd.DataFrame()
    columns = ['wins', 'draws', 'losses', 'goals',
        'opposition_goals', 'shots', 'shots_on_target',
        'opposition_shots', 'opposition_shots_on_target']

    location = ['home', 'away']

    for team in teams:
        team_dict = {
            'name' : team,
            # should be removed not used
            'odds_home' : df[df['home_team']==team]['odds_home'].mean(),
            'odds_away' : df[df['home_team']==team]['odds_away'].mean(),
            'odds_draw' : df[df['home_team']==team]['odds_draw'].mean()
        }
        for pos in location:
            for col in columns:
                team_dict[pos+'_'+col] = df[df[pos+'_team']==team][pos+'_'+col].max() 

        teams_stat = teams_stat.append(team_dict, ignore_index=True)
    return teams_stat

#####
# AWS lambda handler
##############
def lambda_handler(event, context):    
    URI_DATAWARE = "https://dwfootprophet.herokuapp.com/team/add"

    leagues = [
        {"name": 'France', "url":'https://www.football-data.co.uk/mmz4281/2122/F1.csv'},
        {"name": 'England', "url":'https://www.football-data.co.uk/mmz4281/2122/E0.csv'},
    ]

    for league in leagues:
        df = pd.DataFrame(Dataset(pd.read_csv(league['url'])).processed_results)
        stats_df = compute_stats(df)
        stats_df['league'] = league['name']

        for idx, row in stats_df.iterrows():
            tjson = {"team": row.to_json()}
            response = requests.post(URI_DATAWARE, json=tjson)
            print(response.json())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }