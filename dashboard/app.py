import streamlit as st
import sys
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# הוספת תיקיית 'scripts' לנתיב החיפוש
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from duckdb_queries import get_players_evolution, get_young_players_potential, get_top_1_percent_players, \
    get_market_value_by_position, get_best_matching_teams

# קביעת הנתיב למסד הנתונים
sqlite_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "db_file.sqlite"))
def get_connection():
    """Establish a connection to SQLite database."""
    return sqlite3.connect(sqlite_file)

def get_players_list():
    """Retrieve player names from the database."""

    try:
        conn = sqlite3.connect(sqlite_file)
        players = [row[0] for row in
                   conn.execute("SELECT DISTINCT short_name FROM fifa_players ORDER BY short_name;").fetchall()]
        conn.close()
        return players
    except Exception as e:
        st.error(f"Error loading players list: {e}")
        return []

def get_available_fifa_versions():
    """Retrieve unique FIFA versions dynamically from the database."""
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT fifa_version FROM fifa_players ORDER BY fifa_version;")
        available_versions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return available_versions if available_versions else [2023]  # ברירת מחדל לשנה האחרונה
    except Exception as e:
        print(f"Error retrieving FIFA versions: {e}")
        return [2023]  # אם יש שגיאה, נחזיר ברירת מחדל

def get_available_leagues():
    """Retrieve available leagues dynamically from the database."""
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT league_name FROM fifa_players ORDER BY league_name;")
        available_leagues = [row[0] for row in cursor.fetchall()]
        conn.close()
        return available_leagues if available_leagues else []
    except Exception as e:
        print(f"Error retrieving leagues: {e}")
        return []

def get_available_positions():
    """Retrieve unique player positions from the database."""
    conn = sqlite3.connect(sqlite_file)
    positions = [row[0] for row in conn.execute("SELECT DISTINCT player_positions FROM fifa_players ORDER BY player_positions;").fetchall()]
    conn.close()
    return positions


def get_teams_by_league(selected_fifa, selected_league):
    """Get unique teams from a league in a specific FIFA version."""
    conn = sqlite3.connect(sqlite_file)
    teams = [row[0] for row in conn.execute(
        "SELECT DISTINCT club_name FROM fifa_players WHERE fifa_version = ? AND league_name = ? ORDER BY club_name;",
        (selected_fifa, selected_league)
    ).fetchall()]
    conn.close()
    return teams






st.title("⚽ FIFA Players Dashboard")

# Retrieve player list from database
players_list = get_players_list()

# Select first two players as default
default_players = players_list[:2] if len(players_list) >= 2 else []

###  Compare Players Evolution
st.subheader("📈 Compare Players Evolution")
st.markdown("""
This section allows you to **track the evolution of two players over different FIFA versions**.
- You can **select any two players** from the dataset.
- The table shows their **overall rating, potential, market value, wage, and key attributes**.
- The **'Value Change' and 'Overall Change'** columns indicate how much their rating and value have increased or decreased over time.
- **❓ Questions to explore:**
    - Which players had the biggest improvement over time?
    - Do high-value players always have a steady increase in performance?
""")

selected_players = st.multiselect("Select two players:", players_list, default=default_players)

if len(selected_players) == 2:
    st.dataframe(get_players_evolution(selected_players))
else:
    st.warning("Please select exactly two players.")



### 🌟 Players with Highest Potential
st.subheader("🌟 Players with Highest Potential")
st.markdown("""
This section displays **the top young players with the highest potential** based on user-selected criteria.
- **Choose a FIFA version**. 
- **Select a league**.
- **Set a maximum potential threshold** to filter the results.
- **Choose how many players to display** – the system will always show **X players with the highest potential**, prioritizing those with the highest rating.
- If multiple players have the same potential, **younger players will be prioritized**.
-if a player have few different potential score for the same year, we take the max.
- **❓ Questions to explore:**
    - Which leagues have the most high-potential young players?
    - Are young players with high potential already expensive?
    - How does a player's potential vary across different FIFA versions?
""")

# שליפת גרסאות FIFA וליגות מהדאטהבייס
available_fifa_versions = get_available_fifa_versions()
available_leagues = get_available_leagues()

# בחירת גרסת FIFA וליגה
selected_fifa = st.selectbox("Select FIFA Version:", available_fifa_versions, index=len(available_fifa_versions) - 1, key="select_fifa_box1")
selected_league = st.selectbox("Select a League:", available_leagues, key="select_league")

# בחירת דירוג פוטנציאלי מקסימלי
max_potential = st.slider("Maximum potential rating:", 50, 99, 90)

# בחירת מספר שחקנים להצגה
num_players = st.slider("Number of players to display:", 5, 50, 10)

# הרצת השאילתה עם הפרמטרים שנבחרו
young_players = get_young_players_potential(selected_fifa, selected_league, max_potential, num_players)

# הצגת הנתונים בטבלה או הודעת אזהרה
if not young_players.empty:
    st.dataframe(young_players)
else:
    st.warning("No players found for the selected criteria. Try adjusting the filters.")


###  market value by position
st.subheader("🏆 Market Value Trend by Position")
st.markdown("""

This graph visualizes **the average market value (value_eur) of the top 10 most valuable players in selected positions** across different FIFA versions.

📊 What does each axis represent?
- **X-axis:** FIFA versions – showing the evolution of player values over time.
- **Y-axis:** Average market value (€) – representing the **mean value of the top 10 most expensive players in each position**.

🔍 How does the data work?
- The **top 10 most expensive players** in each selected position **per FIFA version** are ranked.
- The **average value of these top 5 players is calculated and plotted**.
- This allows us to track **the financial progression of key positions** over different FIFA versions.

❓ Questions to explore:
- Which positions have seen the biggest increase in player value over the years?
- Are certain positions consistently more expensive than others?
- Do player values spike at certain FIFA versions due to major transfers or emerging stars?
""")


# שליפת רשימת העמדות הזמינות
available_positions = get_available_positions()
selected_positions = st.multiselect("Select positions to compare:", available_positions, default=["ST", "CM", "GK"])

# שליפת הנתונים מהדאטהבייס
if selected_positions:
    position_trends = get_market_value_by_position(selected_positions)

    if not position_trends.empty:
        # יצירת הגרף עם Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        for position in selected_positions:
            data = position_trends[position_trends["player_positions"] == position]
            ax.plot(data["fifa_version"], data["avg_value"], marker="o", label=position)

        ax.set_xlabel("FIFA Version")
        ax.set_ylabel("Average Market Value (€)")
        ax.set_title("Market Value Trend by Position")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected positions.")

### 👥⚽ Best Matching Teams for Your Profile
st.subheader("👥⚽ Find the Most Suitable Teams in the league for your new player!")

st.markdown("""
**create a new player**
Enter your **physical attributes** and find out which teams in the selected **league and FIFA version** are the best fit for your profile.
- The results show **all teams** where the **average** height, weight, age, and overall rating of the players **closely match your input**.
- **Only teams that fit within the allowed deviation are displayed**.
""")

# בחירת גרסת FIFA וליגה
selected_fifa = st.selectbox("Select FIFA Version:", get_available_fifa_versions(), key="fifa_teams")
selected_league = st.selectbox("Select a League:", get_available_leagues(), key="league_teams")

# הזנת נתונים פיזיים
height = st.slider("Select Height (cm):", 150, 210, 175)
weight = st.slider("Select Weight (kg):", 50, 110, 70)
age = st.slider("Select Age:", 16, 40, 25)
overall = st.slider("Select Overall Rating:", 50, 99, 75)

# הפעלת השאילתה והצגת התוצאה
if st.button("Find Best Matching Teams"):
    matching_teams = get_best_matching_teams(selected_fifa, selected_league, height, weight, age, overall)

    if not matching_teams.empty:
        st.markdown("### ✅ Teams That Best Match Your Profile")
        st.dataframe(matching_teams)
    else:
        st.warning("⚠ No teams were found that closely match your criteria. Try adjusting your inputs slightly.")




### Top 1% Players Attributes
st.subheader("🏆 Top 1% Players Attributes")
st.markdown("""
This section identifies **the top 1% of players based on market value**.
- You can **filter by position** to analyze specific roles.
- The table includes **overall rating, potential, club, nationality, and all major attributes**.
- A **radar chart** is generated to visualize the average attributes of the top players.
- **💡 Questions to explore:**
    - Which attributes define the most valuable players?
    - Are certain positions more valuable than others?
""")

conn = get_connection()
position_list = ["All"] + [row[0] for row in conn.execute("SELECT DISTINCT club_position FROM fifa_players ORDER BY club_position;").fetchall()]
selected_position = st.selectbox("Filter by position:", position_list,key="position_selector3")

top_players = get_top_1_percent_players(selected_position)
st.dataframe(top_players)

if len(top_players) > 0:
    radar_data = top_players[["pace", "shooting", "passing", "dribbling", "defending", "physic"]].mean()
    fig = px.line_polar(radar_data, r=radar_data.values, theta=radar_data.index, line_close=True)
    st.plotly_chart(fig)

