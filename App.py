import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64

st.title('NBA Player Stats Visualization')
st.markdown("""
This app scrapes NBA player stats from basketball-reference.com and creates a heatmap showing the correlation between different player ststistics.
* **Python Libraries:** streamlit, pandas, numpy, matplotlib, seaborn
* **Data Source:** https://www.basketball-reference.com/.
""")

#Sidebar header
st.sidebar.header('Filter by:')

#Sidebar selecting which year to scrape data for
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2022))))

# Scraping player stats from basketball-reference.com
@st.cache # Caches retrieved data
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw_data = df.drop(df[df.Age == 'Age'].index) # Deletes redundant headers
    raw_data = raw_data.fillna(0)
    player_stats = raw_data.drop(['Rk'], axis=1)
    return player_stats
player_stats = load_data(selected_year)

# Sidebar for filtering data by team
sorted_teams = sorted(player_stats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_teams, sorted_teams)

# Sidebar for filtering data by position
pos = ['PG','SG','SF','PF','C']
selected_pos = st.sidebar.multiselect('Position', pos, pos)

# Data filtration by team and or position
df_selected_team = player_stats[(player_stats.Tm.isin(selected_team)) & (player_stats.Pos.isin(selected_pos))]
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
test = df_selected_team.astype(str)
st.dataframe(test)

# Download csv of filtered data
def download_file(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="player_stats.csv">Download CSV File</a>'
    return href
st.markdown(download_file(df_selected_team), unsafe_allow_html=True)

# Correlation heatmap
if st.button('Display Heatmap'):
    st.header('Correlation Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)