import pandas as pd

# Sample DataFrame mimicking the data structure
data = {
    'Game Type': ['Ranked Solo'],
    'Timestamp': ['a day ago'],
    'KDA': ['8 / 12 / 24'],
    'KDA Ratio': ['2.67:1 KDA'],
    'Victory': ['Victory'],
    'Duration': ['36m 43s'],
    'Laning': ['Laning 36: 64'],
    'P/Kill': ['P/Kill 57%'],
    'CS': ['CS 213 (5.8)'],
    'Rank': ['Emerald 3'],
    'Medal': ['Resilience']
}

df = pd.DataFrame(data)

# Styling function to mimic the UI
def style_row(row):
    return [
        'background-color: #3B4B72; color: white; text-align: left; font-size: 12pt; padding: 10px;' 
        for _ in row
    ]

# Apply the styling
styled_df = df.style.apply(style_row, axis=1)

# Save the styled DataFrame to an HTML file
html = styled_df.to_html()

with open('styled_dataframe.html', 'w') as f:
    f.write(html)