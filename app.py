from flask import Flask, render_template, request
import requests
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

API_KEY = "2c69fe263529a3b4892796eb96622b54"

 
def init_db():
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()

 
@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    error = None

    if request.method == 'POST':
        city = request.form['city']

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

           
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            weather = {
                "city": city.title(),
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "desc": data["weather"][0]["description"],
                "time": current_time
            }

          
            conn = sqlite3.connect('weather.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO history (city) VALUES (?)", (city,))
            conn.commit()
            conn.close()

        else:
            error = "City not found or API issue!"

    return render_template('index.html', weather=weather, error=error)

 
@app.route('/history')
def history():
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute("SELECT city FROM history ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return render_template('history.html', data=data)

 
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))