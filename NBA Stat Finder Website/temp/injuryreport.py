from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/injuries', methods=['GET'])
def get_injury_reports():
    url = "https://www.rotowire.com/basketball/news.php?view=injuries"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        player_links = soup.find_all('a', class_='news-update__player-link')
        player_desc = soup.find_all('a', class_='news-update__headline')
        date = soup.find_all('div', class_='news-update__timestamp')
        player_desc_news = soup.find_all('div', class_='news-update__news')

        # Build the injury report data
        injury_data = []
        for i in range(len(player_links)):
            player_name = player_links[i].text.strip() if i < len(player_links) else "Unknown Player"
            description = player_desc[i].text.strip() if i < len(player_desc) else "No Description"
            timestamp = date[i].text.strip() if i < len(date) else "No Date"
            news = player_desc_news[i].text.strip() if i < len(player_desc_news) else "No Additional News"

            injury_data.append({
                "player_name": player_name,
                "description": description,
                "timestamp": timestamp,
                "news": news
            })

        return jsonify(injury_data)
    else:
        return jsonify({"error": "Failed to retrieve the page."}), 500

if __name__ == "__main__":
    app.run(debug=True)
