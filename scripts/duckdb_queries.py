import sqlite3
import pandas as pd
import os

# Path to SQLite database
# קבלת הנתיב של התיקייה שבה נמצא הקובץ הנוכחי
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# בניית הנתיב לדאטהבייס כך שיתאים לכל נתיב שבו הפרויקט ממוקם
sqlite_file = os.path.join(BASE_DIR, "..", "data", "db_file.sqlite")


def run_query(query, params=()):
    conn = sqlite3.connect(sqlite_file)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def get_players_evolution(selected_players):
    """Track the evolution of selected players over different FIFA versions."""

    placeholders = ",".join(["?" for _ in selected_players])

    query = f"""
    SELECT 
        short_name,
        fifa_version,
        GROUP_CONCAT(DISTINCT overall) AS overall_values,  
        GROUP_CONCAT(DISTINCT potential) AS potential_values,  
        GROUP_CONCAT(DISTINCT value_eur) AS value_values,  
        GROUP_CONCAT(DISTINCT wage_eur) AS wage_values,  
        GROUP_CONCAT(DISTINCT pace) AS pace_values,
        GROUP_CONCAT(DISTINCT shooting) AS shooting_values,
        GROUP_CONCAT(DISTINCT passing) AS passing_values,
        GROUP_CONCAT(DISTINCT dribbling) AS dribbling_values,
        GROUP_CONCAT(DISTINCT defending) AS defending_values,
        GROUP_CONCAT(DISTINCT physic) AS physic_values,
        value_eur - LAG(value_eur) OVER(PARTITION BY short_name ORDER BY fifa_version) AS value_change,
        overall - LAG(overall) OVER(PARTITION BY short_name ORDER BY fifa_version) AS overall_change
    FROM fifa_players
    WHERE short_name IN ({placeholders})
    GROUP BY short_name, fifa_version
    ORDER BY fifa_version ASC, short_name ASC;

    """

    return run_query(query, tuple(selected_players))



def get_young_players_potential(selected_fifa: int, selected_league: str, max_potential: int, num_players: int):
    """Retrieve young players with high potential while keeping only the highest potential per player."""

    query = """
        WITH ranked_players AS (
            SELECT 
                short_name, 
                fifa_version,  
                age, 
                club_name, 
                nationality_name, 
                league_name,  
                GROUP_CONCAT(DISTINCT overall) AS overall,  
                MAX(potential) AS potential,  -- ✅ לוקח את הפוטנציאל הגבוה ביותר בלבד
                GROUP_CONCAT(DISTINCT COALESCE(value_eur, 0)) AS value_eur,  
                GROUP_CONCAT(DISTINCT COALESCE(wage_eur, 0)) AS wage_eur,  
                ROW_NUMBER() OVER (
                    ORDER BY MAX(potential) DESC, age ASC
                ) AS rank  -- ✅ דירוג לפי פוטנציאל מקסימלי ואז לפי גיל עולה
            FROM fifa_players
            WHERE fifa_version = ?  
              AND league_name = ?  
              AND potential IS NOT NULL  
              AND potential <= ?  
            GROUP BY short_name, fifa_version, age, club_name, nationality_name, league_name
        )
        SELECT * FROM ranked_players
        WHERE rank <= ?  -- ✅ מציג רק את מספר השחקנים שהמשתמש ביקש
        ORDER BY potential DESC, age ASC;  -- ✅ ממיין לפי פוטנציאל (יורד) ואז לפי גיל (עולה)
    """

    # הגדרת הפרמטרים עבור השאילתה
    params = (selected_fifa, selected_league, max_potential, num_players)

    return run_query(query, params)



def get_market_value_by_position(selected_positions):
    """Retrieve the average market value (value_eur) of top 10 players in each selected position over FIFA versions."""

    placeholders = ",".join(["?" for _ in selected_positions])

    query = f"""
    WITH ranked_players AS (
        SELECT 
            fifa_version,
            player_positions,
            value_eur,
            RANK() OVER(PARTITION BY fifa_version, player_positions ORDER BY value_eur DESC) AS rank
        FROM fifa_players
        WHERE player_positions IN ({placeholders})  
    )
    SELECT 
        fifa_version, 
        player_positions, 
        AVG(value_eur) AS avg_value
    FROM ranked_players
    WHERE rank <= 10  -- ✅ בוחרים רק את 10 השחקנים היקרים ביותר בכל עמדה
    GROUP BY fifa_version, player_positions
    ORDER BY fifa_version ASC;
    """

    return run_query(query, tuple(selected_positions))


def get_best_matching_teams(selected_fifa, selected_league, height, weight, age, overall):
    """Find teams where the average physical attributes of their players closely match the user's input."""

    query = """
    WITH team_averages AS (
        SELECT 
            club_name,
            AVG(height_cm) AS avg_height,
            AVG(weight_kg) AS avg_weight,
            AVG(age) AS avg_age,
            AVG(overall) AS avg_overall
        FROM fifa_players
        WHERE fifa_version = ? 
          AND league_name = ?
        GROUP BY club_name
    )
    SELECT club_name
    FROM team_averages
    WHERE 
        (ABS(avg_height - ?) <= 5)  -- התאמה לגובה
        AND (ABS(avg_weight - ?) <= 7)  -- התאמה למשקל (הגדלנו ל-7)
        AND (ABS(avg_age - ?) <= 8)  -- התאמה לגיל (הגדלנו ל-8)
        AND (ABS(avg_overall - ?) <= 6)  -- התאמה לדירוג כללי
    ORDER BY club_name ASC;
    """

    params = (
        selected_fifa, selected_league,
        height, weight, age, overall  # פרמטרים להשוואה עם ממוצעי הקבוצות
    )

    return run_query(query, params)



def get_top_1_percent_players(selected_position="All"):
    """Retrieve top 1% of players using PERCENT_RANK, GROUP BY, and HAVING."""

    query = """
    WITH ranked_players AS (
        SELECT 
            short_name, 
            club_name, 
            nationality_name, 
            overall, 
            potential, 
            pace, 
            shooting, 
            passing, 
            dribbling, 
            defending, 
            physic, 
            club_position, 
            value_eur,
            international_reputation,
            PERCENT_RANK() OVER(ORDER BY value_eur DESC) AS percentile_rank
        FROM fifa_players
    )
    SELECT 
        short_name, 
        club_name, 
        nationality_name, 
        overall, 
        potential, 
        pace, 
        shooting, 
        passing, 
        dribbling, 
        defending, 
        physic, 
        club_position, 
        value_eur,
        international_reputation
    FROM ranked_players
    WHERE percentile_rank <= 0.01
    """

    params = ()

    if selected_position != "All":
        query += " AND club_position = ?"
        params = (selected_position,)

    query += """
    GROUP BY short_name, club_name, nationality_name, overall, potential, pace, shooting, passing, 
             dribbling, defending, physic, club_position, value_eur, international_reputation
    """

    query += """
    HAVING international_reputation IS NOT NULL AND international_reputation >= 1
    ORDER BY value_eur DESC;
    """

    return run_query(query, params)