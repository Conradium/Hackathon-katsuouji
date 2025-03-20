
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
