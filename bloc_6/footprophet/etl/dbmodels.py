
#from flask_sqlalchemy import SQLAlchemy
#db = SQLAlchemy()

# from models import Team
class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    league = db.Column(db.String())

    odds_home = db.Column(db.Float)
    odss_away = db.Column(db.Float)
    odds_draw = db.Column(db.Float)

    home_wins = db.Column(db.Float)
    home_draws = db.Column(db.Float)
    home_losses = db.Column(db.Float)
    home_goals = db.Column(db.Float)
    home_shots = db.Column(db.Float)
    home_shots_on_target = db.Column(db.Float)
    home_opposition_goals = db.Column(db.Float)
    home_opposition_shots = db.Column(db.Float)
    home_opposition_shots_on_target = db.Column(db.Float)

    away_wins = db.Column(db.Float)
    away_draws = db.Column(db.Float)
    away_losses = db.Column(db.Float)
    away_goals = db.Column(db.Float)
    away_shots = db.Column(db.Float)
    away_shots_on_target = db.Column(db.Float)
    away_opposition_goals = db.Column(db.Float)
    away_opposition_shots = db.Column(db.Float)
    away_opposition_shots_on_target = db.Column(db.Float)
    
    def __init__(self, json_input):
        self.id = None
        self.name = json_input['name']
        self.league = json_input['league']
        self.odds_home = json_input['odds_home']
        self.odss_away = json_input['odds_away']
        self.odds_draw = json_input['odds_draw']
        self.home_wins = json_input['home_wins']
        self.home_draws = json_input['home_draws']
        self.home_losses = json_input['home_losses']
        self.home_goals = json_input['home_goals']
        self.home_shots = json_input['home_shots']
        self.home_shots_on_target = json_input['home_shots_on_target']
        self.home_opposition_goals = json_input['home_opposition_goals']
        self.home_opposition_shots = json_input['home_opposition_shots']
        self.home_opposition_shots_on_target = json_input['home_opposition_shots_on_target']
        self.away_wins = json_input['away_wins']
        self.away_draws = json_input['away_draws']
        self.away_losses = json_input['away_losses']
        self.away_goals = json_input['away_goals']
        self.away_shots = json_input['away_shots']
        self.away_shots_on_target = json_input['away_shots_on_target']
        self.away_opposition_goals = json_input['away_opposition_goals']
        self.away_opposition_shots = json_input['away_opposition_shots']
        self.away_opposition_shots_on_target = json_input['away_opposition_shots_on_target']
    
    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize_short(self):
        return {
            'id': self.id, 
            'name': self.name,
            'league' : self.league
        }
    
    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'league' : self.league,
            'odds_home': self.odds_home,
            'odds_away': self.odss_away,
            'odds_draw': self.odds_draw,
            'home_wins': self.home_wins,
            'home_draws': self.home_draws,
            'home_losses': self.home_losses,
            'home_goals': self.home_goals,
            'home_shots':self.home_shots,
            'home_shots_on_target' : self.home_shots_on_target,
            'home_opposition_goals' : self.home_opposition_goals,
            'home_opposition_shots' : self.home_opposition_shots,
            'home_opposition_shots_on_target' : self.home_opposition_shots_on_target,
            'away_wins': self.away_wins,
            'away_draws': self.away_draws,
            'away_losses' : self.away_losses,
            'away_goals' : self.away_goals,
            'away_shots' : self.away_shots,
            'away_shots_on_target' : self.away_shots_on_target,
            'away_opposition_goals' : self.away_opposition_goals,
            'away_opposition_shots' : self.away_opposition_shots,
            'away_opposition_shots_on_target' : self.away_opposition_shots_on_target
        }
