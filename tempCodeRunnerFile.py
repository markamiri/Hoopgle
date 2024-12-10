inactive_games = 0
    print(data_arrays[10][1])
    for i in range(len(data_arrays)):
        if len(data_arrays[i][1]) > 2:
            inactive_games+=1
    start_year = data_arrays[0][2]

    header_counter =0
    for i in range(len(data_arrays)):
        if (data_arrays[i][0]) == "Rk":
            header_counter+=1

    for row in temp_array:
        print(row)
    active_games =(len(data_arrays) - (header_counter) - inactive_games)
    # this needs inactive 
    percentage = (len(temp_array)/active_games)*100
    formatpercentage="{:.2f}".format(percentage)