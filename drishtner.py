import os
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from geopy.geocoders import Nominatim

app = Flask(__name__)
DB_FILE = "drishti_database.db"

# Global reference for live dashboard real-time alert intercepts
LATEST_CRITICAL_ALERT = None  

# Initialize OpenStreetMap Nominatim Geocoder Engine
geolocator = Nominatim(user_agent="drishti_ner_sih26001_monitor")

# =====================================================================
# 🧠 SEISMIC-AWARE RISK CALCULATION LAYER (Pure Python Math Architecture)
# =====================================================================
def predict_landslide_risk(r_int, r_cum, moist, slp, elev, pga, geo, cov, cut, prev, defo):
    """
    Physics-Constrained Multi-Spectral Weight Matrix. Bypasses external compiled 
    binary wheel dependencies to process 11 analytical variables natively.
    """
    score = 0.0
    
    # 1. Rainfall Threshold Weights
    if r_cum > 150.0 or r_int > 35.0: score += 2.5
    elif r_cum > 70.0 or r_int > 15.0: score += 1.2
    
    # 2. Moisture Saturation Vectors
    if moist > 80.0: score += 2.0
    elif moist > 50.0: score += 1.0
    
    # 3. Structural Slope Angles
    if slp > 35.0: score += 2.5
    elif slp > 20.0: score += 1.2
    
    # 4. Critical Seismic Peak Ground Forces (PGA)
    if pga >= 0.22: score += 3.5
    elif pga >= 0.10: score += 1.8
    
    # 5. Geotechnical Subsurface Formations (2: Shale, 1: Sedimentary)
    if geo == 2: score += 1.2
    elif geo == 1: score += 0.5
    
    # 6. Surface Cover / Deforestation Impact
    if cov == 2: score += 1.0
    
    # 7. Human Engineering Activity / Slope Modifications
    if cut == 1: score += 1.0
    
    # 8. Historical Strain Scar Records
    if prev == 1: score += 1.5
    
    # 9. InSAR Satellite Crustal Deformation Rate
    if defo > 20.0: score += 1.5

    # Target Decision Vector Boundaries
    if score >= 8.5:
        return "HIGH RISK"
    elif score >= 4.5:
        return "MODERATE RISK"
    else:
        return "LOW RISK"

# =====================================================================
# 🗄️ RESILIENT STORAGE LAYER (SQLite Schema Initialization)
# =====================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regional_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            rain_intensity REAL NOT NULL,
            rain_cumulative REAL NOT NULL,
            soil_moisture REAL NOT NULL,
            slope_angle REAL NOT NULL,
            elevation REAL NOT NULL,
            seismic_pga REAL NOT NULL,
            geo_type INTEGER NOT NULL,
            land_cover INTEGER NOT NULL,
            road_cutting INTEGER NOT NULL,
            prev_landslides INTEGER NOT NULL,
            satellite_deformation REAL NOT NULL,
            risk_level TEXT NOT NULL,
            network_status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# =====================================================================
# 📧 EMAIL ENGINE LAYER (Secure Google SMTP Gateway)
# =====================================================================
def dispatch_live_email_alert(location, risk_level, r_cum, slope):
    SENDER_EMAIL = "12az3zq@gmail.com"
    SENDER_PASSWORD = "jowbnnxzaeakwnyg"  
    BROADCAST_EMAIL =[ "mrabhineet18@gmail.com","manas81dash@gmail.com","aadityaaanand80@gmail.com","swayambhol7@gmail.com","omkarmahanti9@gmail.com"]
    success_count=0
    failure_count=0
    print(f"\n 🚨[MASS BROADCAST INITIATED] Routing alert grids to {len(BROADCAST_EMAIL)} nodes... ")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            for recipient in BROADCAST_EMAIL:
                try:
                     msg = MIMEText(
                            f"🚨 [DRISHTI-NER SYSTEM ALERT] 🚨\n\n"
                            f"Critical Landslide Danger computed at location node: {location}.\n"
                            f"AI Predictive Inference Classification: {risk_level}\n"
                            f"Telemetry Matrix Parameters: Cumulative Rain {r_cum}mm | Slope Angle {slope}°.\n\n"
                            f"Recommended Action: Evacuate the affected roads and move to designated safe zones immediately!"
                        )
                     msg['Subject'] = f"🚨 CRITICAL LANDSLIDE ALARM: {location}"
                     msg['From'] = SENDER_EMAIL
                     msg['To'] = recipient
                     server.sendmail(SENDER_EMAIL,[recipient],msg.as_string())
                     success_count+=1
                     print(f"\n📧 [EMAIL BROADCAST SUCCESS] Alert successfully sent out to: {recipient}")
                except Exception as individual_error:
                    print(f"[BROADCAST FAILED] Could not send to {recipient}:{individual_error}")
        
        return success_count==len(BROADCAST_EMAIL)
    except Exception as connection_error:
        print(f"\n❌ [EMAIL SMTP SERVER ERROR] Handshake failed: {connection_errorerror}")
        return False

# =====================================================================
# 🖥️ VISUAL CONTAINER LAYER (Tailwind CSS + Leaflet GIS + Chart.js Engine)
# =====================================================================
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project DRISHTI-NER AI Dashboard</title>
    <script src="https://tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans relative antialiased">

    <!-- Emergency Alert Modal Overlay -->
    <div id="emergency-modal" class="hidden fixed inset-0 bg-red-950/95 z-50 flex flex-col items-center justify-center text-center p-6 backdrop-blur-md animate-pulse border-[12px] border-red-600">
        <h1 class="text-5xl md:text-7xl font-black text-white tracking-widest mb-6">🚨 CRITICAL LANDSLIDE ALERT 🚨</h1>
        <div class="bg-slate-900/80 border border-red-500/40 rounded-2xl p-8 max-w-2xl shadow-2xl">
            <p class="text-3xl text-red-400 font-mono mb-3 font-bold">LOCATION: <span id="alert-modal-location" class="text-white">XYZ Village</span></p>
            <p class="text-2xl text-yellow-400 mb-6 font-semibold">RISK STATUS: HIGH INSTABILITY TRIGGERED</p>
            <p class="text-base text-slate-300">Action Matrix Order: Avoid all affected road cuttings and execute tactical evacuation protocols to safe geographical sectors immediately.</p>
        </div>
        <button onclick="dismissEmergencyAlert()" class="mt-10 px-8 py-3.5 bg-white text-red-950 font-bold rounded-xl hover:bg-slate-200 transition tracking-wider uppercase text-sm">
            Dismiss Dashboard Alarm
        </button>
    </div>

    <!-- Header Panel -->
    <header class="border-b border-slate-800 bg-slate-900/70 p-6 backdrop-blur flex flex-col md:flex-row justify-between items-start md:items-center gap-4 sticky top-0 z-40">
        <div>
            <div class="flex items-center gap-3">
                <span class="text-2xl">🛰️</span>
                <h1 class="text-2xl font-black tracking-wider bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">PROJECT DRISHTI-NER</h1>
            </div>
            <p class="text-xs text-slate-400 mt-1">Multi-Spectral Automated GIS Predictive Analytics Platform (SIH26001)</p>
        </div>
        <span class="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold">● HYBRID ANALYTIC RISK ACTIVE</span>
    </header>

    <div class="p-6 max-w-[1600px] mx-auto space-y-6">
        <!-- GIS Map -->
        <div class="bg-slate-900/50 rounded-2xl border border-slate-800 p-4 shadow-2xl backdrop-blur">
            <div id="gis-map" class="w-full h-[350px] rounded-xl bg-slate-950 border border-slate-800 relative z-10"></div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            <!-- Left Controls Column -->
            <div class="space-y-6">
                <!-- Telemetry Intake Form -->
                <div class="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur">
                    <div class="flex items-center gap-2 mb-4">
                        <span class="text-emerald-400 text-lg">📥</span>
                        <h2 class="text-base font-bold tracking-tight text-slate-200">Sensor Telemetry Intake</h2>
                    </div>
                    <form action="/add_log" method="POST" class="space-y-3.5 text-xs">
                        <div>
                            <label class="block text-slate-400 mb-1 font-medium">Regional Location / Sector Context</label>
                            <input type="text" name="location" placeholder="e.g., Tawang Mountain Ridge, India" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 font-medium text-sm">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Rain Intensity (mm/hr)</label>
                                <input type="number" step="any" name="rain_intensity" placeholder="40" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500 font-mono">
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Cumulative Rain (mm)</label>
                                <input type="number" step="any" name="rain_cumulative" placeholder="185" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500 font-mono">
                            </div>
                        </div>
                        <div class="grid grid-cols-3 gap-2">
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Moisture (%)</label>
                                <input type="number" step="any" name="soil_moisture" placeholder="85" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500 font-mono">
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Slope Angle (°)</label>
                                <input type="number" step="any" name="slope_angle" placeholder="38" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500 font-mono">
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Elevation (m)</label>
                                <input type="number" step="any" name="elevation" placeholder="2400" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500 font-mono">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-red-400 mb-1 font-medium">Seismic Force (PGA g)</label>
                                <input type="number" step="any" name="seismic_pga" placeholder="0.28" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-red-500 font-mono">
                            </div>
                            <div>
                                <label class="block text-purple-400 mb-1 font-medium">Sat Defo (mm/yr)</label>
                                <input type="number" step="any" name="satellite_deformation" placeholder="24.5" required class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-purple-500 font-mono">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Geology Formation</label>
                                <select name="geo_type" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500">
                                    <option value="2">Loose Fractured Shale</option>
                                    <option value="1">Mixed Sedimentary</option>
                                    <option value="0">Stable Bedrock</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Surface Coverage</label>
                                <select name="land_cover" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500">
                                    <option value="2">Barren Soil / Deforested</option>
                                    <option value="1">Sparse Vegetation</option>
                                    <option value="0">Dense Canopy Cover</option>
                                </select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Road Slope Cutting</label>
                                <select name="road_cutting" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500">
                                    <option value="1">Yes (Steep Escarpment)</option>
                                    <option value="0">No Cut Modification</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-slate-400 mb-1 font-medium">Historical Failure</label>
                                <select name="prev_landslides" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-white focus:outline-none focus:border-emerald-500">
                                    <option value="1">Active Landslide Scar</option>
                                    <option value="0">No Recorded Slide</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-amber-400 mb-1 font-medium">Emergency Comms Pipeline</label>
                            <select name="network" class="w-full bg-slate-950 border border-amber-900/50 rounded-xl p-2 text-amber-400 focus:outline-none">
                                <option value="ONLINE">Active Online Channel (Send SMTP Emergency Email)</option>
                                <option value="OFFLINE">Offline Local Cache Mode (Local Edge Cache)</option>
                            </select>
                        </div>
                        <button type="submit" class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 font-bold py-3 rounded-xl text-white transition shadow-lg uppercase tracking-wider text-xs">
                            Transmit Telemetry Packet
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Side Dashboard Column -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Graphical Analytics Chart -->
                <div class="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur">
                    <h2 class="text-base font-bold text-slate-200 mb-4">📊 Telemetry Metric Scaling Graph</h2>
                    <div class="w-full h-[160px] relative"><canvas id="metricsChart"></canvas></div>
                </div>

                <!-- Structured Logs Matrix Table -->
                <div class="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur overflow-x-auto custom-scrollbar">
                    <table class="w-full text-left border-collapse min-w-[720px] text-xs">
                        <thead>
                            <tr class="border-b border-slate-800 uppercase text-slate-400 bg-slate-950/60 font-mono">
                                <th class="p-3">Timestamp</th>
                                <th class="p-3">Coordinate Center</th>
                                <th class="p-3 text-center">Multi-Spectral Parameters (R | M | S | PGA | Sat)</th>
                                <th class="p-3 text-center">Comms</th>
                                <th class="p-3 text-right">Risk Grade Output</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800/50">
                            {% for log in logs %}
                            <tr class="hover:bg-slate-900/40 transition-colors">
                                <td class="p-3 font-mono text-slate-400">{{ log[17] }}</td>
                                <td class="p-3">
                                    <div class="text-slate-200 font-bold text-sm">{{ log[1] }}</div>
                                    <div class="text-[10px] text-slate-500 font-mono mt-0.5">Lat: {{ log[2] }} | Lng: {{ log[3] }}</div>
                                </td>
                                <td class="p-3 text-center font-mono text-slate-300">
                                    <span class="text-blue-400 font-bold">{{ log[5] }}mm</span> | 
                                    <span class="text-teal-400 font-bold">{{ log[6] }}%</span> | 
                                    <span class="text-amber-400 font-bold">{{ log[7] }}°</span> |
                                    <span class="text-red-400 font-bold">{{ log[9] }}g</span> |
                                    <span class="text-purple-400 font-bold">{{ log[14] }}mm/y</span>
                                </td>
                                <td class="p-3 text-center">
                                    {% if log[16] == 'ONLINE' %}
                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">ONLINE</span>
                                    {% else %}
                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold">OFFLINE</span>
                                    {% endif %}
                                </td>
                                <td class="p-3 text-right">
                                    {% if log[15] == 'HIGH RISK' %}
                                    <span class="px-3 py-1 rounded-xl text-[11px] font-black bg-red-600 text-white animate-pulse">HIGH RISK</span>
                                    {% elif log[15] == 'MODERATE RISK' %}
                                    <span class="px-3 py-1 rounded-xl text-[11px] font-black bg-amber-600 text-white">MODERATE RISK</span>
                                    {% else %}
                                    <span class="px-3 py-1 rounded-xl text-[11px] font-black bg-emerald-600 text-white">LOW RISK</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Mapping and Graph Interaction Scripts -->
    <script>
        var map = L.map('gis-map').setView([26.1445, 91.7362], 6);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(map);

        var threatColors = { 'HIGH RISK': '#ef4444', 'MODERATE RISK': '#d97706', 'LOW RISK': '#16a34a' };

        {% for log in logs %}
            var lat = parseFloat("{{ log[2] }}"); var lng = parseFloat("{{ log[3] }}");
            var locName = "{{ log[1] }}"; var riskTier = "{{ log[15] }}";
            var c_rain = "{{ log[5] }}"; var pga_val = "{{ log[9] }}";

            if (!isNaN(lat) && !isNaN(lng)) {
                L.circleMarker([lat, lng], { radius: 10, fillColor: threatColors[riskTier], color: '#ffffff', weight: 2, fillOpacity: 0.85 })
                .addTo(map).bindPopup(`<div class="text-slate-900 font-sans p-1 text-xs"><strong>\${locName}</strong><br><b>Risk:</b> \${riskTier}<br><b>Rain:</b> \${c_rain} mm</div>`);
            }
        {% endfor %}

        var chartLabels = []; var rainData = []; var moistureData = []; var slopeData = []; var pgaData = [];
        var count = 0;
        {% for log in logs %}
            if (count < 5) {
                chartLabels.unshift("{{ log[1][:10] }}...");
                rainData.unshift(parseFloat("{{ log[5] }}"));
                moistureData.unshift(parseFloat("{{ log[6] }}"));
                slopeData.unshift(parseFloat("{{ log[7] }}"));
                pgaData.unshift(parseFloat("{{ log[9] }}") * 100); 
                count++;
            }
        {% endfor %}

        var ctx = document.getElementById('metricsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartLabels,
                datasets: [
                    { label: 'Rain (mm)', data: rainData, backgroundColor: '#3b82f6' },
                    { label: 'Moisture (%)', data: moistureData, backgroundColor: '#14b8a6' },
                    { label: 'Slope (°)', data: slopeData, backgroundColor: '#f59e0b' },
                    { label: 'Seismic (g x100)', data: pgaData, backgroundColor: '#ef4444' }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#e2e8f0', font: { size: 9 } } } } }
        });

        // Audio Siren Engine
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var alertInterval = null;
        function playDashboardSirenTone() {
            if (audioCtx.state === 'suspended') { audioCtx.resume(); }
            var osc = audioCtx.createOscillator(); var gain = audioCtx.createGain();
            osc.type = 'sawtooth'; osc.frequency.setValueAtTime(880, audioCtx.currentTime);
            osc.frequency.linearRampToValueAtTime(440, audioCtx.currentTime + 0.4);
            gain.gain.setValueAtTime(0.15, audioCtx.currentTime); gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
            osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime + 0.4);
        }

        setInterval(function() {
            fetch('/check_alerts').then(res => res.json()).then(data => {
                if (data.alert_active) {
                    document.getElementById('alert-modal-location').innerText = data.location;
                    document.getElementById('emergency-modal').classList.remove('hidden');
                    if(!alertInterval) { alertInterval = setInterval(playDashboardSirenTone, 500); }
                }
            });
        }, 3000);

        function dismissEmergencyAlert() {
            document.getElementById('emergency-modal').classList.add('hidden');
            if(alertInterval) { clearInterval(alertInterval); alertInterval = null; }
            fetch('/clear_alert', { method: 'POST' });
        }
    </script>
</body>
</html>
"""

# =====================================================================
# 🎮 CONTROLLER ROUTING HANDLERS (Flask Backend Infrastructure)
# =====================================================================
@app.route("/", methods=["GET"])
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regional_logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_UI, logs=logs)

@app.route("/add_log", methods=["POST"])
def add_log():
    global LATEST_CRITICAL_ALERT
    location = request.form.get("location")
    
    # Automated Geolocation Engine Lookup
    try:
        print(f"📡 Resolving coordinates for: {location}...")
        geo_payload = geolocator.geocode(location, timeout=6)
        if geo_payload:
            latitude = geo_payload.latitude
            longitude = geo_payload.longitude
            print(f"✅ Resolved point: {latitude}, {longitude}")
        else:
            latitude, longitude = 26.1445, 91.7362
            print("⚠️ Location lookup failed. Applying default fallback coordinates.")
    except Exception as geocode_error:
        latitude, longitude = 26.1445, 91.7362
        print(f"❌ Geocoding API timeout: {geocode_error}. Applying default fallback.")

    r_int = float(request.form.get("rain_intensity"))
    r_cum = float(request.form.get("rain_cumulative"))
    moist = float(request.form.get("soil_moisture"))
    slp = float(request.form.get("slope_angle"))
    elev = float(request.form.get("elevation"))
    pga = float(request.form.get("seismic_pga"))
    geo = int(request.form.get("geo_type"))
    cov = int(request.form.get("land_cover"))
    cut = int(request.form.get("road_cutting"))
    prev = int(request.form.get("prev_landslides"))
    defo = float(request.form.get("satellite_deformation"))
    network_status = request.form.get("network")
    
    # Compute hybrid risk evaluation matrix payload
    risk_level = predict_landslide_risk(r_int, r_cum, moist, slp, elev, pga, geo, cov, cut, prev, defo)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Persist log payload row to local cache storage
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO regional_logs (location, latitude, longitude, rain_intensity, rain_cumulative, soil_moisture, slope_angle, elevation, seismic_pga, geo_type, land_cover, road_cutting, prev_landslides, satellite_deformation, risk_level, network_status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (location, latitude, longitude, r_int, r_cum, moist, slp, elev, pga, geo, cov, cut, prev, defo, risk_level, network_status, timestamp))
    conn.commit()
    conn.close()

    # Trigger emergency warning channels
    if risk_level == "HIGH RISK":
        LATEST_CRITICAL_ALERT = {"location": location}
        if network_status == "ONLINE":
            dispatch_live_email_alert(location, risk_level, r_cum, slp)
            
    return redirect(url_for('index'))

@app.route("/check_alerts", methods=["GET"])
def check_alerts():
    if LATEST_CRITICAL_ALERT:
        return jsonify({"alert_active": True, "location": LATEST_CRITICAL_ALERT["location"]})
    return jsonify({"alert_active": False})

@app.route("/clear_alert", methods=["POST"])
def clear_alert():
    global LATEST_CRITICAL_ALERT
    LATEST_CRITICAL_ALERT = None
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
