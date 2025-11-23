# ⚽ Football Data Analytics Dashboard

An interactive data-analytics dashboard for exploring FIFA player statistics across multiple game versions.  
Includes a complete data pipeline (CSV → DuckDB → SQLite), analytical SQL queries, and a Streamlit-based interactive web app.

---

## 🚀 Features

### • Players Evolution  
Compare two players across FIFA versions:
- Overall, potential, market value & wage trends  
- Attribute evolution (pace, shooting, passing, defending, etc.)  
- Automatic change-over-time calculation (value/overall delta)

### • Young Players With Highest Potential  
Filter by:
- FIFA version  
- League  
- Maximum potential  
- Number of players to return  
Ranked by potential → then by age → always returning top prospects.

### • Market Value by Position  
Track how player value evolves for selected positions across FIFA versions.  
Displays the **top 10 most valuable players per position**, averaged per year.

### • Best Matching Teams for a New Player  
Enter custom physical attributes (height, weight, age, overall).  
Find teams whose average squad profile best matches the user’s input.

### • Top 1% Elite Players  
Identify the global top 1% most valuable players  
with radar-chart visualization for key attributes.

---

## 📁 Project Structure

```
dashboard/      → Streamlit web app (app.py)
scripts/        → ETL, DuckDB⇄SQLite tools, analytical SQL queries
data/           → SQLite DB + reduced CSV dataset
schema.jpeg     → Database schema diagram
requirements.txt
```

---

## 🛠 Technologies

- Python, Pandas  
- Streamlit  
- Plotly, Matplotlib, Seaborn  
- DuckDB, SQLite  
- SQL analytics  
- ETL pipeline & preprocessing scripts  

---

## ▶️ Run the Dashboard

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically in your browser.

---

## 📦 Dataset Notes

- The repository includes a **reduced dataset** for demo purposes.  
- The full dataset can be regenerated using the DuckDB→SQLite pipeline found in `/scripts`.

---

## 📫 Contact

Feel free to reach out for questions or collaboration.
