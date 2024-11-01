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

# season_names = ['2014', '2015', '2016', '2017', '2018', '2019']
# gws = ['3', '5', '10']
# leagues = ['EPL', 'La_liga', 'Bundesliga', 'Serie_A', 'Ligue_1']

season_names = ['2024']
gws = ['5']
leagues = ['Serie_A']

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
    print(f"Getting data for season {season}/{int(season)+1}")
    print(f"League {league}")
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

    season_df.to_csv(r'{}_whole_season_data.csv'.format(season), encoding='utf-8', index=False)
    print('csv file for {} season written'.format(season))

    return season_df

def update_listbox(*args):
    search_term = search_entry.get().lower()
    listbox.delete(0, tk.END)

    # Filtra i giocatori in base al termine di ricerca
    filtered_players = season[season["player_name"].str.lower().str.contains(search_term)]

    # Memorizza gli ID filtrati per il confronto successivo
    filtered_ids = []

    for _, player in filtered_players.iterrows():
        listbox.insert(tk.END, player["player_name"])
        filtered_ids.append(player["id"])

        # Se il giocatore è già selezionato, evidenzialo
        if player["id"] in selected_players_ids:
            listbox.selection_set(listbox.size() - 1)  # Seleziona l'ultimo elemento aggiunto

    # Deseleziona gli ID non più presenti nella lista filtrata
    for i in range(listbox.size()):
        player_id = season.loc[season["player_name"] == listbox.get(i), "id"].values[0]
        if player_id not in filtered_ids:
            listbox.selection_clear(i)

def select_players():
    selected_indices = listbox.curselection()
    selected_players = [listbox.get(i) for i in selected_indices]

    if not selected_players:  # Verifica se ci sono giocatori selezionati
        messagebox.showerror("No Selection", "Please select at least one player.")
        return  # Esci dalla funzione se non ci sono selezioni

    # Aggiorna la selezione degli ID dei giocatori
    global selected_players_ids
    selected_players_ids = [season.loc[season["player_name"] == player_name, "id"].values[0] for player_name in selected_players]

    print("Lista di ID selezionati:", selected_players_ids)

    # Filtro il DataFrame con i giocatori selezionati
    selected_players_df = season[season["id"].isin(selected_players_ids)]

    if not selected_players_df.empty:  # Controlla se ci sono giocatori selezionati
        messagebox.showinfo("Selected Players", f"{', '.join(selected_players)} selezionati!")

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
            },
            labels={
                'goals_season': 'Goals',
                'xG_season': 'Expected Goals',
                'assists_season': 'Assists',
                'xA_season': 'Expected Assists',
                'Goal_Diff': 'Goal Difference',
                'Assist_Diff': 'Assist Difference',
                'Status': 'Performance Status'
            },
            title="Player Performance: Goal vs Assist Difference"
        )
        
        fig.show()
    else:
        messagebox.showerror("No Selection", "Please select at least one player.")

season = season_data(season_names[0], leagues[0])

root = tk.Tk()
root.title("Player Selection for Performance Analysis")
root.geometry("400x600")

label = tk.Label(root, text="Select Players", font=("Arial", 14))
label.pack(pady=10)

search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)
search_entry.insert(0, "Cerca giocatore...")
search_entry.bind("<KeyRelease>", update_listbox)

listbox = tk.Listbox(root, selectmode="multiple", width=50, height=20)
listbox.pack()

# Inserisci tutti i giocatori inizialmente nella Listbox
for _, player in season.iterrows():
    listbox.insert(tk.END, player["player_name"])

button = tk.Button(root, text="Analyze Selected Players", command=select_players)
button.pack(pady=20)

root.mainloop()