import csv
import datetime
from functools import reduce


class Dataset:
    def __init__(self, file_path):
        self.raw_results = []
        self.processed_results = []
        with open(file_path, encoding='latin1') as stream:
            reader = csv.DictReader(stream)

            count=0
            for row in reader:
                try:
                    row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%Y')
                except BaseException as err:
                    try:
                        row['Date'] = datetime.datetime.strptime(row['Date'], '%d/%m/%y')
                    except BaseException as err:
                        print(f"* Unexpected {err=}, {type(err)=}"+':'+file_path)
                        print('Error in line :', count)
                        continue
                count+=1
                self.raw_results.append(row)
        count=0
        for result in self.raw_results: 
            try:
                home_statistics = self.get_statistics(result['HomeTeam'], result['Date'])
    
                if home_statistics is None:
                    continue
    
                away_statistics = self.get_statistics(result['AwayTeam'], result['Date'])
    
                if away_statistics is None:
                    continue
    
                processed_result = {
                    'result': result['FTR']
                }
                
                for label, statistics in [('home', home_statistics), ('away', away_statistics)]:
                    for key in statistics.keys():
                        processed_result[label + '-' + key] = statistics[key]
    
                self.processed_results.append(processed_result)
                count+=1
            except BaseException as err:
                print(f"Processing results, Unexpected {err=}, {type(err)=}"+':'+file_path)
                print('Error in line :', count, result)
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
    def get_statistics(self, team, date, matches=10):
        try:
            recent_results = self.filter(team, date)
        except:
            print('Error while filtering results')

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
                'opposition-goals': int(result['FT{}G'.format(opposition_letter)]),
                'shots': int(result['{}S'.format(team_letter)]),
                'shots-on-target': int(result['{}ST'.format(team_letter)]),
                'opposition-shots': int(result['{}S'.format(opposition_letter)]),
                'opposition-shots-on-target': int(result['{}ST'.format(opposition_letter)]),
            }

        def reduce_fn(x, y):
            result = {}

            for key in x.keys():
                result[key] = x[key] + y[key]

            return result

        return reduce(reduce_fn, map(map_fn, recent_results[-matches:]))
