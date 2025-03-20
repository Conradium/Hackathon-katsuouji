# app.py - Fully simulated AR navigation app
from flask import Flask, render_template, jsonify, request
import json
import os
import math
import random

app = Flask(__name__)

# Sample navigation points near a simulated user position
# Format: [longitude, latitude, title, description]
BASE_LAT = 37.7749  # San Francisco latitude
BASE_LNG = -122.4194  # San Francisco longitude

# Generate points in a circle around the base location
SAMPLE_NAV_POINTS = []
for i in range(10):
    # Random distance between 50-500 meters
    distance = random.uniform(50, 500)
    # Random bearing in degrees
    bearing = random.uniform(0, 360)
    
    # Convert distance and bearing to lat/lng offset
    # Rough approximation (not accounting for Earth's curvature for short distances)
    lat_offset = distance * math.cos(math.radians(bearing)) / 111000  # 1 degree ~ 111km
    lng_offset = distance * math.sin(math.radians(bearing)) / (111000 * math.cos(math.radians(BASE_LAT)))
    
    point_lat = BASE_LAT + lat_offset
    point_lng = BASE_LNG + lng_offset
    
    SAMPLE_NAV_POINTS.append([
        point_lng, 
        point_lat, 
        f"Point {chr(65+i)}", 
        f"Location {i+1} - {int(distance)}m from center"
    ])

@app.route('/')
def index():
    """Serve the main AR application page"""
    return render_template('index.html')

@app.route('/navigation-points')
def get_navigation_points():
    """Return all navigation points"""
    points = []
    for lng, lat, title, description in SAMPLE_NAV_POINTS:
        points.append({
            "id": len(points) + 1,
            "latitude": lat,
            "longitude": lng,
            "title": title,
            "description": description
        })
    
    return jsonify(points)

# Create required directories if they don't exist
if not os.path.exists('templates'):
    os.makedirs('templates')
if not os.path.exists('static'):
    os.makedirs('static')

# Create HTML template
with open('templates/index.html', 'w', encoding='utf-8') as f: # Added encoding='utf-8'
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>AR Navigation Simulator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div id="app">
        <div id="simulator-view">
            <div id="compass-container">
                <div id="compass">
                    <div id="compass-north">N</div>
                    <div id="compass-east">E</div>
                    <div id="compass-south">S</div>
                    <div id="compass-west">W</div>
                    <div id="compass-needle"></div>
                </div>
            </div>
            <div id="ar-overlay"></div>
            <div id="control-panel">
                <button id="rotate-left" class="control-button">⟲ Left</button>
                <button id="move-forward" class="control-button">↑ Move</button>
                <button id="rotate-right" class="control-button">⟳ Right</button>
            </div>
        </div>
        <div id="map-container">
            <div id="map">
                <div id="user-marker"></div>
                <!-- Point markers will be added here -->
            </div>
        </div>
        <div id="info-panel">
            <h2>AR Navigation Simulator</h2>
            <div id="status">Use buttons or arrow keys to move</div>
            <div id="coordinates">Position: 37.7749, -122.4194 (simulated)</div>
            <div id="heading">Heading: 0° (North)</div>
            <div id="nearby-points"></div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>
""")

# Create CSS file
with open('static/style.css', 'w', encoding='utf-8') as f:  # Added encoding='utf-8'
    f.write("""
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    overflow: hidden;
}

#app {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

#simulator-view {
    position: relative;
    width: 100%;
    height: 60vh;
    overflow: hidden;
    background-color: #444;
    background-image: linear-gradient(#333 0%, #666 100%);
}

#compass-container {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 100px;
    height: 100px;
    z-index: 5;
}

#compass {
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.4);
}

#compass-north, #compass-east, #compass-south, #compass-west {
    position: absolute;
    color: white;
    font-weight: bold;
    text-align: center;
}

#compass-north {
    top: 5px;
    left: 50%;
    transform: translateX(-50%);
}

#compass-east {
    right: 5px;
    top: 50%;
    transform: translateY(-50%);
}

#compass-south {
    bottom: 5px;
    left: 50%;
    transform: translateX(-50%);
}

#compass-west {
    left: 5px;
    top: 50%;
    transform: translateY(-50%);
}

#compass-needle {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 4px;
    height: 40px;
    background-color: red;
    transform-origin: bottom center;
    transform: translate(-50%, -100%) rotate(0deg);
}

#ar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    pointer-events: none;
}

.ar-marker {
    position: absolute;
    background-color: rgba(255, 0, 0, 0.5);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: bold;
    transform: translate(-50%, -50%);
    pointer-events: all;
    cursor: pointer;
    transition: all 0.3s ease;
}

.ar-marker:hover {
    background-color: rgba(255, 0, 0, 0.8);
    transform: translate(-50%, -50%) scale(1.1);
}

#control-panel {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    z-index: 5;
}

.control-button {
    padding: 10px 15px;
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.control-button:hover {
    background-color: rgba(0, 0, 0, 0.8);
}

#map-container {
    width: 100%;
    height: 25vh;
    background-color: #eee;
    position: relative;
    overflow: hidden;
}

#map {
    width: 100%;
    height: 100%;
    position: relative;
}

#user-marker {
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: blue;
    border-radius: 50%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
}

#user-marker:after {
    content: '';
    position: absolute;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 15px solid blue;
    top: -12px;
    left: 50%;
    transform: translateX(-50%) rotate(0deg);
    transform-origin: bottom center;
}

.map-point {
    position: absolute;
    width: 12px;
    height: 12px;
    background-color: red;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    z-index: 5;
}

#info-panel {
    width: 100%;
    height: 15vh;
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px;
    overflow-y: auto;
}

#coordinates, #heading {
    margin: 5px 0;
    font-size: 0.9em;
}

#nearby-points {
    margin-top: 5px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.point-item {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 5px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    max-width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

@media (max-width: 600px) {
    #simulator-view {
        height: 50vh;
    }
    
    #map-container {
        height: 30vh;
    }
    
    #info-panel {
        height: 20vh;
    }
}
""")

# Create JavaScript file
with open('static/app.js', 'w', encoding='utf-8') as f:  # Added encoding='utf-8'
    f.write("""
// AR Navigation Simulator

// Main app state
const state = {
    position: {
        latitude: 37.7749,  // San Francisco
        longitude: -122.4194
    },
    heading: 0,  // 0 = North, 90 = East, 180 = South, 270 = West
    navigationPoints: [],
    movementSpeed: 0.00005,  // approx 5m in latitude degrees
    rotationSpeed: 15  // degrees
};

// DOM Elements
const arOverlay = document.getElementById('ar-overlay');
const statusEl = document.getElementById('status');
const coordinatesEl = document.getElementById('coordinates');
const headingEl = document.getElementById('heading');
const nearbyPointsEl = document.getElementById('nearby-points');
const compassNeedle = document.getElementById('compass-needle');
const userMarker = document.getElementById('user-marker');
const mapEl = document.getElementById('map');

// Control buttons
const rotateLeftBtn = document.getElementById('rotate-left');
const moveForwardBtn = document.getElementById('move-forward');
const rotateRightBtn = document.getElementById('rotate-right');

// Initialize the application
async function init() {
    // Set up event listeners
    rotateLeftBtn.addEventListener('click', rotateLeft);
    moveForwardBtn.addEventListener('click', moveForward);
    rotateRightBtn.addEventListener('click', rotateRight);
    
    // Add keyboard controls
    window.addEventListener('keydown', handleKeyDown);
    
    // Fetch navigation points
    await fetchNavigationPoints();
    
    // Initial update
    updateDisplay();
    updateARScene();
    createMapPoints();
    
    // Update loop
    setInterval(() => {
        updateARScene();
        updateMapPoints();
    }, 100);
    
    // Status message
    statusEl.textContent = 'Ready - Use buttons or arrow keys to move and rotate';
}

// Handle keyboard controls
function handleKeyDown(e) {
    if (e.key === 'ArrowLeft') {
        rotateLeft();
    } else if (e.key === 'ArrowRight') {
        rotateRight();
    } else if (e.key === 'ArrowUp') {
        moveForward();
    }
}

// Rotate left (counter-clockwise)
function rotateLeft() {
    state.heading = (state.heading - state.rotationSpeed + 360) % 360;
    updateDisplay();
}

// Rotate right (clockwise)
function rotateRight() {
    state.heading = (state.heading + state.rotationSpeed) % 360;
    updateDisplay();
}

// Move forward in the current heading direction
function moveForward() {
    // Convert heading to radians
    const headingRad = state.heading * Math.PI / 180;
    
    // Calculate new position
    // We move in the opposite direction of the heading (0 = North, so we go up)
    state.position.latitude += state.movementSpeed * Math.cos(headingRad);
    state.position.longitude += state.movementSpeed * Math.sin(headingRad);
    
    updateDisplay();
}

// Update display elements
function updateDisplay() {
    // Update heading display
    headingEl.textContent = `Heading: ${state.heading}° (${getCardinalDirection(state.heading)})`;
    
    // Update compass needle
    compassNeedle.style.transform = `translate(-50%, -100%) rotate(${state.heading}deg)`;
    
    // Update position display
    coordinatesEl.textContent = `Position: ${state.position.latitude.toFixed(6)}, ${state.position.longitude.toFixed(6)} (simulated)`;
    
    // Update user marker direction
    userMarker.querySelector(':after')?.style?.transform = `translateX(-50%) rotate(${state.heading}deg)`;
    
    // Update nearby points list
    updateNearbyPointsList();
}

// Get cardinal direction name from heading
function getCardinalDirection(heading) {
    const directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest'];
    return directions[Math.round(heading / 45) % 8];
}

// Fetch navigation points from the backend
async function fetchNavigationPoints() {
    try {
        const response = await fetch('/navigation-points');
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        
        state.navigationPoints = await response.json();
        
    } catch (error) {
        console.error('Error fetching navigation points:', error);
        statusEl.textContent = `Error loading navigation data: ${error.message}`;
    }
}

// Update the list of nearby points in the info panel
function updateNearbyPointsList() {
    nearbyPointsEl.innerHTML = '';
    
    if (state.navigationPoints.length === 0) {
        nearbyPointsEl.innerHTML = '<div class="point-item">No navigation points found.</div>';
        return;
    }
    
    // Sort points by distance
    const sortedPoints = [...state.navigationPoints].sort((a, b) => {
        const distA = calculateDistance(
            state.position.latitude,
            state.position.longitude,
            a.latitude,
            a.longitude
        );
        const distB = calculateDistance(
            state.position.latitude,
            state.position.longitude,
            b.latitude,
            b.longitude
        );
        return distA - distB;
    });
    
    // Take only closest 5 points
    sortedPoints.slice(0, 5).forEach(point => {
        const distance = calculateDistance(
            state.position.latitude,
            state.position.longitude,
            point.latitude,
            point.longitude
        );
        
        const pointEl = document.createElement('div');
        pointEl.className = 'point-item';
        pointEl.innerHTML = `${point.title}: ${distance.toFixed(0)}m`;
        pointEl.title = point.description;
        nearbyPointsEl.appendChild(pointEl);
    });
}

// Create map points
function createMapPoints() {
    state.navigationPoints.forEach((point, index) => {
        const pointEl = document.createElement('div');
        pointEl.className = 'map-point';
        pointEl.id = `map-point-${index}`;
        pointEl.title = `${point.title}: ${point.description}`;
        mapEl.appendChild(pointEl);
    });
    
    updateMapPoints();
}

// Update map point positions
function updateMapPoints() {
    state.navigationPoints.forEach((point, index) => {
        const pointEl = document.getElementById(`map-point-${index}`);
        if (!pointEl) return;
        
        // Calculate position on map
        // Center of map is the user's position
        // Convert to relative position
        const latDiff = point.latitude - state.position.latitude;
        const lngDiff = point.longitude - state.position.longitude;
        
        // Scale factor (how many pixels per degree)
        const scale = 100000;
        
        const x = 50 + (lngDiff * scale);
        const y = 50 - (latDiff * scale);
        
        // Set position
        pointEl.style.left = `${x}%`;
        pointEl.style.top = `${y}%`;
    });
}

// Update the AR scene with navigation markers
function updateARScene() {
    // Clear existing markers
    arOverlay.innerHTML = '';
    
    if (state.navigationPoints.length === 0) {
        return;
    }
    
    // Place each navigation point in the AR view
    state.navigationPoints.forEach(point => {
        // Calculate bearing and distance
        const bearing = calculateBearing(
            state.position.latitude,
            state.position.longitude,
            point.latitude,
            point.longitude
        );
        
        const distance = calculateDistance(
            state.position.latitude,
            state.position.longitude,
            point.latitude,
            point.longitude
        );
        
        // Calculate relative bearing (adjust based on where user is facing)
        const relativeBearing = ((bearing - state.heading) + 360) % 360;
        
        // Only show points that are roughly in front of us
        if (relativeBearing > 300 || relativeBearing < 60) {
            // Map the bearing to screen coordinates
            const screenX = arOverlay.offsetWidth / 2 + (((relativeBearing > 180 ? relativeBearing - 360 : relativeBearing) / 60) * arOverlay.offsetWidth / 2);
            
            // Vertical position based on distance (closer = lower)
            const screenY = arOverlay.offsetHeight / 2 + (distance / 100 * arOverlay.offsetHeight / 4);
            
            // Create marker element
            const marker = document.createElement('div');
            marker.className = 'ar-marker';
            marker.textContent = `${point.title} (${distance.toFixed(0)}m)`;
            marker.style.left = `${screenX}px`;
            marker.style.top = `${screenY}px`;
            
            // Scale based on distance (closer = bigger)
            const scale = Math.max(0.5, Math.min(1.5, 1 - (distance / 500)));
            marker.style.transform = `translate(-50%, -50%) scale(${scale})`;
            
            // Add click event to show details
            marker.addEventListener('click', () => {
                alert(`${point.title}: ${point.description}`);
            });
            
            arOverlay.appendChild(marker);
        }
    });
}

// Calculate distance between two points in meters
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;
    
    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    
    return R * c;
}

// Calculate bearing from point 1 to point 2 in degrees
function calculateBearing(lat1, lon1, lat2, lon2) {
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;
    
    const y = Math.sin(Δλ) * Math.cos(φ2);
    const x = Math.cos(φ1) * Math.sin(φ2) -
              Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ);
    
    const θ = Math.atan2(y, x);
    
    return (θ * 180 / Math.PI + 360) % 360; // in degrees
}

// Start the application when the page is loaded
window.addEventListener('load', init);
""")

if __name__ == '__main__':
    print("AR Navigation Simulator Created!")
    print("To run the application:")
    print("1. Install Flask if you haven't already: pip install flask")
    print("2. Run the app: python app.py")
    print("3. Open a web browser and navigate to http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)