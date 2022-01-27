
## Inspired from this post thanks !!!
https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc


## 1 ########################################
# Must create a specific environment so we can package only the minimum
# mandatory package for deployement
conda create -n etl python=3.9
conda activate etl

## ####################
## 2 ########################################
Follow the steps from the link above innstall postgres first

## 3 ########################################
pip install flask
pip install flask_sqlalchemy
# not sure this one is required anymore since que are now
# using heroko cli command pip install flask_script
pip install flask_migrate
pip install psycopg2-binary 

## CREATE USER prophet WITH PASSWORD 'footprophet' CREATEDB;
createdb -O prophet footprophetdb
## psql -U prophet -d footprophetdb (did not create prophet user in postgres)
## psql -d footprophetdb

## local config
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql://localhost/footprophetdb"

# DB setup locally use heroku CLI command 
## WARNING if you recreate a database you should drop this table : delete from alembic_version;
flask db init  # (creates a migrations directory, to be removed prior of recreating db)
flask db migrate
flask db upgrade

# Heroku setup 
heroku create dlfootprophet 
git remote add heroku https://git.heroku.com/dwfootprophet.git
heroku config:set APP_SETTINGS=config.ProductionConfig --remote heroku
heroku addons:create heroku-postgresql:hobby-dev --app dwfootprophet
heroku config --app dwfootprophet


heroku logs --tail -a dwfootprophet

## db creation on heroku
heroku run flask db upgrade

# Acces directly remote database
heroku pg:psql postgresql-flat-42374 --app dwfootprophet

# Sample of local URL
curl -i -H "Content-Type: application/json" -X POST -d '{ "team" : {"name" : "Paris Saint Germain", "league":"France", "odds_home": "1.0", "odds_away":"1.1", "odds_draw":"1.2"}}' http://127.0.0.1:5000/team/add


curl -i -H "Content-Type: application/json" -X POST -d '{"team"
: {"name":"Southampton","odds_home":"2.2566666667","odds_away":"3.2066666667","odds_draw":"3.4333333333","home_wins":2.6666666667,"home_draws":3.6666666667,"home_losses":3.6666666667,"home_goals":8.3333333333,"home_opposition_goals":12.6666666667,"home_shots":127.3333333333,"home_shots_on_target":35.6666666667,"home_opposition_shots":119.6666666667,"home_opposition_shots_on_target":39.6666666667,"away_wins":3.0,"away_draws":3.75,"away_losses":3.25,"away_goals":9.5,"away_opposition_goals":12.75,"away_shots":132.5,"away_shots_on_target":38.0,"away_opposition_shots":118.25,"away_opposition_shots_on_target":41.0,"league":"England"}}' http://127.0.0.1:5000/team/add


http://127.0.0.1:5000/team/league/France (returns all the team in the specified league)


http://127.0.0.1:5000/team/getall (not recommended)

http://127.0.0.1:5000/team/get/13

http://127.0.0.1:5000/team/form

## ###############################################
## Basic postgres command
## ###############################################
postgres=# \db
        List of tablespaces
    Name    |   Owner    | Location 
------------+------------+----------
 pg_default | ycammarata | 
 pg_global  | ycammarata | 
(2 rows)

postgres=# \du
                                    List of roles
 Role name  |                         Attributes                         | Member of 
------------+------------------------------------------------------------+-----------
 prophet    | Create DB                                                  | {}
 ycammarata | Superuser, Create role, Create DB, Replication, Bypass RLS | {}

postgres=# \d
Did not find any relations.
postgres=# \db
        List of tablespaces
    Name    |   Owner    | Location 
------------+------------+----------
 pg_default | ycammarata | 
 pg_global  | ycammarata | 
(2 rows)

postgres=# \l
                                  List of databases
     Name      |   Owner    | Encoding | Collate | Ctype |     Access privileges     
---------------+------------+----------+---------+-------+---------------------------
 footprophetdb | prophet    | UTF8     | C       | C     | 
 postgres      | ycammarata | UTF8     | C       | C     | 
 template0     | ycammarata | UTF8     | C       | C     | =c/ycammarata            +
               |            |          |         |       | ycammarata=CTc/ycammarata
 template1     | ycammarata | UTF8     | C       | C     | =c/ycammarata            +
               |            |          |         |       | ycammarata=CTc/ycammarata
(4 rows)

postgres=# \c footprophetdb
You are now connected to database "footprophetdb" as user "ycammarata".
footprophetdb=# \dt
               List of relations
 Schema |      Name       | Type  |   Owner    
--------+-----------------+-------+------------
 public | alembic_version | table | ycammarata
 public | team            | table | ycammarata
(2 rows)

footprophetdb=# \dt team
         List of relations
 Schema | Name | Type  |   Owner    
--------+------+-------+------------
 public | team | table | ycammarata
(1 row)

footprophetdb=# \d team
                                 Table "public.team"
 Column |       Type        | Collation | Nullable |             Default              
--------+-------------------+-----------+----------+----------------------------------
 id     | integer           |           | not null | nextval('team_id_seq'::regclass)
 teamid | integer           |           |          | 
 name   | character varying |           |          | 
Indexes:
    "team_pkey" PRIMARY KEY, btree (id)

## ####### LAMBDA ###############
## inspired from : https://towardsdatascience.com/python-packages-in-aws-lambda-made-easy-8fbc78520e30 
## (might need private navigation windows)
## #######################################
conda create --no-default-packages -n lambda python=3.9
conda activate lambda
pip install pandas
conda deactivate

cp -r ~/miniforge3/envs/lambda/lib/python3.9/site-packages/* .
zip -r aws_pandas_layer.zip aws_pandas_layer
aws lambda publish-layer-version --layer-name pandas --zip-file fileb://aws_pandas_layer.zip --compatible-runtimes python3.9


### Inspired from this documentation
### https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/

# to create docker container (you me located in the directory containing Dockerfile)
docker build -t applambda .

# to run the container locally
docker run -p 9000:8080 applambda

# to delete the container
docker images rm -f applambda

# get the id of the container id
docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS                    NAMES
6c2945517218   9ba5b688fb8b   "/entry.sh app.lambd…"   2 weeks ago   Up 2 weeks   0.0.0.0:9000->8080/tcp   boring_leakey

# stop the container before being able to delete it 
docker stop 6c2945517218
docker image rm -f 9ba5b688fb8b

# to launch the trigger 
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
