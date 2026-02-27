from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('wearable.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT, lat REAL, lng REAL, bpm INTEGER,
                  panic BOOLEAN, fall BOOLEAN, sound BOOLEAN,
                  food BOOLEAN, water BOOLEAN, restroom BOOLEAN)''')
    conn.commit()
    conn.close()

init_db()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AEGIS.SYS // Emergency Monitor</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root { --bg-main: #0a0c10; --bg-panel: #11141a; --accent: #00d2ff; --danger: #ff3333; --text-main: #e0e0e0; --border: #1f2533; }
        body { font-family: 'Share Tech Mono', monospace; background-color: var(--bg-main); color: var(--text-main); margin: 0; padding: 15px; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 220px; border-right: 1px solid var(--border); padding-right: 15px; display: flex; flex-direction: column; }
        .main-content { flex-grow: 1; padding-left: 20px; display: flex; flex-direction: column; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--border); background: var(--bg-panel); padding: 10px 20px; margin-bottom: 15px; }
        .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px; }
        .bottom-row { display: flex; gap: 15px; flex-grow: 1; min-height: 0; }
        .map-wrapper { flex: 2; border: 1px solid var(--accent); position: relative; }
        #map { height: 100%; width: 100%; }
        .side-panels { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .card { background: var(--bg-panel); border: 1px solid var(--border); padding: 15px; display: flex; flex-direction: column; justify-content: space-between; }
        .card-header { font-size: 0.8rem; display: flex; justify-content: space-between; margin-bottom: 15px; color: #7a8b99; }
        .card-value { font-size: 2rem; color: #fff; }
        .terminal { background: var(--bg-panel); border: 1px solid var(--accent); padding: 15px; flex: 2; overflow-y: auto; font-size: 0.8rem; }
        .log-entry { margin-bottom: 5px; }
        .log-time { color: #7a8b99; }
        .log-msg { color: var(--accent); }
        .log-danger { color: var(--danger); font-weight: bold;}
        
        /* NEW MASSIVE ALERT BANNER */
        #emergency-banner {
            display: none;
            background-color: var(--danger);
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 1.5rem;
            font-weight: bold;
            border-radius: 5px;
            margin-bottom: 15px;
            text-transform: uppercase;
            animation: blink 1s infinite;
        }
        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>
    <div class="sidebar">
        <div style="color: var(--accent); font-size: 1.5rem; margin-bottom: 40px;">● AEGIS.SYS</div>
        <div style="font-size: 0.7rem; color: #7a8b99; margin-bottom: 10px;">DEVICE STATUS</div>
        <div style="margin-bottom: 15px;">BATTERY: <span style="color: #00ff00;">100%</span></div>
        <div>UPLINK: <span id="signal-text">--%</span></div>
    </div>

    <div class="main-content">
        <div class="top-bar">
            <h2>EMERGENCY MONITOR</h2>
            <span id="val-conn" style="color: var(--accent);">CONNECTING...</span>
        </div>

        <div id="emergency-banner">CHILD REQUEST ALERT!</div>

        <div class="stats-row">
            <div class="card"><div class="card-header">HEART RATE ♥</div><div class="card-value" id="val-bpm">--</div></div>
            <div class="card"><div class="card-header">MIC SENSOR ∿</div><div class="card-value" id="val-noise" style="font-size: 1.5rem;">QUIET</div></div>
            <div class="card"><div class="card-header">FALL STATUS ⚠</div><div class="card-value" id="val-fall" style="font-size: 1.5rem;">STABLE</div></div>
            <div class="card"><div class="card-header">CHILD NEEDS 🛎️</div><div class="card-value" id="val-needs" style="font-size: 1.2rem; color: #00ff00;">ALL GOOD</div></div>
        </div>

        <div class="bottom-row">
            <div class="map-wrapper"><div id="map"></div></div>
            <div class="side-panels">
                <div class="terminal" id="terminal">
                    <div style="color: var(--accent); margin-bottom: 10px; border-bottom: 1px solid #1f2533; padding-bottom: 5px;">SYSTEM TERMINAL_</div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map', {zoomControl: false}).setView([11.9416, 79.8083], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        var marker = L.circleMarker([11.9416, 79.8083], { radius: 8, fillColor: "#00d2ff", color: "#000", weight: 2, opacity: 1, fillOpacity: 0.8 }).addTo(map);

        function addLog(msg, isDanger = false) {
            const term = document.getElementById('terminal');
            const time = new Date().toLocaleTimeString('en-US', {hour12:false});
            const colorClass = isDanger ? 'log-danger' : 'log-msg';
            term.innerHTML += `<div class="log-entry"><span class="log-time">[${time}] ></span> <span class="${colorClass}">${msg}</span></div>`;
            term.scrollTop = term.scrollHeight; 
        }

        let lastState = { food: false, water: false, restroom: false, fall: false, sound: false, panic: false };

        setInterval(function() {
            fetch('/api/latest').then(r => r.json()).then(data => {
                if(data.error) return;
                
                document.getElementById('val-conn').innerText = "LINK ACTIVE";
                document.getElementById('signal-text').innerText = "98%";
                document.getElementById('val-bpm').innerText = data.bpm;
                
                // MIC LOGIC
                if(data.sound) {
                    document.getElementById('val-noise').innerText = "LOUD!";
                    document.getElementById('val-noise').style.color = "var(--danger)";
                    if(!lastState.sound) addLog("ALERT: High Noise / Crying Detected", true);
                } else {
                    document.getElementById('val-noise').innerText = "QUIET";
                    document.getElementById('val-noise').style.color = "#fff";
                }

                // FALL LOGIC
                if(data.fall) {
                    document.getElementById('val-fall').innerText = "IMPACT!";
                    document.getElementById('val-fall').style.color = "var(--danger)";
                    if(!lastState.fall) addLog("CRITICAL: Fall Detected", true);
                } else {
                    document.getElementById('val-fall').innerText = "STABLE";
                    document.getElementById('val-fall').style.color = "#fff";
                }

                // --- NEW BUTTON UI LOGIC ---
                let needs = [];
                if(data.food) needs.push("HUNGRY");
                if(data.water) needs.push("THIRSTY");
                if(data.restroom) needs.push("RESTROOM");

                const banner = document.getElementById('emergency-banner');
                const needsCard = document.getElementById('val-needs');

                if (needs.length > 0) {
                    // Flash the big banner and play an alert sound
                    banner.style.display = "block";
                    banner.innerText = "CHILD REQUEST: " + needs.join(" & ");
                    needsCard.innerText = needs.join(" & ");
                    needsCard.style.color = "var(--danger)";
                    
                    if(!lastState.food && data.food) { addLog("BUTTON PRESSED: HUNGRY", true); alert("⚠️ CHILD IS HUNGRY!"); }
                    if(!lastState.water && data.water) { addLog("BUTTON PRESSED: THIRSTY", true); alert("⚠️ CHILD IS THIRSTY!"); }
                    if(!lastState.restroom && data.restroom) { addLog("BUTTON PRESSED: RESTROOM", true); alert("⚠️ CHILD NEEDS RESTROOM!"); }
                } else {
                    banner.style.display = "none";
                    needsCard.innerText = "ALL GOOD";
                    needsCard.style.color = "#00ff00";
                }

                // GPS LOGIC
                if(data.lat !== 0 && data.lng !== 0) {
                    let latlng = new L.LatLng(data.lat, data.lng);
                    marker.setLatLng(latlng);
                    map.setView(latlng, 15);
                }
                lastState = data;
            }).catch(e => document.getElementById('val-conn').innerText = "NO SIGNAL");
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        conn = sqlite3.connect('wearable.db')
        c = conn.cursor()
        c.execute('''INSERT INTO sensor_data (timestamp, lat, lng, bpm, panic, fall, sound, food, water, restroom)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.get('lat',0.0), data.get('lng',0.0), data.get('bpm',0),
                   data.get('panic',False), data.get('fall',False), data.get('sound',False), data.get('food',False), data.get('water',False), data.get('restroom',False)))
        conn.commit(); conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/latest')
def get_latest():
    conn = sqlite3.connect('wearable.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({"timestamp": row[1], "lat": row[2], "lng": row[3], "bpm": row[4], "panic": bool(row[5]), "fall": bool(row[6]), "sound": bool(row[7]), "food": bool(row[8]), "water": bool(row[9]), "restroom": bool(row[10])})
    return jsonify({"error": "No data"})

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
