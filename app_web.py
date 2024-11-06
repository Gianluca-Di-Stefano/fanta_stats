import kagglehub
import requests
import json
import pandas as pd
import os
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import plotly.express as px
from tkinterweb import HtmlFrame 
import warnings
warnings.filterwarnings("ignore")
import streamlit as st
import plotly.express as px

# season_names = ['2014', '2015', '2016', '2017', '2018', '2019']
# leagues = ['EPL', 'La_liga', 'Bundesliga', 'Serie_A', 'Ligue_1']

season_names = ['2022', '2023', '2024']
gws = ['5']
leagues = ['EPL', 'La_liga', 'Bundesliga', 'Serie_A', 'Ligue_1']
# Lista per memorizzare i nomi dei giocatori selezionati
selected_players_list = []

def scrape_understat(payload):
    #Build request using url, headers (mimicking what Firefox does normally)
    #Works best with verify=True as you won't get the ssl errors. Payload is
    #taylored for each request
    url = 'https://understat.com/main/getPlayersStats/'
    headers = {'content-type':'application/json; charset=utf-8',
    'Host': 'understat.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': '39',
    'Origin': 'https: // understat.com',
    'Connection': 'keep - alive',
    'Referer': 'https: // understat.com / league / Serie_A'
    }
    response = requests.post(url, data=payload, headers = headers, verify=True)
    response_json = response.json()
    inner_wrapper = response_json['response']
    json_player_data = inner_wrapper['players']
    return json_player_data

def clean_df(player_df, weeks):
    # Get rid of the columns that we don't care about
    player_df.drop(['xGChain','xGBuildup'], axis=1, inplace=True)
    player_df["time"] = (player_df["time"].astype(int)/player_df["games"].astype(int)).astype(str)
    player_df  = player_df.rename(columns={'time':"min_PG", 'goals':'goals_'+weeks,'xG':'xG_'+weeks,'assists':'assists_'+weeks, 'xA':'xA_'+weeks, 'shots':'shots_'+weeks, 'key_passes':
        'key_passes_'+weeks,'npg':'npg_'+weeks,'npxG':'npxG_'+weeks})
    return(player_df)

def gw_data(season , league,  no_of_gw):
    # Create Pandas dataframes from each html table
    print('Getting data for last {} matches'.format(no_of_gw))
    print(f"Season {season}/{int(season)+1}")
    print(f"League {league}")
    json_player_data = scrape_understat({'league':'Serie_A', 'season':season, 'n_last_matches': no_of_gw})
    gw_table = pd.DataFrame(json_player_data)
    gw_df = clean_df(gw_table, f"{no_of_gw}wks")
    #Replace Position indentifiers with something more useful
    gw_df['position'] = gw_df['position'].str.slice(0,1)
    position_map = {'D':'DEF', 'F':'FWD', 'M':'MID', 'G':'GK', 'S':'FWD'}
    gw_df = gw_df.replace({'position': position_map})
    gw_df.to_csv(r'last_{}_gw_data.csv'.format(no_of_gw), encoding='utf-8', index=False)
    print('last {} matches csv data written'.format(no_of_gw))
    return gw_df

def season_data(season, league):
    st.info(f"Getting data for {league} season {season}/{int(season)+1} ")
    json_player_data = scrape_understat({'league': league, 'season':season})
    season_table = pd.DataFrame(json_player_data)
    season_df = clean_df(season_table, 'season')

    season_df["games"] = season_df["games"].astype(int)
    season_df["min_PG"] = round(season_df["min_PG"].astype(float), 2)
    season_df["goals_season"] = season_df["goals_season"].astype(int)
    season_df["xG_season"] = round(season_df["xG_season"].astype(float), 2)
    season_df["assists_season"] = season_df["assists_season"].astype(int)
    season_df["xA_season"] = round(season_df["xA_season"].astype(float), 2)
    season_df["shots_season"] = season_df["shots_season"].astype(int)
    season_df["key_passes_season"] = season_df["key_passes_season"].astype(int)
    season_df["yellow_cards"] = season_df["yellow_cards"].astype(int)
    season_df["red_cards"] = season_df["red_cards"].astype(int)
    season_df["npg_season"] = season_df["npg_season"].astype(int)
    season_df["npxG_season"] = round(season_df["npxG_season"].astype(float), 2)

    st.success('data loaded')

    return season_df

def select_players(selected_players_list):
    # Filtro il DataFrame con i giocatori selezionati nella lista "My Players"
    selected_players_df = season[season["player_name"].isin(selected_players_list)]

    if not selected_players_df.empty:  # Controlla se ci sono giocatori selezionati
        # Calcolo delle differenze e stato di performance
        selected_players_df['Goal_Diff'] = selected_players_df['goals_season'] - selected_players_df['xG_season']
        selected_players_df['Assist_Diff'] = selected_players_df['assists_season'] - selected_players_df['xA_season']

        # Filtra i giocatori per sotto-performance e sovra-performance
        underperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] < 0) & (selected_players_df['Assist_Diff'] < 0)]
        overperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] >= 0) & (selected_players_df['Assist_Diff'] >= 0)]
        assist_underperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] >= 0) & (selected_players_df['Assist_Diff'] < 0)]
        assist_overperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] <= 0) & (selected_players_df['Assist_Diff'] > 0)]
        goal_underperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] < 0) & (selected_players_df['Assist_Diff'] >= 0)]
        goal_overperforming_players = selected_players_df[(selected_players_df['Goal_Diff'] > 0) & (selected_players_df['Assist_Diff'] <= 0)]

        # Aggiungi lo stato di performance ai DataFrame
        underperforming_players['Status'] = 'Underperforming'
        overperforming_players['Status'] = 'Overperforming'
        assist_underperforming_players['Status'] = 'A_Underperforming'
        assist_overperforming_players['Status'] = 'A_Overperforming'
        goal_underperforming_players['Status'] = 'G_Underperforming'
        goal_overperforming_players['Status'] = 'G_Overperforming'

        all_players = pd.concat([underperforming_players, overperforming_players, assist_underperforming_players, assist_overperforming_players, goal_underperforming_players, goal_overperforming_players])

        # Creazione del grafico con Plotly
        fig = px.scatter(
            all_players,
            x='Goal_Diff',
            y='Assist_Diff',
            color='Status',
            hover_name='player_name',
            hover_data={
                'goals_season': True,
                'xG_season': True,
                'assists_season': True,
                'xA_season': True,
                'Goal_Diff': True,
                'Assist_Diff': True,
                'position': True
            },
            labels={
                'goals_season': 'Goals',
                'xG_season': 'Expected Goals',
                'assists_season': 'Assists',
                'xA_season': 'Expected Assists',
                'Goal_Diff': 'Goal Difference',
                'Assist_Diff': 'Assist Difference',
                'Status': 'Performance Status',
                'position': 'Pos'
            },
            title="Player Performance: Goal vs Assist Difference"
        )
                # Aggiungi le linee degli assi x e y
        fig.add_shape(
            type="line", x0=-1, x1=1, y0=0, y1=0, line=dict(color="Gray", width=1), xref="paper"
        )
        fig.add_shape(
            type="line", x0=0, x1=0, y0=-1, y1=1, line=dict(color="Gray", width=1), yref="paper"
        )
        st.plotly_chart(fig)
    else:
        st.error("Please select at least one player.")


#---------------------MAIN----------------------------

# Inizializza `season` in `session_state` se non esiste ancora
if "season" not in st.session_state:
    st.session_state.season = pd.DataFrame()

st.title("FANTA STATS")
st.header("Welcome to fantastats app!")

#Liste per scegliere stagione e campionato
league_name = st.selectbox("Select league", leagues)
season_name = st.selectbox("Select season", season_names)

button_upload_season = st.button("upload dataset")

if button_upload_season:
    st.session_state.season = season_data(season_name, league_name)

if not st.session_state.season.empty:
    season = st.session_state.season
    st.divider()
    st.subheader("Player performance: Overrated vs Underrated")
    st.write("You can:")
    st.write("- Import your players file") 
    st.write("- Chose your file from list below")
    st.write("- Export your players list for future loading")
    st.write("- Calculate underrated/overrated scatterplot of selected players")

    # Bottone per importare una lista di giocatori da un file
    uploaded_file = st.file_uploader("Import players from file", type="csv")

    # Lista di giocatori importati
    imported_player_names = []

    # Se è stato caricato un file, leggilo e riempi la lista dei giocatori importati
    if uploaded_file is not None:
        # Legge il file CSV caricato
        imported_players_df = pd.read_csv(uploaded_file)
        
        # Aggiungi alla lista i nomi dei giocatori importati
        imported_player_names = imported_players_df["player_name"].tolist()
        st.success(f"Imported players")

    # Selettore multiplo per i giocatori, precompilato con i giocatori importati
    selected_players_list = st.multiselect("Choose players", season["player_name"], default=imported_player_names)

    # Bottone per calcolare le statistiche
    if st.button("Calculate Und/Ovrr"):
        select_players(selected_players_list)

    # Bottone per esportare i giocatori selezionati
    if selected_players_list:
        # Crea un DataFrame solo con i giocatori selezionati
        selected_players_df = season[season["player_name"].isin(selected_players_list)]
        
        # Conversione del DataFrame in CSV
        csv = selected_players_df.to_csv(index=False).encode('utf-8')
        
        # Bottone per scaricare il file CSV
        st.download_button(
            label="Export players to file",
            data=csv,
            file_name="selected_players.csv",
            mime="text/csv"
        )