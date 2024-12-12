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
        if str(data_arrays.loc[i, 'PTS']) == 'Inactive' or str(data_arrays.loc[i, 'PTS']) == 'PTS' or str(data_arrays.loc[i, 'PTS']) == 'Did Not Dress':
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

