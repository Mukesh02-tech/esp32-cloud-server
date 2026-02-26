HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AEGIS.SYS // Emergency Monitor</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0a0c10;
            --bg-panel: #11141a;
            --bg-panel-light: #181c24;
            --accent: #00d2ff;
            --accent-dim: rgba(0, 210, 255, 0.2);
            --danger: #ff3333;
            --text-main: #e0e0e0;
            --text-dim: #7a8b99;
            --border: #1f2533;
        }

        body {
            font-family: 'Share Tech Mono', monospace;
            background-color: var(--bg-main);
            color: var(--text-main);
            margin: 0;
            padding: 15px;
            display: flex;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
        }

        /* --- Layout Grid --- */
        .sidebar {
            width: 220px;
            border-right: 1px solid var(--border);
            padding-right: 15px;
            display: flex;
            flex-direction: column;
        }
        
        .main-content {
            flex-grow: 1;
            padding-left: 20px;
            display: flex;
            flex-direction: column;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
            background: var(--bg-panel);
            padding: 10px 20px;
            margin-bottom: 15px;
            border-radius: 4px;
        }

        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }

        .bottom-row {
            display: flex;
            gap: 15px;
            flex-grow: 1;
            min-height: 0;
        }

        .map-wrapper {
            flex: 2;
            border: 1px solid var(--accent);
            border-radius: 4px;
            position: relative;
            box-shadow: 0 0 10px var(--accent-dim);
        }

        #map { height: 100%; width: 100%; border-radius: 3px; }

        .side-panels {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        /* --- Components --- */
        h1, h2, h3 { margin: 0; font-weight: normal; }
        
        .logo {
            color: var(--accent);
            font-size: 1.5rem;
            margin-bottom: 40px;
            text-shadow: 0 0 8px var(--accent-dim);
        }

        .sidebar-menu { list-style: none; padding: 0; margin: 0; color: var(--text-dim); }
        .sidebar-menu li { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        
        .header-title { display: flex; align-items: center; gap: 15px; }
        .shield-icon { color: var(--accent); font-size: 1.5rem; border: 1px solid var(--accent); padding: 5px 10px; border-radius: 4px; }
        .subtitle { color: var(--text-dim); font-size: 0.8rem; letter-spacing: 1px; margin-top: 5px; }

        .btn {
            background: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
            padding: 8px 15px;
            font-family: inherit;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
            font-size: 0.8rem;
        }
        .btn:hover { background: var(--danger); color: #fff; box-shadow: 0 0 10px rgba(255, 51, 51, 0.4); }

        .card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 15px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .card-header { color: var(--text-dim); font-size: 0.8rem; display: flex; justify-content: space-between; margin-bottom: 15px; }
        .card-value { font-size: 2rem; color: #fff; }
        .card-sub { font-size: 0.7rem; color: var(--text-dim); }
        
        .progress-bar {
            height: 4px;
            background: var(--bg-panel-light);
            margin-top: 10px;
            width: 100%;
        }
        .progress-fill {
            height: 100%;
            background: var(--accent);
            width: 0%;
            box-shadow: 0 0 5px var(--accent);
            transition: width 0.5s ease;
        }

        .terminal {
            background: var(--bg-panel);
            border: 1px solid var(--accent);
            border-radius: 4px;
            padding: 15px;
            flex: 2;
            overflow-y: auto;
            font-size: 0.8rem;
            box-shadow: 0 0 10px var(--accent-dim) inset;
        }
        .log-entry { margin-bottom: 5px; }
        .log-time { color: var(--text-dim); }
        .log-msg { color: var(--accent); }
        .log-danger { color: var(--danger); font-weight: bold;}

        .integrity-card {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 4px;
        }
        .integrity-val { font-size: 3rem; color: var(--accent); text-shadow: 0 0 10px var(--accent-dim); }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="logo">● AEGIS.SYS</div>
        
        <div style="margin-bottom: 30px;">
            <div style="font-size: 0.7rem; color: var(--text-dim); margin-bottom: 10px;">DEVICE STATUS</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 5px;">
                <span>BATTERY</span> <span style="color: #00ff00;">100%</span>
            </div>
            <div class="progress-bar" style="margin-bottom: 15px;"><div class="progress-fill" style="width: 100%; background: #00ff00;"></div></div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 5px;">
                <span>UPLINK SIGNAL</span> <span id="signal-text">--%</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" id="signal-bar" style="width: 0%;"></div></div>
        </div>

        <ul class="sidebar-menu">
            <li>> DIAGNOSTICS</li>
            <li>> CONFIGURATION</li>
            <li style="color: var(--text-main);">> RESPONDER-01</li>
        </ul>
        
        <div style="margin-top: auto; font-size: 0.6rem; color: var(--text-dim);">
            V.2.0.4 - BETA<br>SECURE CONNECTION
        </div>
    </div>

    <div class="main-content">
        
        <div class="top-bar">
            <div class="header-title">
                <div class="shield-icon">🛡</div>
                <div>
                    <h2>EMERGENCY MONITOR <span style="color: var(--accent); font-size: 0.8rem;">V.2.0</span></h2>
                    <div class="subtitle">LIVE FEED // SUBJECT ID: AW-2049 // SECURE UPLINK</div>
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn" onclick="simulateAlert('FALL')">SIMULATE FALL</button>
                <button class="btn" onclick="simulateAlert('SCREAM')">SIMULATE SCREAM</button>
            </div>
        </div>

        <div class="stats-row">
            <div class="card" id="card-bpm">
                <div class="card-header"><span>HEART RATE</span> <span>♥</span></div>
                <div>
                    <span class="card-value" id="val-bpm">--</span> <span class="card-sub">BPM</span>
                    <div class="card-sub" id="sub-bpm" style="margin-top: 5px;">AWAITING DATA</div>
                </div>
                <div class="progress-bar"><div class="progress-fill" id="bar-bpm" style="width: 0%;"></div></div>
            </div>

            <div class="card" id="card-noise">
                <div class="card-header"><span>MIC SENSOR</span> <span>∿</span></div>
                <div>
                    <span class="card-value" id="val-noise">--</span>
                    <div class="card-sub" id="sub-noise" style="margin-top: 5px;">NORMAL RANGE</div>
                </div>
                <div class="progress-bar"><div class="progress-fill" id="bar-noise" style="width: 0%;"></div></div>
            </div>

            <div class="card">
                <div class="card-header"><span>LOCATION STATUS</span> <span>⌖</span></div>
                <div>
                    <span class="card-value" id="val-loc" style="font-size: 1.5rem;">TRACKING</span>
                    <div class="card-sub" style="margin-top: 5px;">GPS ACTIVE</div>
                </div>
                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
            </div>

            <div class="card" style="border-color: var(--accent); box-shadow: 0 0 10px var(--accent-dim) inset;">
                <div class="card-header"><span>SYSTEM STATUS</span> <span>⚡</span></div>
                <div style="margin-top: 10px;">
                    <span style="font-size: 1.5rem; color: var(--accent);" id="val-conn">CONNECTING...</span>
                    <div class="card-sub" id="val-time" style="margin-top: 5px;">DURATION: 0m 0s</div>
                </div>
            </div>
        </div>

        <div class="bottom-row">
            <div class="map-wrapper">
                <div id="map"></div>
                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 5px 10px; border: 1px solid var(--text-dim); z-index: 1000; font-size: 0.8rem; border-radius: 3px;">
                    ⌖ GPS: <span id="overlay-lat">--</span>, <span id="overlay-lng">--</span> | <span style="color: var(--text-dim);">SOURCE: NEO-6M</span>
                </div>
            </div>

            <div class="side-panels">
                <div class="terminal" id="terminal">
                    <div style="color: var(--accent); margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px;">SYSTEM TERMINAL_</div>
                    </div>

                <div class="integrity-card">
                    <div class="card-sub" style="margin-bottom: 10px;">SYSTEM INTEGRITY</div>
                    <div class="integrity-val" id="integrity-text">100%</div>
                    <div class="card-sub" style="margin-top: 10px;">ALL SYSTEMS NOMINAL</div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // 1. Initialize Map (Centered on Puducherry as per your image)
        var map = L.map('map', {zoomControl: false}).setView([11.9416, 79.8083], 13);
        
        // We use the standard Light map to match your screenshot perfectly
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        // Custom tech-styled map marker
        var marker = L.circleMarker([11.9416, 79.8083], {
            radius: 8, fillColor: "#00d2ff", color: "#000", weight: 2, opacity: 1, fillOpacity: 0.8
        }).addTo(map);

        // 2. Terminal Logging System
        function addLog(msg, isDanger = false) {
            const term = document.getElementById('terminal');
            const time = new Date().toLocaleTimeString('en-US', {hour12:false});
            const colorClass = isDanger ? 'log-danger' : 'log-msg';
            const html = `<div class="log-entry"><span class="log-time">[${time}] ></span> <span class="${colorClass}">${msg}</span></div>`;
            term.innerHTML += html;
            term.scrollTop = term.scrollHeight; // Auto-scroll to bottom
        }

        addLog("Booting AEGIS.SYS kernel...");
        addLog("Connecting to GSM Command Server...");

        // Track previous state to prevent spamming logs
        let lastState = { food: false, water: false, restroom: false, fall: false, sound: false, panic: false };
        let startTime = Date.now();

        // 3. Fetch Data from ESP32 / Flask
        setInterval(function() {
            fetch('/api/latest')
                .then(response => response.json())
                .then(data => {
                    if(data.error) return;
                    
                    document.getElementById('val-conn').innerText = "LINK ACTIVE";
                    document.getElementById('signal-text').innerText = "98%";
                    document.getElementById('signal-bar').style.width = "98%";
                    
                    // Update Timer
                    let diff = Math.floor((Date.now() - startTime) / 1000);
                    document.getElementById('val-time').innerText = `DURATION: ${Math.floor(diff/60)}m ${diff%60}s`;

                    // --- Heart Rate UI ---
                    document.getElementById('val-bpm').innerText = data.bpm;
                    document.getElementById('bar-bpm').style.width = Math.min(100, (data.bpm / 160) * 100) + "%";
                    if(data.panic) {
                        document.getElementById('sub-bpm').innerText = "ELEVATED HEART RATE!";
                        document.getElementById('sub-bpm').style.color = "var(--danger)";
                        document.getElementById('bar-bpm').style.background = "var(--danger)";
                        if(!lastState.panic) addLog("WARNING: Abnormal Heart Rate Detected (" + data.bpm + " BPM)", true);
                    } else {
                        document.getElementById('sub-bpm').innerText = "RESTING";
                        document.getElementById('sub-bpm').style.color = "var(--text-dim)";
                        document.getElementById('bar-bpm').style.background = "var(--accent)";
                    }

                    // --- Noise/Mic UI ---
                    if(data.sound) {
                        document.getElementById('val-noise').innerText = "LOUD";
                        document.getElementById('sub-noise').innerText = "CRYING/SCREAM DETECTED";
                        document.getElementById('sub-noise').style.color = "var(--danger)";
                        document.getElementById('bar-noise').style.width = "100%";
                        document.getElementById('bar-noise').style.background = "var(--danger)";
                        if(!lastState.sound) addLog("ALERT: High Noise Level / Crying Detected", true);
                    } else {
                        document.getElementById('val-noise').innerText = "QUIET";
                        document.getElementById('sub-noise').innerText = "NORMAL RANGE";
                        document.getElementById('sub-noise').style.color = "var(--text-dim)";
                        document.getElementById('bar-noise').style.width = "20%";
                        document.getElementById('bar-noise').style.background = "var(--accent)";
                    }

                    // --- Fall Detection & System Integrity ---
                    if(data.fall) {
                        document.getElementById('integrity-text').innerText = "CRITICAL";
                        document.getElementById('integrity-text').style.color = "var(--danger)";
                        if(!lastState.fall) addLog("CRITICAL: Fall Impact Detected via MPU-6050", true);
                    } else if (document.getElementById('integrity-text').innerText !== "CRITICAL") {
                        // Keep critical if it happened, or write a reset logic
                        document.getElementById('integrity-text').innerText = "100%";
                        document.getElementById('integrity-text').style.color = "var(--accent)";
                    }

                    // --- Needs (Buttons) logged to Terminal ---
                    if(data.food && !lastState.food) addLog("REQUEST: Subject pressed HUNGRY button.", true);
                    if(data.water && !lastState.water) addLog("REQUEST: Subject pressed THIRSTY button.", true);
                    if(data.restroom && !lastState.restroom) addLog("REQUEST: Subject pressed RESTROOM button.", true);

                    // --- Map & GPS ---
                    if(data.lat !== 0 && data.lng !== 0) {
                        let latlng = new L.LatLng(data.lat, data.lng);
                        marker.setLatLng(latlng);
                        map.setView(latlng, 15);
                        document.getElementById('overlay-lat').innerText = data.lat.toFixed(4);
                        document.getElementById('overlay-lng').innerText = data.lng.toFixed(4);
                        if(lastState.lat === 0) addLog("GPS Uplink Established. Receiving Telemetry.");
                    }

                    // Save state for next tick
                    lastState = data;
                })
                .catch(err => {
                    document.getElementById('val-conn').innerText = "NO SIGNAL";
                });
        }, 2000);

        // 4. Testing Simulation Buttons
        function simulateAlert(type) {
            addLog(`MANUAL OVERRIDE: Simulating ${type}...`, true);
            if(type === 'FALL') {
                document.getElementById('integrity-text').innerText = "CRITICAL";
                document.getElementById('integrity-text').style.color = "var(--danger)";
            }
            if(type === 'SCREAM') {
                document.getElementById('val-noise').innerText = "LOUD";
                document.getElementById('bar-noise').style.background = "var(--danger)";
                document.getElementById('bar-noise').style.width = "100%";
            }
            setTimeout(() => addLog("Simulation complete. Awaiting clear..."), 3000);
        }
    </script>
</body>
</html>
"""