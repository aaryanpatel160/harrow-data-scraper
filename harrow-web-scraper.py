import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "C:\\Users\\160aa\\Downloads\\memberIDNameTeam.xlsx"  # Replace with the correct file path
df_players = pd.read_excel(file_path)

# Function to get the PlayerID from the name
def get_player_id(first_name, surname, df):
    player = df[(df['FirstName'].str.lower() == first_name.lower()) & (df['Surname'].str.lower() == surname.lower())]
    if not player.empty:
        return player.iloc[0]['PlayerID']
    else:
        return None

# Streamlit UI
st.title("Cricket Player Profile Finder")

# Get the player's name from the user
first_name = st.text_input("Enter the player's first name:")
surname = st.text_input("Enter the player's surname:")

if st.button("Find Player"):
    # Get the PlayerID
    player_id = get_player_id(first_name, surname, df_players)

    if player_id:
        st.success(f"Player ID for {first_name} {surname} is {player_id}.")
        # Construct the URL
        url = f'https://www.harrowcricketclub.co.uk/memberprofile/memberID_{player_id}/{first_name}-{surname}.aspx'
        
        # Scrape the page
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')    
        
        recent_stats = soup.find_all('table', class_='rgMasterTable')[2]
        
        # Extract headers
        th_tags = recent_stats.find_all('th')
        headers = [th.text.strip() for th in th_tags]
        
        # Create DataFrame to hold the stats
        df_stats = pd.DataFrame(columns=headers)
        
        # Extract the rows
        tr_tags = recent_stats.find_all('tr')
        for row in tr_tags[3:]:
            row_data = row.find_all('td')
            individual_row_data = [data.text.replace('\n', '').replace('\t', '').strip() for data in row_data]
            length = len(df_stats)
            df_stats.loc[length] = individual_row_data
        
        df = df_stats
        
        # Display the dataframe
        st.dataframe(df)
        
        # Function to handle not-outs and convert batting scores to integers
        def parse_runs(batting):
            try:
                return int(batting.replace('*', ''))
            except ValueError:
                return 0
        
        # Extract relevant data for visualization
        df['Runs'] = df['Batting'].apply(parse_runs)
        df['Wickets'] = df['Bowling'].apply(lambda x: int(x.split('-')[0]) if '-' in x else 0)
        df['Catches'] = df['Fielding'].apply(lambda x: int(x.split(',')[0].split(' ')[1]))
        df['Stumpings'] = df['Fielding'].apply(lambda x: int(x.split(',')[1].split(' ')[1]))
        df['RunOuts'] = df['Fielding'].apply(lambda x: int(x.split(',')[2].split(' ')[1]))

        # Bar graph for Runs Scored per Fixture
        st.write("### Runs Scored in Each Fixture")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.bar(df['Fixture'], df['Runs'], color='skyblue')
        ax1.set_title('Runs Scored in Each Fixture')
        ax1.set_xlabel('Fixture')
        ax1.set_ylabel('Runs Scored')
        ax1.set_xticklabels(df['Fixture'], rotation=45, ha='right')
        st.pyplot(fig1)

        # Bar graph for Wickets Taken per Fixture
        st.write("### Wickets Taken in Each Fixture")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(df['Fixture'], df['Wickets'], color='lightgreen')
        ax2.set_title('Wickets Taken in Each Fixture')
        ax2.set_xlabel('Fixture')
        ax2.set_ylabel('Wickets Taken')
        ax2.set_xticklabels(df['Fixture'], rotation=45, ha='right')
        st.pyplot(fig2)

        # Pie chart for Fielding Performance
        st.write("### Fielding Performance Overview")
        fielding_totals = [df['Catches'].sum(), df['Stumpings'].sum(), df['RunOuts'].sum()]
        labels = ['Catches', 'Stumpings', 'Run-Outs']
        colors = ['#ff9999','#66b3ff','#99ff99']

        fig3, ax3 = plt.subplots(figsize=(8, 8))
        ax3.pie(fielding_totals, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax3.set_title('Fielding Performance')
        st.pyplot(fig3)
    else:
        st.error(f"No player found with the name {first_name} {surname}.")
