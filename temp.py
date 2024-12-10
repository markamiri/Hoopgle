import requests
import pandas as pd
from fuzzywuzzy import process, fuzz
headers = ["Rk", "G", "2021 Playoffs", "Series", "Tm", "Unnamed: 5", "Opp", "G#", "Unnamed: 8", "GS", "MP",
           "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK",
           "TOV", "PF", "PTS", "GmSc", "+/-"]
def playoffstats():
    name = input("Please enter the name of the player:")
    name_parts = name.split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[-1]

    url = "https://www.basketball-reference.com/players/{}/".format(last_name[0])
    response_p = requests.get(url)
    tables = pd.read_html(response_p.content)[0]
    pd.set_option('display.max_rows', None)
    file_path = "{}_players.txt".format(last_name[0])
    tables.to_csv(file_path, sep='\t', index=False)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    playoff_player_names = set()
    for line in lines:
        line = line.strip()
        player_nme = line.split()
        full_name = player_nme[0] + " " + player_nme[1]
        playoff_player_names.add(full_name)

    closest_match_name = process.extractOne(name, playoff_player_names, scorer=fuzz.token_sort_ratio)
    closest_playoff_name, similarlity_playoff_score = closest_match_name
    playoff_first_name, playoff_last_name = closest_playoff_name.split()
    playoff_sliced_first_name = playoff_first_name[:2]
    playoff_sliced_last_name = playoff_last_name[:5]
    playoff_url_playername = playoff_sliced_last_name + playoff_sliced_first_name + "01"
    career_playoff_url = "https://www.basketball-reference.com/players/{}/{}/gamelog-playoffs".format(last_name[0], playoff_url_playername)

    stat_cat = input("What stat Category are you looking for:")
    stat_dict = {
        "points": -3, "buckets": -3, "rebounds": -9, "boards": -9,
        "assists": -8, "dimes": -8, "PR": [-3, -9], "points rebounds": [-3, -9],
        "PA": [-3, -8], "points assists": [-3, -8], "pra": [-3, -9, -8], "points rebounds assists": [-3, -9, -8],
        "triple double": 0, "double double": 0, "blocks": -6, "steals": -7, "AR": [-9, -8], "assists rebounds": [-9, -8]
    }
    closest_stat = process.extractOne(stat_cat, stat_dict.keys(), scorer=fuzz.token_sort_ratio)
    closest_stat_key = closest_stat[0]
    cat_index = stat_dict.get(closest_stat_key)

    ou = input("Are you looking for the over/under")
    over_under_dict = {"over", "under"}
    closest_ou = process.extractOne(ou, over_under_dict, scorer=fuzz.token_sort_ratio)
    closest_ou_key = closest_ou[0]

    propt_num = int(input("What is the line for the " + closest_ou_key + ":"))

    response = requests.get(career_playoff_url)
    tables = pd.read_html(response.content)[7]
    pd.set_option('display.max_rows', None)

    file_path = 'output.txt'
    tables.to_csv(file_path, sep='\t', index=False)

    with open(file_path, 'r') as file:
        lines = file.readlines()

    data_arrays = [line.strip().split() for line in lines if line.strip()]
    temp_array = set()

    for i in range(len(data_arrays)):
        try:
            if closest_ou_key == "over":
                if isinstance(cat_index, int):
                    if int(data_arrays[i][cat_index]) > propt_num:
                        temp_array.add(tuple(data_arrays[i]))
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = data_arrays[i][cat_index[0]]
                    temp2 = data_arrays[i][cat_index[1]]
                    if int(temp1) + int(temp2) > propt_num:
                        temp_array.add(tuple(data_arrays[i]))
            else:
                if isinstance(cat_index, int):
                    if int(data_arrays[i][cat_index]) < propt_num:
                        temp_array.add(tuple(data_arrays[i]))
                elif isinstance(cat_index, list) and len(cat_index) == 2:
                    temp1 = data_arrays[i][cat_index[0]]
                    temp2 = data_arrays[i][cat_index[1]]
                    if int(temp1) + int(temp2) < propt_num:
                        temp_array.add(tuple(data_arrays[i]))
        except ValueError:
            continue

    inactive_games = sum(1 for row in data_arrays if len(row[1]) > 2)
    header_counter = sum(1 for row in data_arrays if row[0] == "Rk")
    active_games = len(data_arrays) - header_counter - inactive_games
    percentage = (len(temp_array) / active_games) * 100
    formatpercentage = "{:.2f}".format(percentage)
    
    
    with open("results.txt", "w") as file:
        file.write(closest_playoff_name + " has covered the " + closest_ou_key + " " + str(propt_num) + " " + str(closest_stat_key) + " in " + str(len(temp_array)) + "/" + str(active_games) + " (" + str(formatpercentage) + "%) playoff games.\n\n")
        file.write("Filtered Data:\n")
        file.write("\t".join(headers) + "\n")  # Write headers

        for row in temp_array:
            file.write("\t".join(row) + "\n")

    def latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num):
        latest_array = set()
        if data_arrays[-1][5] == "@":
            latest_series_numb = 7
            latest_series = int(data_arrays[-1][latest_series_numb])
        else:
            latest_series_numb = 6
            latest_series = int(data_arrays[-1][latest_series_numb])
        end_index = len(data_arrays) - latest_series
        i = len(data_arrays) - 1

        while i >= end_index:
            if len(data_arrays[i][1]) > 2:
                end_index -= 1
            else:
                try:
                    if closest_ou_key == "over":
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                    else:
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                except ValueError:
                    continue
            i -= 1

        with open("results.txt", "a") as file:
            file.write("\nLatest Series Data:\n")
            file.write("\t".join(headers) + "\n")  # Write headers
            for row in latest_array:
                file.write("\t".join(row) + "\n")

        return end_index

    end_index = latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num)

    def second_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index):
        latest_array = set()
        if data_arrays[end_index - 1][5] == "@":
            latest_series = int(data_arrays[end_index - 1][7])
        else:
            latest_series = int(data_arrays[end_index - 1][6])
        i = end_index - 1
        end_index = end_index - latest_series
        while i >= end_index:
            if len(data_arrays[i][1]) > 2:
                end_index -= 1
            else:
                try:
                    if closest_ou_key == "over":
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                    else:
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                except ValueError:
                    continue
            i -= 1

        with open("results.txt", "a") as file:
            file.write("\nSecond Latest Series Data:\n")
            file.write("\t".join(headers) + "\n")  # Write headers
            for row in latest_array:
                file.write("\t".join(row) + "\n")

        return end_index

    if data_arrays[end_index - 1][7].isdigit() or data_arrays[end_index - 1][6].isdigit():
        end_index = second_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index)
    else:
        with open("results.txt", "a") as file:
            file.write("\nNo second latest series\n")

    def third_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index):
        latest_array = set()
        if data_arrays[end_index - 1][5] == "@":
            latest_series = int(data_arrays[end_index - 1][7])
        else:
            latest_series = int(data_arrays[end_index - 1][6])
        i = end_index - 1
        end_index = end_index - latest_series
        while i >= end_index:
            if len(data_arrays[i][1]) > 2:
                end_index -= 1
            else:
                try:
                    if closest_ou_key == "over":
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                    else:
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                except ValueError:
                    continue
            i -= 1

        with open("results.txt", "a") as file:
            file.write("\nThird Latest Series Data:\n")
            file.write("\t".join(headers) + "\n")  # Write headers
            for row in latest_array:
                file.write("\t".join(row) + "\n")

        return end_index

    if data_arrays[end_index - 1][7].isdigit() or data_arrays[end_index - 1][6].isdigit():
        end_index = third_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index)
    else:
        with open("results.txt", "a") as file:
            file.write("\nNo third latest series\n")

    def fourth_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index):
        latest_array = set()
        if data_arrays[end_index - 1][5] == "@":
            latest_series = int(data_arrays[end_index - 1][7])
        else:
            latest_series = int(data_arrays[end_index - 1][6])
        i = end_index - 1
        end_index = end_index - latest_series
        while i >= end_index:
            if len(data_arrays[i][1]) > 2:
                end_index -= 1
            else:
                try:
                    if closest_ou_key == "over":
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 > propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                    else:
                        if isinstance(cat_index, int):
                            if int(data_arrays[i][cat_index]) < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                        elif isinstance(cat_index, list) and len(cat_index) == 2:
                            temp1 = int(data_arrays[i][cat_index[0]])
                            temp2 = int(data_arrays[i][cat_index[1]])
                            if temp1 + temp2 < propt_num:
                                latest_array.add(tuple(data_arrays[i]))
                except ValueError:
                    continue
            i -= 1

        with open("results.txt", "a") as file:
            file.write("\nFourth Latest Series Data:\n")
            file.write("\t".join(headers) + "\n")  # Write headers
            for row in latest_array:
                file.write("\t".join(row) + "\n")

        return end_index

    if data_arrays[end_index - 1][7].isdigit() or data_arrays[end_index - 1][6].isdigit():
        end_index = fourth_latest_percentage(data_arrays, closest_ou_key, cat_index, propt_num, end_index)
    else:
        with open("results.txt", "a") as file:
            file.write("\nNo fourth latest series\n")

    input("Press Enter to exit...")

playoffstats()
