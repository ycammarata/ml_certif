import streamlit as st
import pandas as pd
import numpy as np
import requests
import pickle
from PIL import Image

# ----------
# Defining functions
@st.cache
def display_all_team(country):
    url = "https://dwfootprophet.herokuapp.com/team/league/" + country
    response = requests.get(url)
    
    name_to_display = []
    for elt in range(len(response.json())):
        name_to_display.append(response.json()[elt]['name'])
    
    return name_to_display

@st.cache
def all_name_id(country, team):
    url = "https://dwfootprophet.herokuapp.com/team/league/" + country
    response = requests.get(url)
    
    for elt in range(len(response.json())):
        if response.json()[elt]['name'] == team:
            id = response.json()[elt]['id']
    
    return id

@st.cache
def team_stats(id):
    url = "https://dwfootprophet.herokuapp.com/team/get/" + str(id)
    response = requests.get(url)
    
    team_dict = response.json()
    team_df = pd.DataFrame()
    team_df = team_df.append(team_dict, ignore_index=True)
    team_df = team_df[team_df.columns[::-1]]
    
    return team_df

# ----------
# App header title
st.set_page_config(page_title="The Foot Prophet App", layout="wide")

# ----------
# Loading image
player = Image.open('images/player.png')
ball = Image.open('images/ball.png')
prophet = Image.open('images/prophet.png')

# ----------
# Display main title & logo
# main_title, logo = st.columns((2, 1))
main_title, logo = st.columns((2, 1))

css_title = '<p style="font-family:Arial Black; color:White; font-size: 60px;">Foot<i style="font-family:Arial Black; color:Black; font-size: 40px;">prophet</i></p>'
main_title.markdown(css_title, unsafe_allow_html=True)
# main_title.title('Foot ***Prophet***')

logo.image(prophet, width=300)
# logo.image(ball, width=70)

# ----------
# Display info about the app
st.markdown("""
This app is designed to predict the outcome of a soccer match
""")

expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries**: streamlit, pandas, numpy, requests, pickle
* **Data Source**: [football-data.co.uk](https://www.football-data.co.uk/)
* **Authors**: Yves Cammarata, Pierre Adda, Jules Walbert
""")

# ----------
# First page column: sidebar input selection
col1 = st.sidebar
col1.header('Leagues')

selected_leagues = col1.selectbox('Select a league', list(['France', 'England']))
col1.write('---')

col1.header('Teams')
selected_home_team = col1.selectbox('Home Team', display_all_team(selected_leagues))
selected_away_team = col1.selectbox('Away Team', display_all_team(selected_leagues))

# ----------
# Second page column: dataframe construction & prediction
if selected_home_team == selected_away_team:
    st.error("Please choose two different teams !")
else:
    col2, col3 = st.columns((5, 1))
    col2.subheader('Team Stats')
    
    selected_home_id = all_name_id(selected_leagues, selected_home_team)
    selected_away_id = all_name_id(selected_leagues, selected_away_team)
    
    HomeTeam = team_stats(selected_home_id)
    AwayTeam = team_stats(selected_away_id)
    
    # ----------
    # Columns cleaning & display dataframe
    HomeTeam = HomeTeam[[
        'name', 'home_wins', 'home_draws', 'home_losses',
        'home_goals', 'home_opposition_goals', 'home_shots',
        'home_shoats_on_target', 'home_opposition_shots', 'home_opposition_shots_on_target']]
    
    AwayTeam = AwayTeam[[
        'name', 'away_wins', 'away_draws', 'away_losses',
        'away_goals', 'away_opposition_goals', 'away_shots',
        'away_shots_on_target', 'away_opposition_shots', 'away_opposition_shots_on_target']]
    
    # CSS to inject contained in a string (method streamlit to avoid index display)
    hide_dataframe_row_index = """
        <style>
        .row_heading.level0 {display:none}
        .blank {display:none}
        </style>
        """
    
    # Inject CSS with Markdown (method streamlit to avoid index display)
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
    
    col2.dataframe(HomeTeam.style.format({ 'home_wins': '{:.0f}', 'home_draws': '{:.0f}', 'home_losses': '{:.0f}',
        'home_goals': '{:.0f}', 'home_opposition_goals': '{:.0f}', 'home_shots': '{:.0f}',
        'home_shoats_on_target': '{:.0f}', 'home_opposition_shots': '{:.0f}', 'home_opposition_shots_on_target': '{:.0f}'}))
    
    col2.dataframe(AwayTeam.style.format({ 'away_wins': '{:.0f}', 'away_draws': '{:.0f}', 'away_losses': '{:.0f}',
        'away_goals': '{:.0f}', 'away_opposition_goals': '{:.0f}', 'away_shots': '{:.0f}',
        'away_shots_on_target': '{:.0f}', 'away_opposition_shots': '{:.0f}', 'away_opposition_shots_on_target': '{:.0f}'}))
    
    # ----------
    # Prediction preparation
    col2.subheader('Prediction')
    mlp_classifier = pickle.load(open('mlp_classifier.pkl', 'rb'))
    
    HomeTeam = HomeTeam.drop(['name'], axis=1)
    AwayTeam = AwayTeam.drop(['name'], axis=1)
    stats = np.concatenate((HomeTeam.values.reshape(-1), AwayTeam.values.reshape(-1)))
    
    prediction = mlp_classifier.predict([stats])[0]
    result = np.array(['Draw', 'Home', 'Away'])
    result = result[prediction]
    
    if result == 'Home':
        col2.success(selected_home_team + " wins against " + selected_away_team)
    elif result == 'Away':
        col2.success(selected_away_team + " wins against " + selected_home_team)
    else:
        col2.write('Draw')
    
    col3.write('Other model ?')
