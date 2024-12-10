import tkinter
import customtkinter
from PIL import Image, ImageTk
import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import shutil
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

nlp = spacy.load("en_core_web_sm")

# Define custom stop words
custom_stop_words = {"season", "seasons", "stats", "stat"}


def parse_input(user_input):
    # Process the input sentence with spaCy
    doc = nlp(user_input)
    
    tokens = [token.text.lower() for token in doc]
    
    season_keywords = ["regular", "playoff", "post", "postseason"]
    stat_keywords = [
        "points", "buckets", "rebounds", "boards",
        "assists", "dimes", "pr", "points rebounds",
        "pa", "points assists", "pra", "points rebounds assists",
        "triple double", "double double", "blocks", "steals", "ar", "assists rebounds"
    ]
    over_under_keywords = ["over", "under"]

    over_under = ""
    season_type = ""
    stat_category = ""
    line = ""
    year = ""
    player_name_parts = []

    # Helper flags
    found_season = False
    found_stat = False
    found_line = False
    found_year = False
    found_over_under = False

    def fuzzy_match(word, choices, threshold=80):
        match, score = process.extractOne(word, choices, scorer=fuzz.ratio)
        if score >= threshold:
            return match
        return None

    # Remove custom stop words from tokens
    tokens = [token for token in tokens if token not in custom_stop_words]

    # Iterate through tokens and identify each component
    for token in tokens:
        if not found_season:
            matched_season = fuzzy_match(token, season_keywords)
            if matched_season:
                season_type = matched_season
                found_season = True
                continue

        if not found_stat:
            matched_stat = fuzzy_match(token, stat_keywords)
            if matched_stat:
                stat_category = matched_stat
                found_stat = True
                continue

        if not found_over_under and token in over_under_keywords:
            over_under = token
            found_over_under = True
            continue

        if not found_line and token.isdigit() and len(token) <= 2:
            line = token
            found_line = True
            continue

        if not found_year and token.isdigit() and len(token) == 4:
            year = token
            found_year = True
            continue

        # If it's none of the above, it's part of the player's name
        if not nlp.vocab[token].is_stop:
            player_name_parts.append(token)

    # Join the player name parts to form the full name
    player_name = " ".join(player_name_parts).title()
    player_name = player_name.lower()
    return player_name, season_type, stat_category, over_under, line, year


#system setting

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

#Our app frame
app = customtkinter.CTk()
app.geometry("720x480")
app.title("hoopgle")


#adding UI elements
title = customtkinter.CTkLabel(app, text= "Search Player propts")
title.pack(padx=10, pady=10)

#Search Box
link =customtkinter.CTkEntry(app, width= 350, height = 40, placeholder_text="Search player props (e.g., over/under)")
link.pack()

# Function to handle the Search button click
def search():
    user_input = link.get()
    player_name, season_type, stat_category, over_under, line_num, year = parse_input(user_input)

    print(f"Player Name: {player_name}")
    print(f"Season Type: {season_type}")
    print(f"Stat Category: {stat_category}")
    print(f"Over/Under: {over_under}")
    print(f"Line: {line_num}")
    print(f"Year: {year}")
    
    # Add your search functionality here

# Function to handle the I'm Feeling Lucky button click
def feeling_lucky():
    print("I'm Feeling Lucky clicked")
    # Add your I'm Feeling Lucky functionality here

# Create a frame to contain the buttons
button_frame = tkinter.Frame(app, bg= '#242424')
button_frame.pack(pady=10)

# Create the Search button
search_button = customtkinter.CTkButton(button_frame, text="Search", command=search)
search_button.pack(side="left", padx=5)

# Create the I'm Feeling Lucky button
lucky_button = customtkinter.CTkButton(button_frame, text="I'm Feeling Lucky", command=feeling_lucky)
lucky_button.pack(side="left", padx=5)


#Run app
app.mainloop()