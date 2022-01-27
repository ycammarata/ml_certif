import os
import json
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

APP_SETTINGS_DEFAULT = "config.DevelopmentConfig"

app = Flask(__name__)

### must catch the exception
try:
    app.config.from_object(os.environ['APP_SETTINGS'])
except KeyError:
    app.config.from_object(APP_SETTINGS_DEFAULT)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# avoid circulare import of db
exec(open('dbmodels.py').read())

#from dbmodels import Team

# this is required to manage db initialization
migrate = Migrate(app, db)

@app.route("/")
def welcome():
    return "Welcome to footprophet warehouse API"

@app.route("/team/add" , methods=["POST"])
def add_team():
    # Check if request has a JSON content
    if request.json:
        # Get the JSON as dictionnary
        req = request.get_json()
        # Check mandatory key
        if "team" in req.keys():
            try:
                team=Team(json.loads(req['team']))
                teamdb = Team.query.filter_by(name=team.name).first()
                # check if it is an update
                if (teamdb != None):
                    team.id = teamdb.id
                    db.session.merge(team)
                    msg =  "OK : team {} statistics updated, id is {}".format(team.name, team.id)
                else:
                    db.session.add(team)
                    msg =  "OK : team {} statistics added, id is {}".format(team.name, team.id)

                db.session.commit()
                return jsonify({"msg": msg})

            except Exception as e:
                return jsonify({"msg": "ERROR : {}".format(str(e))})
    
    return jsonify({"msg": "ERROR: not a JSON and/or no team key in your request"})

@app.route("/team/getall")
def get_all():
    try:
        teams=Team.query.all()
        return  jsonify([e.serialize() for e in teams])
    except Exception as e:
	    return(str(e))

@app.route("/team/league/<league_>")
def get_league(league_):
    try:
        teams=Team.query.filter_by(league=league_)#.first()
        return jsonify([e.serialize_short() for e in teams])
    except Exception as e:
	    return(str(e))

@app.route("/team/get/<id_>")
def get_by_id(id_):
    try:
        team=Team.query.filter_by(id=id_).first()
        if (team!=None):
            return jsonify(team.serialize())
        else:
            return jsonify({"msg": "ERROR: team with id {} does not exist".format(id_)})
    except Exception as e:
	    return(str(e))

@app.route("/team/form", methods=['GET', 'POST'])
def add_team_form():
    if request.method == 'POST':
        name=request.form.get('name')
        teamid=request.form.get('teamid')
        try:
            team = Team(name=name,teamid=teamid)
            db.session.add(team)
            db.session.commit()
            return "Team added. team id={}".format(team.id)

        except Exception as e:
	        return(str(e))

    return render_template("getdata.html")

if __name__ == '__main__':
    app.run()