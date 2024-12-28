from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import pandas as pd
from fuzzywuzzy import fuzz, process
import requests
import numpy as np
import os

import re
from fuzzywuzzy import process


app = Flask(__name__)
app.secret_key = 'your_secret_key'

#team logos
team_logo_map = {
    "ATL": "/static/team_Logo/nba-atlanta-hawks-logo.png",
    "BOS": "/static/team_Logo/nba-boston-celtics-logo.png",
    "BRK": "/static/team_Logo/nba-brooklyn-nets-logo.png",
    "CHO": "/static/team_Logo/nba-charlotte-hornets-logo.png",
    "CHI": "/static/team_Logo/nba-chicago-bulls-logo.png",
    "CLE": "/static/team_Logo/nba-cleveland-cavaliers-logo.png",
    "DAL": "/static/team_Logo/nba-dallas-mavericks-logo.png",
    "DEN": "/static/team_Logo/nba-denver-nuggets-logo.png",
    "DET": "/static/team_Logo/nba-detroit-pistons-logo.png",
    "GSW": "/static/team_Logo/nba-golden-state-warriors-logo.png",
    "HOU": "/static/team_Logo/nba-houston-rockets-logo.png",
    "IND": "/static/team_Logo/nba-indiana-pacers-logo.png",
    "LAC": "/static/team_Logo/NBA-LA-Clippers-logo.png",
    "LAL": "/static/team_Logo/nba-los-angeles-lakers-logo.png",
    "MEM": "/static/team_Logo/nba-memphis-grizzlies-logo.png",
    "MIA": "/static/team_Logo/nba-miami-heat-logo.png",
    "MIL": "/static/team_Logo/nba-milwaukee-bucks-logo.png",
    "MIN": "/static/team_Logo/nba-minnesota-timberwolves-logo.png",
    "NOP": "/static/team_Logo/nba-new-orleans-pelicans-logo.png",
    "NYK": "/static/team_Logo/nba-new-york-knicks-logo.png",
    "OKC": "/static/team_Logo//nba-oklahoma-city-thunder-logo.png",
    "ORL": "/static/team_Logo/nba-orlando-magic-logo.png",
    "PHI": "/static/team_Logo/nba-philadelphia-76ers-logo.png",
    "PHO": "/static/team_Logo/nba-phoenix-suns-logo.png",
    "POR": "/static/team_Logo/nba-portland-trail-blazers-logo.png",
    "SAC": "/static/team_Logo/nba-sacramento-kings-logo.png",
    "SAS": "/static/team_Logo/nba-san-antonio-spurs-logo.png",
    "TOR": "/static/team_Logo/nba-toronto-raptors-logo.png",
    "UTA": "/static/team_Logo/nba-utah-jazz-logo.png",
    "WAS": "/static/team_Logo/nba-washington-wizards-logo.png"
}

def clean_dataframe(df):
    # Apply the logos to the team and opponent columns
    df['Tm'] = df['Tm'].apply(add_logo)
    df['Opp'] = df['Opp'].apply(add_logo)
    
    # Drop the unwanted columns
    columns_to_drop = ["+/-", "Rk", "GmSc", "TOV", "PF", "Unnamed: 5", "Unnamed: 7", "Age", "GS"]
    df = df.drop(columns=columns_to_drop)
    
    return df

def clean_dataframe_playoff(temp_df):
    # Apply the logos to the team and opponent columns
    temp_df['Tm'] = temp_df['Tm'].apply(add_logo)
    temp_df['Opp'] = temp_df['Opp'].apply(add_logo)
    temp_df = temp_df.drop(columns=["+/-"])
    temp_df = temp_df.drop(columns=["Rk"])
    temp_df = temp_df.drop(columns=["GmSc"])
    temp_df = temp_df.drop(columns=["TOV"])
    temp_df = temp_df.drop(columns=["PF"])
    temp_df = temp_df.drop(columns=["Unnamed: 5"])
    temp_df = temp_df.drop(columns=["Unnamed: 8"])
    if "Unnamed: 31" in temp_df.columns:
        temp_df = temp_df.drop(columns=["Unnamed: 31"])
    
    return temp_df





@app.route('/')
def home():
    
    return render_template('site.html')

@app.route('/stat_search', methods=['POST'])
def stat_search1():
    query = request.form['query']
    print(query)

    tokens = query.split()
    game_logs_html = None
    url_path = "_".join(tokens)
    

    year, season, over_under, stat_cat, line, name = identify_query_components(query)
    print("Debugging Output:")
    print(f"Year: {year}")
    print(f"Season: {season}")
    print(f"Over/Under: {over_under}")
    print(f"Stat Category: {stat_cat}")
    print(f"Line: {line}")
    print(f"Name: {name}")
    name_capital = name.title()
    in_string = "in the"
    url_path_string = " ".join([name_capital, stat_cat, over_under, line, in_string, year, season])
    print(url_path_string)
    last_name = name.split()[-1]
 
    print(f"Year: {year}, Season: {season}, Over/Under: {over_under}, Stat Cat: {stat_cat}, Line: {line}, Name: {name}")

    split = regularOrPlayoffs(season)
    cat_index, closest_ou_key, propt_num, closest_stat_key = getVariables(stat_cat, over_under, line)

    print("split")
    print(split)


    if split == "regular":
        print("is this being called")
        player_url = regularURL(year, name, last_name)
        result_message, format_percentage, game_logs_html, last5_result, last5_df, last10_result, last10_df, last15_result, last15_df,  last20_result, last20_df, result_data,  format_percentage1, format_percentage2, format_percentage3, format_percentage4, games, points ,propt_num, cat, ou, opp= tableScrape(player_url, cat_index, closest_ou_key, propt_num, name, closest_stat_key, year)
        print(format_percentage, format_percentage1, format_percentage2, format_percentage3, format_percentage4)
        return render_template(
        'result.html',
        result_message = result_message,
        path=url_path_string,
        game_logs_html=game_logs_html,
        last5_result=last5_result,
        last5_df=last5_df,
        last10_result=last10_result,
        last10_df=last10_df,
        last15_result=last15_result,
        last15_df=last15_df,
        last20_result = last20_result,
        last20_df = last20_df,
        year = year,
        result_data = result_data,
        format_percentage = format_percentage,
        format_percentage1=  format_percentage1,
        format_percentage2 = format_percentage2,
        format_percentage3 = format_percentage3,
        format_percentage4 = format_percentage4, games = games, points= points, propt_num= propt_num, cat = cat, ou = ou, opp = opp,
        )
    else:
        player_url = playoffURL(name, last_name)
        print("player_url")
        print(player_url)
        end_index,total_game_logs_html, result_message, first_game_log, latest_result_string, second_game_log, second_result_string, third_game_log, third_result_string, fourth_game_log, fourth_result_string, games, points, propt_num, cat, ou, opp= playoffTableScrape(player_url, cat_index, closest_ou_key, propt_num, name, closest_stat_key)

        print("testing ou")
        print(ou)
        return render_template(
        'result.html',
        path=url_path_string,
        result_message=result_message,
        game_logs_html=total_game_logs_html,
        last5_result=latest_result_string,
        last5_df=first_game_log,
        last10_result=second_result_string,
        last10_df=second_game_log,
        last15_result=third_result_string,
        last15_df=third_game_log,
        last20_result = fourth_result_string,
        last20_df = fourth_game_log,
        end_index = end_index,
        games = games, points= points, propt_num= propt_num, cat = cat, ou= ou, opp = opp,
        
        )


@app.route('/get-player-names', methods=['GET'])
def get_player_names():
    # File path to playerName.txt
    file_path = os.path.join(os.path.dirname(__file__), 'playerName.txt')


    # Read the player names from the file
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            player_names = [line.strip() for line in file.readlines()]
        return jsonify(player_names)  # Send as JSON response
    else:
        return jsonify({"error": "File not found"}), 404


def add_logo(team_abbreviation):
    # Get the path to the logo from the team_logo_map
    logo_path = team_logo_map.get(team_abbreviation, '')
    # Create the HTML for the image, using the static path
    logo_html = f'<img src="{logo_path}" width="30" height="30" style="vertical-align: middle; margin-left: 5px;">'
    # Return the team abbreviation followed by the image, all wrapped in a span
    return f'<span>{team_abbreviation}{logo_html}</span>'

def playoffURL(name, last_name):
    print("playoff name")
    
    print("Before lower:", name, last_name)
    name = name.lower()
    last_name = last_name.lower()
    print("After lower:", name, last_name)
    url = f"https://www.basketball-reference.com/players/{last_name[0]}/"
    response_p = requests.get(url)
    tables = pd.read_html(response_p.content)[0]
    file_path = f"{last_name[0]}_players.txt"
    tables.to_csv(file_path, sep='\t', index=False)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    playoff_player_names = set()
    for line in lines:
        line = line.strip()
        player_nme = line.split()
        full_name = player_nme[0] + " " + player_nme[1]
        playoff_player_names.add(full_name)

    closest_playoff_name, _ = process.extractOne(name, playoff_player_names, scorer=fuzz.token_sort_ratio)
    playoff_first_name, playoff_last_name = closest_playoff_name.split()
    playoff_url_playername = playoff_last_name[:5] + playoff_first_name[:2] + "01"
    career_playoff_url = f"https://www.basketball-reference.com/players/{last_name[0]}/{playoff_url_playername}/gamelog-playoffs"
    print(career_playoff_url)
    return career_playoff_url

def regularOrPlayoffs(season):
    playoff_dict = {"regular", "Postseason", "Playoffs"}
    closest_split, _ = process.extractOne(season, playoff_dict, scorer=fuzz.token_sort_ratio)
    return closest_split

def regularURL(year, name, last_name):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_minute.html"
    response = requests.get(url)
    tables = pd.read_html(response.content)[0]
    file_path = f'{year}_players.txt'
    tables.to_csv(file_path, sep='\t', index=False)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    player_names = set()
    for line in lines:
        line = line.strip()
        player_nme = line.split()
        full_name = player_nme[1] + " " + player_nme[2]
        player_names.add(full_name)

    closest_name, _ = process.extractOne(name, player_names, scorer=fuzz.token_sort_ratio)
    firstname, lastname = closest_name.split()
    url_playername = None
    if lastname[:5] + firstname[:2] == "JohnsCa" or lastname[:5] + firstname[:2] == "JacksJa" or lastname[:5] + firstname[:2] == "MilleBr" or lastname[:5] + firstname[:2] == "BrownJa":
        url_playername = lastname[:5] + firstname[:2] + "02"
    else:
        url_playername = lastname[:5] + firstname[:2] + "01"


    player_link = f"https://www.basketball-reference.com/players/w/{url_playername}/gamelog/{year}"
    return player_link

def tableScrape(player_url, cat_index, closest_ou_key, propt_num, name, closest_stat_key, year):
    print("player_url")
    print(player_url)
    response = requests.get(player_url)
    tables = pd.read_html(response.content)[7]
    pd.set_option('display.max_rows', None)
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    print("should be AST")
    print(stat_key)
    # Convert the DataFrame to a list of lists
    data_arrays = tables.values.tolist()

    # Use the original column headers from the DataFrame
    columns = tables.columns.tolist()

    # Include the first row (which contains the headers in your original setup) as data
    data = data_arrays  # No need to exclude the first row


    # Create a new DataFrame with the column headers and all data including the first row
    df = pd.DataFrame(data, columns=columns)
    df = df.fillna(0)
    print("DataFrame columns:", df.columns)
    print("AST column values:\n", df['AST'])


    df['T/F'] = None
    true_counter = 0


    # Initialize an empty list to store the rows that match the condition
    rows_list = []

    # Iterate over each row of the DataFrame
    for index, row in df.iterrows():
        try:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(df.iloc[index][stat_key])>=propt_num:
                        row.loc[ 'T/F'] = '✔️'
                        true_counter+=1
                    else:
                        row.loc[ 'T/F'] = '❌'   
                  
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = row[cat_index[0]]
                    temp2 = row[cat_index[1]]
                    if int(temp1) + int(temp2) >= propt_num:
                        rows_list.append(row)
            else:
                if isinstance(cat_index, int):
                    if int(df.iloc[index][stat_key])<=propt_num:
                        row.loc[ 'T/F'] = '✔️'
                        true_counter+=1
                    else:
                        row.loc[ 'T/F'] = '❌'  
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = row[cat_index[0]]
                    temp2 = row[cat_index[1]]
                    if int(temp1) + int(temp2) <= propt_num:
                        rows_list.append(row)

            rows_list.append(row)
        except ValueError:
            continue

    # Convert the list of Series (rows) to a DataFrame
    temp_df = pd.DataFrame(rows_list, columns=df.columns)

    opp = temp_df['Opp'].tolist()

    temp_df = clean_dataframe(temp_df)
    games = temp_df['G'].tolist()

    print("printing opp")
    print(opp)
    print("printing the games")
    print(type(games))
    print(games)
    print("stat_key")
    print(stat_key)

    points = temp_df[stat_key].tolist()
    cat =stat_key
    ou = closest_ou_key
    
    # Calculate inactive games
    #inactive_games = df['G'].apply(lambda x: len(str(x)) > 2).sum()
    active_games=0
    inactive_games=0
    for i in range(len(df)):
        if str(df.loc[i, 'G']) == 'G':
            continue
        if str(df.loc[i, 'G']) == '0' or str( df.loc[i, 'PTS']) == 'Inactive' or str(df.loc[i, 'PTS']) == 'PTS' or str(df.loc[i, 'PTS']) == 'Did Not Dress':
            inactive_games+=1
        else:
            active_games+=1


    # Calculate active games
    print("active games", active_games)
    print("inactive_games", inactive_games)
    # Calculate the percentage
    percentage = (true_counter/ active_games) * 100
    format_percentage = "{:.2f}".format(percentage)
    
    # Display the final result
    result_message = f"{name} has covered the {closest_stat_key} {closest_ou_key} {propt_num}  line in {year} in {true_counter}/{active_games} ({format_percentage}%) games."
    if float(format_percentage) >= 90:
        color_class = "high"
    elif 70 <= float(format_percentage) < 90:
        color_class = "medium"
    else:
        color_class = "low"
    
    result_data = {
    "name": name,
    "closest_stat_key": closest_stat_key,
    "closest_ou_key": closest_ou_key,
    "propt_num": propt_num,
    "year": year,
    "true_counter": true_counter,
    "active_games": active_games,
    "format_percentage": format_percentage,
    "color_class": color_class
}



    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

      # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)

    last5_result = last5_df = format_percentage1 = None
    last10_result = last10_df = format_percentage2 = None
    last15_result = last15_df = format_percentage3 = None
    last20_result = last20_df = format_percentage4 = None

    #testing of last 5 percentages
    if active_games>=5:
        last5_result, last5_df, format_percentage1 =last5_percentage(df, closest_ou_key, closest_stat_key, propt_num, cat_index, name)
    if active_games>=10:
        last10_result, last10_df, format_percentage2 =last10_percentage(df, closest_ou_key, closest_stat_key, propt_num, cat_index, name)
    if active_games>=15:
        last15_result, last15_df, format_percentage3 =last15_percentage(df, closest_ou_key, closest_stat_key, propt_num, cat_index, name )
    #Error : 19 active games showing 20
    if active_games>=20:
        last20_result, last20_df, format_percentage4 =last20_percentage(df, closest_ou_key, closest_stat_key, propt_num, cat_index, name )
    format_percentage = round(float(format_percentage), 2)  # Ensure it's a float with two decimal places

    # Return the result message and temp_df for further processing if needed
    return  result_message, format_percentage, game_logs_html, last5_result, last5_df, last10_result, last10_df, last15_result, last15_df,  last20_result, last20_df, result_data, format_percentage1, format_percentage2, format_percentage3, format_percentage4, games, points, propt_num, cat,ou, opp

def getVariables(stat_cat, over_under, line):
    stat_dict = {
        "points": -3, "buckets": -3, "rebounds": -9, "boards": -9,
        "assists": -8, "dimes": -8, "PR": [-3, -9], "points rebounds": [-3, -9],
        "PA": [-3, -8], "points assists": [-3, -8], "pra": [-3, -9, -8], "points rebounds assists": [-3, -9, -8],
        "triple double": 0, "double double": 0, "blocks": -6, "steals": -7, "AR": [-9, -8], "assists rebounds": [-9, -8]
    }
    closest_stat = process.extractOne(stat_cat, stat_dict.keys(), scorer=fuzz.token_sort_ratio)
    closest_stat_key = closest_stat[0]
    cat_index = stat_dict.get(closest_stat_key)

    over_under_dict = {"over", "under"}
    closest_ou = process.extractOne(over_under, over_under_dict, scorer=fuzz.token_sort_ratio)
    closest_ou_key = closest_ou[0]

    propt_num = int(line)
    return cat_index, closest_ou_key, propt_num, closest_stat_key

def playoffTableScrape(player_url, cat_index, closest_ou_key, propt_num, name, closest_stat_key):
    #ignore the year for now, can come back to fix 
    """
    TO DO LIST 
    - make the finder work for non single like triple double, double double, three point, free throw right now it only works for 1 word stats like points
        -needs a new system in the search query(NLP)
    - Fix the year (add the last year latest stats implement it from main)
    """
    #column finder 
    stat_dict = {
        "points": -3, "buckets": -3, "rebounds": -9, "boards": -9,
        "assists": -8, "dimes": -8, "PR": [-3, -9], "points rebounds": [-3, -9],
        "PA": [-3, -8], "points assists": [-3, -8], "pra": [-3, -9, -8], "points rebounds assists": [-3, -9, -8],
        "triple double": 0, "double double": 0, "blocks": -6, "steals": -7, "AR": [-9, -8], "assists rebounds": [-9, -8]
    }
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    if stat_key is None:
        raise ValueError(f"Invalid stat key: {closest_stat_key}")
   
    response_p = requests.get(player_url)
    tables = pd.read_html(response_p.content)[7]
    pd.set_option('display.max_rows', None)
    # Convert the DataFrame to a list of lists
    data_arrays = tables.values.tolist()
    print("Data arrays before filtering:", data_arrays)
    #Error: random 0 0 0 games definitely has to do with the inactive games

    # Use the original column headers from the DataFrame
    columns = tables.columns.tolist()

    # Include the first row (which contains the headers in your original setup) as data
    data = data_arrays  # No need to exclude the first row

    # Create a new DataFrame with the column headers and all data including the first row
    df = pd.DataFrame(data, columns=columns)
    df = df.fillna(0)
   





    df['T/F'] = None    
    true_counter = 0


    # Initialize an empty list to store the rows that match the condition
    rows_list = []

    pd.set_option('display.max_rows', None)
    #The issue is, lebron point column is -3 to rudy gobert whereas is -4,  I need to fix this issue

    """
    Change the way the stat_cat is found with df['PTS].iloc[3]
    change this for both table scrape and playoff table scrape
    (DO ASAP)
    """

  # Iterate over each row of the DataFrame
    for index, row in df.iterrows():
        try:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(df.iloc[index][stat_key])>propt_num:
                        row.loc[ 'T/F'] = '✔️'
                        true_counter+=1
                    else:
                        row.loc[ 'T/F'] = '❌'    
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = row[cat_index[0]]
                    temp2 = row[cat_index[1]]
                    if int(temp1) + int(temp2) > propt_num:
                        rows_list.append(row.to_dict())
            else:
                if isinstance(cat_index, int):
                    if int(df.iloc[index][stat_key])>propt_num:
                        row.loc[ 'T/F'] = '✔️'
                        true_counter+=1
                    else:
                        row.loc[ 'T/F'] = '❌'    
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = row[cat_index[0]]
                    temp2 = row[cat_index[1]]
                    if int(temp1) + int(temp2) < propt_num:
                        rows_list.append(row.to_dict())
            rows_list.append(row.to_dict())
        except ValueError:
            continue

    # Convert the list of Series (rows) to a DataFrame
    temp_df = pd.DataFrame(rows_list, columns=df.columns)
    opp = temp_df['Opp'].tolist()


    # Calculate inactive games
    inactive_games = df['G'].apply(lambda x: len(str(x)) > 2).sum()

    # Calculate active games
    active_games = len(df) - (len(df) // 20) - inactive_games

    # Calculate the percentage
    percentage = (true_counter / active_games) * 100
    format_percentage = "{:.2f}".format(percentage)

    # Display the final result
    name = name.title()
    result_message = f"{name} has covered the {closest_ou_key} {propt_num} {closest_stat_key} line in {true_counter}/{active_games} ({format_percentage}%) total career playoff games"
    print(result_message)
   
    temp_df =clean_dataframe_playoff(temp_df)
    games = temp_df['G'].tolist()

    print(games)
    cat =stat_key
    print("stat_key")
    print(stat_key)

    points = temp_df[stat_key].tolist()

    propt_num = int(propt_num)
    ou = closest_ou_key

    print(points)
    print(propt_num)

    # Filter out indices where games, points, or opp contain numeric 0
    filtered_indices = [i for i in range(len(games)) if games[i] != 0 and points[i] != 0 and opp[i] != 0]

    # Create new filtered lists based on the filtered indices
    games = [games[i] for i in filtered_indices]
    points = [points[i] for i in filtered_indices]
    opp = [opp[i] for i in filtered_indices]
    #temp_df = temp_df.astype(str)

    temp_df = temp_df[temp_df['G#'] != 0]

    total_game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)
     # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = total_game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = total_game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    total_game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)


    end_index, first_game_log, latest_result_string = latest_percentage(df, closest_ou_key, closest_stat_key, cat_index, propt_num, name)

    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index, second_game_log, second_result_string =second_latest_percentage(df, closest_ou_key,closest_stat_key, cat_index, propt_num, name, end_index)
    else:
        return end_index, total_game_logs_html,first_game_log, latest_result_string


    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index, third_game_log, third_result_string =third_latest_percentage(df, closest_ou_key,closest_stat_key, cat_index, propt_num, name, end_index)
    else:
        return end_index,total_game_logs_html, first_game_log, latest_result_string, second_game_log, second_result_string

    if data_arrays[end_index -1][7].isdigit() or data_arrays[end_index -1][6].isdigit():
        end_index, fourth_game_log, fourth_result_string =fourth_latest_percentage(df, closest_ou_key,closest_stat_key, cat_index, propt_num, name, end_index)
    else:
        return end_index,total_game_logs_html, first_game_log, latest_result_string, second_game_log, second_result_string, third_game_log, third_result_string


    # Return the result message and temp_df for further processing if needed
    return end_index,total_game_logs_html, result_message, first_game_log, latest_result_string, second_game_log, second_result_string, third_game_log, third_result_string, fourth_game_log, fourth_result_string,games, points, propt_num, cat,ou, opp

#Query processing 
def preprocess_query(query):
    # Remove stopwords like "during", "in", "the"
    stopwords = ["during", "in", "the"]
    for word in stopwords:
        query = re.sub(rf'\b{word}\b', '', query)
    query = query.strip()
    return query

def fuzzy_match_stat_cat(query, stat_cats):
    matched_stats = []
    remaining_query = query

    # Handle multi-word phrases first
    for stat in stat_cats:
        if stat in remaining_query:
            matched_stats.append(stat)
            remaining_query = remaining_query.replace(stat, '').strip()

    # Handle single words by fuzzy matching
    words = remaining_query.split()
    for word in words:
        if len(word) > 2:  # Exclude very short words from fuzzy matching
            match, score = process.extractOne(word, stat_cats)
            if score > 85 and match not in matched_stats:  # Increase threshold and avoid duplicates
                matched_stats.append(match)
                remaining_query = remaining_query.replace(word, '').strip()

    # Combine all matched stat categories into one string
    stat_cat = ' '.join(matched_stats) if matched_stats else None

    return stat_cat, remaining_query


def identify_query_components(query):
    query = preprocess_query(query)
    query = correct_typos(query)

    # Initialize components
    year = season = over_under = stat_cat = line = name = None

    # Define patterns
    year_pattern = r"\b(19|20)\d{2}\b"
    season_pattern = r"\b(Playoffs?|Regular Season|Season|Regular|Post|Post season|playoff|regular|regular season|post season)\b"
    over_under_pattern = r"\b(Over|Under|over|under)\b"
    line_pattern = r"\b\d+(\.\d+)?\b"

    stat_cat_list = [
        "points", "rebounds", "assists", "blocks", "steals",
        "triple double", "free throw", "double double",
        "points assists", "points rebounds", "points rebounds assists",
        "assists rebounds", "three pointer"
    ]

    # Extract components
    year_match = re.search(year_pattern, query)
    if year_match:
        year = year_match.group(0)
        query = re.sub(year_pattern, '', query, 1)  # Remove year from query

    season_match = re.search(season_pattern, query)
    if season_match:
        season = season_match.group(0)
        query = re.sub(season_pattern, '', query, 1)  # Remove season from query

    over_under_match = re.search(over_under_pattern, query)
    if over_under_match:
        over_under = over_under_match.group(0)
        query = re.sub(over_under_pattern, '', query, 1)  # Remove over/under from query

    line_match = re.search(line_pattern, query)
    if line_match:
        line = line_match.group(0)
        query = re.sub(line_pattern, '', query, 1)  # Remove line from query

    stat_cat, query = fuzzy_match_stat_cat(query, stat_cat_list)
    
    # The remaining query is considered the player's name
    name = query.strip()

    # Ensure no extra words are left in the player's name
    name = ' '.join([word for word in name.split() if word.lower() not in stat_cat_list and word.lower() not in ["double", "triple"]])

    return year, season, over_under, stat_cat, line, name

def correct_typos(query):
    # Correct common typos for "over" and "under"
    typo_corrections = {
        "ovr": "over",
        "ovre": "over",
        "uder": "under",
        "undr": "under",
        "undre": "under",
        "steels": "steals",
        "stls": "steals",
        "asts": "assists",
        "boards": "rebounds",
        "pts": "points",
        "reg" : "regular"
    }
    for typo, correction in typo_corrections.items():
        query = re.sub(rf'\b{typo}\b', correction, query)
    return query


#Regular season functions
def last5_percentage(data_arrays, closest_ou_key, closest_stat_key, propt_num, cat_index, name):
    last5_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    data_arrays['T/F'] = None
    true_counter = 0

    i = len(data_arrays) - 1 
    end_index = len(data_arrays) - 6 # Ensure we don't go out of bounds

    while i> end_index: 
       
        if  str(data_arrays.loc[i, 'G']) == '0' or str( data_arrays.loc[i, 'PTS']) == 'Inactive' or str(data_arrays.loc[i, 'PTS']) == 'PTS' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Dress':
            end_index -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.loc[i, stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        last5_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.loc[i, stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        last5_array.add(tuple(data_arrays[i]))
            last5_array.append(data_arrays.iloc[i].tolist())

        i-=1
    temp_df = pd.DataFrame(last5_array, columns=data_arrays.columns)

    percentage = (true_counter/5) *100
    formatted_percentage = "{:.0f}".format(percentage)

    result_string = (f"{name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/5 ({formatted_percentage}%)")

    
    temp_df = clean_dataframe(temp_df)

    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

    # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)

    return result_string, game_logs_html, formatted_percentage



def last10_percentage(data_arrays, closest_ou_key, closest_stat_key, propt_num, cat_index,name):
    last10_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    data_arrays['T/F'] = None
    true_counter = 0
    i = len(data_arrays) - 1
    end_index = len(data_arrays) - 11 # Ensure we don't go out of bounds

    while i> end_index: 
        if str(data_arrays.loc[i, 'PTS']) == 'Inactive' or str(data_arrays.loc[i, 'PTS']) == 'PTS' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Dress' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Play':
            end_index -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.loc[i, stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'     
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        last10_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.loc[i, stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'     
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        last10_array.add(tuple(data_arrays[i]))
            last10_array.append(data_arrays.iloc[i].tolist())

        i-=1
    temp_df = pd.DataFrame(last10_array, columns=data_arrays.columns)

    percentage = (true_counter/10) *100
    formatted_percentage = "{:.0f}".format(percentage)

    result_string = (f"{name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/10 ({formatted_percentage}%)")

    temp_df = clean_dataframe(temp_df)

    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)
 # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
        

    return result_string, game_logs_html, formatted_percentage

def last15_percentage(data_arrays, closest_ou_key, closest_stat_key, propt_num, cat_index, name):
    last15_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    data_arrays['T/F'] = None
    true_counter = 0

    i = len(data_arrays) - 1
    end_index = len(data_arrays) - 16 # Ensure we don't go out of bounds

    while i> end_index: 
        if str(data_arrays.loc[i, 'PTS']) == 'Inactive' or str(data_arrays.loc[i, 'PTS']) == 'PTS' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Dress' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Play':
            end_index -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.loc[i, stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        last15_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.loc[i, stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'

                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        last15_array.add(tuple(data_arrays[i]))
            last15_array.append(data_arrays.iloc[i].tolist())
        i-=1
    temp_df = pd.DataFrame(last15_array, columns=data_arrays.columns)

    percentage = (true_counter/15) *100
    formatted_percentage = "{:.0f}".format(percentage)

    result_string = (f"{name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/15 ({formatted_percentage}%)")

    temp_df = clean_dataframe(temp_df)


    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

    # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
    return result_string, game_logs_html, formatted_percentage



def last20_percentage(data_arrays, closest_ou_key, closest_stat_key, propt_num, cat_index, name):
    last20_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    data_arrays['T/F'] = None
    true_counter = 0
    i = len(data_arrays) - 1
    end_index = len(data_arrays) - 21 # Ensure we don't go out of bounds

    while i> end_index: 
        if str(data_arrays.loc[i, 'PTS']) == 'Inactive' or str(data_arrays.loc[i, 'PTS']) == 'PTS' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Dress' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Play':
            end_index -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.loc[i, stat_key])>propt_num:
                        
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'  
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        last20_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.loc[i, stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'  
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        last20_array.add(tuple(data_arrays[i]))
            last20_array.append(data_arrays.iloc[i].tolist())
        i-=1
    temp_df = pd.DataFrame(last20_array, columns=data_arrays.columns)

    percentage = (true_counter/20) *100
    formatted_percentage = "{:.0f}".format(percentage)

    result_string = (f"{name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/20 ({formatted_percentage}%)")

    temp_df = clean_dataframe(temp_df)


    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)
# Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
 
    return result_string, game_logs_html, formatted_percentage






#Playoff functions 
def latest_percentage(data_arrays, closest_ou_key, closest_stat_key, cat_index, propt_num, closest_playoff_name):
    latest_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)

    data_arrays['T/F'] = None
    true_counter = 0
    latest_series = int(data_arrays.iloc[-1]["G#"])

    end_index = len(data_arrays) - latest_series
    i = len(data_arrays) - 1

    while i>=end_index: 
        if len(data_arrays.iloc[i, 1]) > 2:
            end_index -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.iloc[i][stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'        
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        latest_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.iloc[i][stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1
                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'   
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        latest_array.add(tuple(data_arrays[i]))
            latest_array.append(data_arrays.iloc[i].tolist())
        i-=1

    opp_team = data_arrays.loc[end_index, 'Opp']

    print("\n")
    #print(f"Latest Playoff Series vs {opp_team}")
    percentage = (true_counter/ latest_series) * 100
    formatted_percentage = "{:.0f}".format(percentage)
    # print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
    closest_playoff_name = closest_playoff_name.title()
    result_string = (f"{closest_playoff_name} playoff series vs {opp_team} where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/{latest_series}({formatted_percentage}%)")
    print(result_string)
    #Should print the games where is was not covered 
    #luka doesnt work pj washington doesnt work name issue
    #dereck lively doenst work line 162 division by zero
    end_index = end_index-1
    

    temp_df = pd.DataFrame(latest_array, columns=data_arrays.columns)

    temp_df =clean_dataframe_playoff(temp_df)



    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

    # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)




    # Now, game_logs_html contains the modified HTML with the styles applied

    return end_index, game_logs_html, result_string

def second_latest_percentage(data_arrays, closest_ou_key,closest_stat_key, cat_index, propt_num, closest_playoff_name, end_index):
    #Error: off by 1 game has to due with the inactive games 100%
    latest_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    latest_series = int(data_arrays.iloc[end_index-1]["G#"])
    data_arrays['T/F'] = None
    true_counter = 0

    i = end_index-1
    end_index =end_index - latest_series
    opp_team = data_arrays.loc[end_index, 'Opp']

    while i>=end_index: 
        print("data_arrays.iloc[i, 8]")
        print(data_arrays.iloc[i, 9])
        if pd.isna(data_arrays.iloc[i, 1]) or data_arrays.iloc[i, 9]== "Inactive" :
            i -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.iloc[i][stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'    
                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        latest_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.iloc[i][stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'  

                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        latest_array.add(tuple(data_arrays[i]))
            latest_array.append(data_arrays.iloc[i].tolist())
        i-=1


    print("\n")
    percentage = (true_counter / latest_series) * 100
    formatted_percentage = "{:.0f}".format(percentage)
    #print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
    temp_df = pd.DataFrame(latest_array, columns=data_arrays.columns)
    temp_df =clean_dataframe_playoff(temp_df)
    closest_playoff_name = closest_playoff_name.title()
    result_string = (f"{closest_playoff_name} playoff series vs {opp_team} where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/{latest_series}({formatted_percentage}%)")
    print(result_string)


    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

     # Split the HTML rows using '</tr>' but preserve the splitting point
    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
    end_index = end_index-1

    return end_index, game_logs_html, result_string

def third_latest_percentage(data_arrays, closest_ou_key, closest_stat_key, cat_index, propt_num, closest_playoff_name, end_index):
    latest_array = []
    stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
    stat_key = stat_key_finder.get(closest_stat_key)
    latest_series = int(data_arrays.iloc[end_index-1]["G#"])
    
    data_arrays['T/F'] = None
    true_counter = 0

    i = end_index-1
    end_index =end_index - latest_series
    while i>=end_index: 
        if pd.isna(data_arrays.iloc[i, 1]):
            i -=1
        else:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays.iloc[i][stat_key])>propt_num:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'

                elif isinstance(cat_index, list) and len(cat_index) ==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if int(temp1)+int(temp2)>propt_num:
                        latest_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if (int(data_arrays.iloc[i][stat_key])<propt_num) == True:
                        data_arrays.loc[i, 'T/F'] = '✔️'
                        true_counter+=1

                    else:
                        data_arrays.loc[i, 'T/F'] = '❌'
                elif isinstance(cat_index, list) and len(cat_index)==2:
                    temp1 =(data_arrays[i][cat_index[0]]) 
                    temp2 =(data_arrays[i][cat_index[1]])
                    if (int(temp1)+int(temp2)<propt_num) == True:
                        latest_array.add(tuple(data_arrays[i]))
            latest_array.append(data_arrays.iloc[i].tolist())

        i-=1
    opp_team = data_arrays.loc[end_index, 'Opp']

    print("\n")
    #print(f"Latest Playoff Series vs {opp_team}")
    percentage = (true_counter / latest_series) * 100
    formatted_percentage = "{:.0f}".format(percentage)
    #print(f"{closest_playoff_name} game logs where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {len(latest_array)}/{latest_series}({formatted_percentage}%)")
    temp_df = pd.DataFrame(latest_array, columns=data_arrays.columns)
    temp_df =clean_dataframe_playoff(temp_df)

    game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)

    rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

    # Prepare the header row separately if it exists
    header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

    # Iterate over the rows to apply the styles
    for i in range(len(rows)):
        if '✔️' in rows[i]:
            rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
        else:
            rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

    # Reconstruct the HTML
    game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
    end_index= end_index-1
    closest_playoff_name = closest_playoff_name.title()

    result_string = (f"{closest_playoff_name} playoff series vs {opp_team} where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/{latest_series}({formatted_percentage}%)")


    return end_index, game_logs_html, result_string

def fourth_latest_percentage(data_arrays, closest_ou_key, closest_stat_key,cat_index, propt_num, closest_playoff_name, end_index):
        latest_array = []
        stat_key_finder = {"points": "PTS", "rebounds": "TRB", "blocks": "BLK", "steal" : "STL", "assists": "AST", "Freethrow" : "FT", "three pointer" : "3P"}
        stat_key = stat_key_finder.get(closest_stat_key)
        latest_series = int(data_arrays.iloc[end_index-1]["G#"])

        data_arrays['T/F'] = None
        true_counter = 0
        
        i = end_index-1
        end_index =end_index - latest_series
        while i>=end_index: 
            if pd.isna(data_arrays.iloc[i, 1]):
                i -=1
            else:
                if closest_ou_key == "over":
                    if isinstance(cat_index, int):
                        if int(data_arrays.iloc[i][stat_key])>propt_num:
                            data_arrays.loc[i, 'T/F'] = '✔️'
                            true_counter+=1

                        else:
                            data_arrays.loc[i, 'T/F'] = '❌'
                    elif isinstance(cat_index, list) and len(cat_index) ==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if int(temp1)+int(temp2)>propt_num:
                            latest_array.add(tuple(data_arrays[i]))
                else:
                    if isinstance(cat_index, int):
                        if (int(data_arrays.iloc[i][stat_key])<propt_num) == True:
                            data_arrays.loc[i, 'T/F'] = '✔️'
                            true_counter+=1
                        else:
                            data_arrays.loc[i, 'T/F'] = '❌'

                    elif isinstance(cat_index, list) and len(cat_index)==2:
                        temp1 =(data_arrays[i][cat_index[0]]) 
                        temp2 =(data_arrays[i][cat_index[1]])
                        if (int(temp1)+int(temp2)<propt_num) == True:
                            latest_array.add(tuple(data_arrays[i]))
                latest_array.append(data_arrays.iloc[i].tolist())

            i-=1
        opp_team = data_arrays.loc[end_index, 'Opp']

        print("\n")
        #print(f"Latest Playoff Series vs {opp_team}")
        percentage = (true_counter / latest_series) * 100
        formatted_percentage = "{:.0f}".format(percentage)
        result_string = (f"{closest_playoff_name} playoff series vs {opp_team} where he has covered {closest_ou_key} {propt_num} {closest_stat_key}. {true_counter}/{latest_series}({formatted_percentage}%)")
        temp_df = pd.DataFrame(latest_array, columns=data_arrays.columns)
        temp_df =clean_dataframe_playoff(temp_df)

        game_logs_html = temp_df.to_html(classes='game-logs-table', index=False, escape=False)
        rows = game_logs_html.split('<tr>')[1:]  # Skip the first split which is before the first <tr>

        # Prepare the header row separately if it exists
        header_row = game_logs_html.split('<tr>')[0]  # Get the part before the first <tr>

        # Iterate over the rows to apply the styles
        for i in range(len(rows)):
            if '✔️' in rows[i]:
                rows[i] = '<tr style="background:#85BB65;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'
            else:
                rows[i] = '<tr style="background:#59343B;color:white;">' + rows[i].replace('<tr>', '').replace('</tr>', '') + '</tr>'

        # Reconstruct the HTML
        game_logs_html = header_row + '<tr>' + '</tr><tr>'.join(rows)
        closest_playoff_name = closest_playoff_name.title()


        end_index = end_index-1

        return end_index, game_logs_html, result_string




if __name__ == '__main__':
    app.run(debug=False)
