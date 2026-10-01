from flask import Flask, jsonify, request, render_template_string
import time
import math

app = Flask(__name__)

# ==============================================================================
# IN-MEMORY DATABASE & INITIAL DEMO DATA
# ==============================================================================
dump_sites = [
    {
        "id": 1,
        "lat": -1.0388,
        "lng": 37.0833,
        "volume": "Large",
        "wasteType": "organic",
        "desc": "Market organic waste buildup causing high odor and methane hazard.",
        "risk": "CRITICAL DISASTER HAZARD",
        "grantAmount": 500,
        "status": "Needs Funding",
        "methaneKgDay": 245.5,
        "placeName": "Thika Central Market, Kenya"
    },
    {
        "id": 2,
        "lat": -1.0450,
        "lng": 37.0720,
        "volume": "Medium",
        "wasteType": "mixed",
        "desc": "Riverbank informal dumping site threatening water catchment area.",
        "risk": "ELEVATED RISK",
        "grantAmount": 300,
        "status": "Grant Assigned",
        "methaneKgDay": 98.2,
        "placeName": "Chania Riverbed, Kenya"
    }
]

# ==============================================================================
# AI RISK & METHANE EMISSION ESTIMATOR ENGINE
# ==============================================================================
def calculate_ai_methane_risk(volume_str, waste_type, temperature_c=28.0):
    """
    Simulates a biochemical decay algorithm estimating methane emissions (kg CH4/day)
    and calculating disaster hazard threat levels.
    """
    volume_mapping = {"Small": 0.5, "Medium": 3.0, "Large": 8.0}
    volume_tons = volume_mapping.get(volume_str, 1.0)
    
    emission_factors = {
        "organic": 0.25,
        "industrial": 0.15,
        "mixed": 0.18,
        "plastic": 0.02
    }
    factor = emission_factors.get(waste_type, 0.15)
    
    # Methane output formula adjusting for temperature-accelerated decay
    methane_kg_day = (volume_tons * 1000) * factor * (1 + (temperature_c - 20) * 0.03)
    
    if methane_kg_day > 150:
        risk_level = "CRITICAL DISASTER HAZARD"
        grant_amount = 500
    elif methane_kg_day > 50:
        risk_level = "ELEVATED RISK"
        grant_amount = 300
    else:
        risk_level = "LOW IMPACT"
        grant_amount = 150
        
    return round(methane_kg_day, 1), risk_level, grant_amount

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================
@app.route("/api/sites", methods=["GET"])
def get_sites():
    return jsonify(dump_sites)

@app.route("/api/report", methods=["POST"])
def add_report():
    data = request.json or {}
    lat = float(data.get("lat", -1.0388))
    lng = float(data.get("lng", 37.0833))
    volume = data.get("volume", "Small")
    waste_type = data.get("wasteType", "organic")
    desc = data.get("desc", "Unspecified site report")
    place_name = data.get("placeName", f"Coordinates: {lat}, {lng}")
    
    methane_kg, risk_level, grant_amt = calculate_ai_methane_risk(volume, waste_type)
    
    new_site = {
        "id": int(time.time()),
        "lat": lat,
        "lng": lng,
        "volume": volume,
        "wasteType": waste_type,
        "desc": desc,
        "risk": risk_level,
        "grantAmount": grant_amt,
        "status": "Needs Funding",
        "methaneKgDay": methane_kg,
        "placeName": place_name
    }
    dump_sites.append(new_site)
    return jsonify({"status": "success", "site": new_site}), 201

@app.route("/api/claim-grant", methods=["POST"])
def claim_grant():
    data = request.json or {}
    site_id = data.get("siteId")
    for site in dump_sites:
        if site["id"] == site_id:
            site["status"] = "Grant Assigned"
            return jsonify({"status": "success", "message": "Grant successfully claimed!"})
    return jsonify({"status": "error", "message": "Site not found"}), 404

# ==============================================================================
# HTML / JAVASCRIPT FRONTEND TEMPLATE
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EcoTrace AI — Global Satellite Methane & Disaster Tracker</title>
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    #map { height: 480px; width: 100%; border-radius: 1rem; }
    .nav-btn.active { background-color: #059669; color: #ffffff; }
    
    @keyframes orbit {
      0% { transform: rotate(0deg) translateX(12px) rotate(0deg); }
      100% { transform: rotate(360deg) translateX(12px) rotate(-360deg); }
    }
    .satellite-orbit {
      animation: orbit 4s linear infinite;
      transform-origin: 16px 16px;
    }

    @keyframes pulse-ring {
      0% { transform: scale(0.6); opacity: 1; }
      100% { transform: scale(1.8); opacity: 0; }
    }
    .disaster-marker-critical {
      position: relative;
      width: 18px;
      height: 18px;
      background-color: #ef4444;
      border: 2px solid #ffffff;
      border-radius: 50%;
      box-shadow: 0 0 12px #ef4444;
    }
    .disaster-marker-critical::after {
      content: '';
      position: absolute;
      top: -7px;
      left: -7px;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      border: 2px solid #ef4444;
      animation: pulse-ring 1.5s infinite ease-out;
    }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen pb-12">

  <header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
      <div class="flex items-center space-x-3">
        <div class="bg-emerald-950 border border-emerald-500/30 p-2 rounded-xl text-emerald-400 flex items-center justify-center">
          <svg class="w-8 h-8 text-emerald-400 overflow-visible" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M6 16C6 16 10 12 16 12C22 12 26 16 26 16" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
            <ellipse cx="16" cy="16" rx="14" ry="5" stroke="rgba(16, 185, 129, 0.4)" stroke-width="1" transform="rotate(-25 16 16)"/>
            <g class="satellite-orbit">
              <circle cx="16" cy="4" r="2.5" fill="#10B981"/>
            </g>
          </svg>
        </div>
        <div>
          <span class="text-xl font-bold tracking-tight text-white block leading-none">EcoTrace AI</span>
          <span class="text-[10px] text-emerald-400 font-medium tracking-wide">SATELLITE METHANE & HAZARD TRACKER</span>
        </div>
      </div>
      <span class="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-3 py-1 rounded-full font-medium flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Satellite Online
      </span>
    </div>
  </header>

  <main class="max-w-6xl mx-auto px-4 mt-6">

    <!-- Navigation Tabs -->
    <div class="flex bg-slate-800 p-1 rounded-xl border border-slate-700 mb-6 max-w-lg mx-auto">
      <button onclick="switchTab('report')" id="tab-report" class="nav-btn active flex-1 py-2 text-xs md:text-sm font-semibold rounded-lg transition-all flex justify-center items-center gap-1.5">
        <i data-lucide="camera" class="w-4 h-4"></i> Report
      </button>
      <button onclick="switchTab('mapTab')" id="tab-mapTab" class="nav-btn flex-1 py-2 text-xs md:text-sm font-semibold rounded-lg transition-all flex justify-center items-center gap-1.5 text-slate-400">
        <i data-lucide="map" class="w-4 h-4"></i> Live Map
      </button>
      <button onclick="switchTab('grants')" id="tab-grants" class="nav-btn flex-1 py-2 text-xs md:text-sm font-semibold rounded-lg transition-all flex justify-center items-center gap-1.5 text-slate-400">
        <i data-lucide="coins" class="w-4 h-4"></i> Grants
      </button>
      <button onclick="switchTab('analytics')" id="tab-analytics" class="nav-btn flex-1 py-2 text-xs md:text-sm font-semibold rounded-lg transition-all flex justify-center items-center gap-1.5 text-slate-400">
        <i data-lucide="bar-chart-3" class="w-4 h-4"></i> Analytics
      </button>
    </div>

    <!-- TAB 1: REPORT FORM -->
    <section id="view-report" class="space-y-6">
      <div class="bg-slate-800 p-6 rounded-2xl border border-slate-700 max-w-xl mx-auto shadow-xl">
        <h2 class="text-xl font-bold mb-1 text-white">Log Environmental Hotspot</h2>
        <p class="text-slate-400 text-sm mb-6">Capture coordinates to run AI methane decay analysis & deploy satellite tracking.</p>

        <form id="dumpForm" onsubmit="handleFormSubmit(event)" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1">GPS Coordinates (Lat, Lng)</label>
            <div class="flex gap-2">
              <input type="text" id="geoInput" placeholder="-1.0388, 37.0833" required class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500" />
              <button type="button" onclick="detectGPS()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-1">
                <i data-lucide="crosshair" class="w-4 h-4"></i> Auto GPS
              </button>
            </div>
            <p id="locationNameLabel" class="text-xs text-emerald-400 mt-1 italic"></p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1">Waste Volume</label>
              <select id="volumeInput" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500">
                <option value="Small">Small (&lt; 1 Ton)</option>
                <option value="Medium">Medium (1–5 Tons)</option>
                <option value="Large">Large (&gt; 5 Tons)</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1">Waste Composition</label>
              <select id="typeInput" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500">
                <option value="organic">Organic Food Waste</option>
                <option value="mixed">Mixed Solid Waste</option>
                <option value="industrial">Industrial Residue</option>
                <option value="plastic">Plastics & Non-Organic</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-1">Observations / Notes</label>
            <textarea id="descInput" rows="3" placeholder="Describe environmental factors or risk details..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500" required></textarea>
          </div>

          <button type="submit" id="submitBtn" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 rounded-xl transition shadow-lg flex justify-center items-center gap-2">
            <i data-lucide="send" class="w-4 h-4"></i> Run AI Analysis & Pin Hotspot
          </button>
        </form>
      </div>
    </section>

    <!-- TAB 2: LIVE SATELLITE MAP -->
    <section id="view-mapTab" class="hidden space-y-4">
      <div class="bg-slate-800 p-4 rounded-2xl border border-slate-700">
        <div id="map"></div>
        <div class="mt-3 flex justify-between items-center text-xs text-slate-400 px-1">
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-rose-500 inline-block"></span> High Methane Threat</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-cyan-500 inline-block"></span> ESA Sentinel-5P Methane Layer Active</span>
        </div>
      </div>
    </section>

    <!-- TAB 3: MICRO-GRANTS TERMINAL -->
    <section id="view-grants" class="hidden space-y-6">
      <div id="grantList" class="grid md:grid-cols-2 gap-4"></div>
    </section>

    <!-- TAB 4: ANALYTICS DASHBOARD -->
    <section id="view-analytics" class="hidden space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
          <p class="text-xs text-slate-400 font-medium">Total Hotspots Logged</p>
          <h3 id="stat-total" class="text-2xl font-bold text-white mt-1">0</h3>
        </div>
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
          <p class="text-xs text-slate-400 font-medium">Allocated Micro-Grants</p>
          <h3 id="stat-funds" class="text-2xl font-bold text-emerald-400 mt-1">$0</h3>
        </div>
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
          <p class="text-xs text-slate-400 font-medium">Critical Disaster Risks</p>
          <h3 id="stat-highrisk" class="text-2xl font-bold text-rose-400 mt-1">0</h3>
        </div>
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
          <p class="text-xs text-slate-400 font-medium">Est. Daily CH4 Methane</p>
          <h3 id="stat-methane" class="text-2xl font-bold text-cyan-400 mt-1">0 kg/day</h3>
        </div>
      </div>
    </section>

  </main>

  <script>
    let dumpSites = [];
    let map, mapInitialized = false;
    let mapMarkers = [];
    let detectedAddress = "";

    lucide.createIcons();
    window.addEventListener('load', fetchSites);

    function fetchSites() {
      fetch('/api/sites')
        .then(res => res.json())
        .then(data => {
          dumpSites = data;
          renderAnalytics();
          if (mapInitialized) updateMapMarkers();
        });
    }

    function switchTab(tabName) {
      ['report', 'mapTab', 'grants', 'analytics'].forEach(t => {
        document.getElementById(`view-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).classList.remove('active');
        document.getElementById(`tab-${t}`).classList.add('text-slate-400');
      });

      document.getElementById(`view-${tabName}`).classList.remove('hidden');
      document.getElementById(`tab-${tabName}`).classList.add('active');
      document.getElementById(`tab-${tabName}`).classList.remove('text-slate-400');

      if (tabName === 'mapTab') setTimeout(initMap, 100);
      if (tabName === 'grants') renderGrants();
      if (tabName === 'analytics') renderAnalytics();
    }

    function detectGPS() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          pos => {
            const lat = pos.coords.latitude.toFixed(4);
            const lng = pos.coords.longitude.toFixed(4);
            document.getElementById('geoInput').value = `${lat}, ${lng}`;

            // Reverse Geocoding
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
              .then(res => res.json())
              .then(data => {
                detectedAddress = data.display_name || "";
                document.getElementById('locationNameLabel').innerText = `📍 ${detectedAddress}`;
              })
              .catch(() => {
                detectedAddress = `Location (${lat}, ${lng})`;
              });
          },
          err => alert("Unable to access high-precision GPS.")
        );
      }
    }

    function handleFormSubmit(e) {
      e.preventDefault();
      const coords = document.getElementById('geoInput').value.split(',');
      const payload = {
        lat: parseFloat(coords[0]),
        lng: parseFloat(coords[1]),
        volume: document.getElementById('volumeInput').value,
        wasteType: document.getElementById('typeInput').value,
        desc: document.getElementById('descInput').value,
        placeName: detectedAddress || `Coordinates: ${coords[0]}, ${coords[1]}`
      };

      fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(res => {
        alert("Report logged and analyzed by AI!");
        document.getElementById('dumpForm').reset();
        document.getElementById('locationNameLabel').innerText = "";
        fetchSites();
        switchTab('mapTab');
        if (map) map.setView([payload.lat, payload.lng], 15);
      });
    }

    function initMap() {
      if (!mapInitialized) {
        map = L.map('map').setView([-1.0388, 37.0833], 13);

        // 1. High Resolution Satellite Imagery
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          attribution: 'Tiles &copy; Esri World Imagery'
        }).addTo(map);

        // 2. ESA Sentinel-5P Methane Layer Overlay
        L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/S5P_TROPOMI_Level3_CH4_Column_Volume_Mixing_Ratio_Dry_Air/default/default/250m/{z}/{y}/{x}.png', {
          opacity: 0.55,
          attribution: 'NASA GIBS / ESA Sentinel-5P TROPOMI'
        }).addTo(map);

        mapInitialized = true;
      }
      updateMapMarkers();
    }

    function updateMapMarkers() {
      if (!map) return;
      mapMarkers.forEach(m => map.removeLayer(m));
      mapMarkers = [];

      dumpSites.forEach(site => {
        const pulseIcon = L.divIcon({
          className: 'custom-pulse',
          html: `<div class="disaster-marker-critical"></div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });

        const marker = L.marker([site.lat, site.lng], { icon: pulseIcon }).addTo(map)
          .bindPopup(`
            <div style="color: #0f172a; padding: 2px;">
              <span style="font-size: 10px; font-weight: bold; background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px;">${site.risk}</span>
              <h4 style="font-weight: bold; font-size: 13px; margin-top: 6px;">${site.placeName}</h4>
              <p style="font-size: 11px; margin-top: 4px; color: #475569;">${site.desc}</p>
              <hr style="margin: 6px 0;">
              <p style="font-size: 11px; color: #0891b2;"><b>AI Methane Emission:</b> ${site.methaneKgDay} kg/day</p>
            </div>
          `);
        mapMarkers.push(marker);
      });
    }

    function renderGrants() {
      const container = document.getElementById('grantList');
      container.innerHTML = '';
      dumpSites.forEach(site => {
        container.innerHTML += `
          <div class="bg-slate-800 p-5 rounded-xl border border-slate-700">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-bold text-white">${site.placeName}</span>
              <span class="text-xs bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-semibold">$${site.grantAmount} Grant</span>
            </div>
            <p class="text-xs text-slate-400 mb-2">${site.desc}</p>
            <p class="text-xs text-cyan-400 font-mono mb-4">Methane Rate: ${site.methaneKgDay} kg CH4/day</p>
            <button onclick="claimGrant(${site.id})" ${site.status === 'Grant Assigned' ? 'disabled' : ''} class="w-full py-2.5 ${site.status === 'Grant Assigned' ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-500 text-white'} rounded-lg text-sm font-semibold transition">
              ${site.status === 'Grant Assigned' ? 'Grant Disbursed' : 'Claim Micro-Grant'}
            </button>
          </div>
        `;
      });
    }

    function claimGrant(siteId) {
      fetch('/api/claim-grant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ siteId: siteId })
      })
      .then(res => res.json())
      .then(() => {
        alert("Grant released to cleanup team!");
        fetchSites();
        renderGrants();
      });
    }

    function renderAnalytics() {
      const total = dumpSites.length;
      let totalFunds = 0;
      let highRisk = 0;
      let totalMethane = 0;

      dumpSites.forEach(s => {
        totalFunds += (s.grantAmount || 0);
        totalMethane += (s.methaneKgDay || 0);
        if (s.risk.includes('CRITICAL')) highRisk++;
      });

      document.getElementById('stat-total').innerText = total;
      document.getElementById('stat-funds').innerText = `$${totalFunds}`;
      document.getElementById('stat-highrisk').innerText = highRisk;
      document.getElementById('stat-methane').innerText = `${totalMethane.toFixed(1)} kg/day`;
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
