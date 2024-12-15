import requests
from bs4 import BeautifulSoup

def scrape_and_save_player_names():
    # URL of the page to scrape
    url = "https://basketball.realgm.com/nba/players"

    # File path to save player names
    file_path = r"C:\Users\Mark\Desktop\NBA Stat Finder\NBA Stat Finder Website\playerName.txt"

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        print("GET request successful. Status code:", response.status_code)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        print("HTML content parsed successfully.")

        # Find the table containing player data
        table = soup.find("table", {"class": "tablesaw"})
        if not table:
            print("Table with class 'tablesaw' not found.")
            return

        # Extract all rows from the table body
        tbody = table.find("tbody")
        if not tbody:
            print("Table body ('<tbody>') not found.")
            return

        rows = tbody.find_all("tr")
        print(f"Number of rows found in table body: {len(rows)}")

        # Extract player names
        player_names = []
        for index, row in enumerate(rows):
            # Find the cell with `data-th="Player"`
            name_cell = row.find("td", {"data-th": "Player"})
            if name_cell:
                # Find the <a> tag inside the cell to get the player's name
                name_link = name_cell.find("a")
                if name_link:
                    player_name = name_link.get_text(strip=True)
                    print(f"Player name found: {player_name}")
                    player_names.append(player_name)
                else:
                    print(f"No <a> tag found in the 'Player' cell for row {index + 1}.")
            else:
                print(f"No 'Player' cell found for row {index + 1}.")

        # Clear the file and write player names
        try:
            with open(file_path, "w") as file:
                # Clear the file by opening in write mode, then write player names
                for name in player_names:
                    file.write(name + "\n")
            print(f"Player names written to {file_path} successfully.")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")

# Call the function to scrape and save names
scrape_and_save_player_names()
