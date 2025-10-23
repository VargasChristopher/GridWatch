/**
 * GridWatch API Client
 * Handles communication with the backend API
 */

class GridWatchAPI {
  constructor(
    baseURL = "https://gridwatch-backend-554454627121.us-east1.run.app"
  ) {
    this.baseURL = baseURL;
    this.pollInterval = null;
    this.onIncidentsUpdate = null;
  }

  /**
   * Check if backend is healthy
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch (error) {
      console.error("Health check failed:", error);
      return false;
    }
  }

  /**
   * Fetch incidents from backend
   */
  async getIncidents(limit = 20, since = null, city = null) {
    try {
      const params = new URLSearchParams();
      if (limit) params.append("limit", limit);
      if (since) params.append("since", since);
      if (city) params.append("city", city);

      const url = `${this.baseURL}/incidents${
        params.toString() ? "?" + params.toString() : ""
      }`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
      return [];
    }
  }

  /**
   * Post evidence to backend (for testing)
   */
  async postEvidence(evidence) {
    try {
      const response = await fetch(`${this.baseURL}/evidence`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(evidence),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to post evidence:", error);
      throw error;
    }
  }

  /**
   * Start polling for incidents
   */
  startPolling(intervalMs = 30000, onUpdate = null) {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    this.onIncidentsUpdate = onUpdate;

    // Initial fetch
    this.pollIncidents();

    // Set up polling
    this.pollInterval = setInterval(() => {
      this.pollIncidents();
    }, intervalMs);
  }

  /**
   * Stop polling
   */
  stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  /**
   * Internal polling method
   */
  async pollIncidents() {
    try {
      const incidents = await this.getIncidents();
      if (this.onIncidentsUpdate) {
        this.onIncidentsUpdate(incidents);
      }
    } catch (error) {
      console.error("Polling failed:", error);
    }
  }

  /**
   * Transform backend incident to frontend format
   */
  transformIncident(incident) {
    return {
      id: incident.id,
      type: incident.type,
      title: this.getIncidentTitle(incident),
      severity: this.getSeverityLevel(incident.severity),
      confidence: incident.confidence,
      lat: incident.lat,
      lng: incident.lng,
      where: this.getLocationDescription(incident),
      eta: this.getETA(incident),
      sources: incident.sources || [],
      actions: incident.actions || [],
      created_at: incident.created_at,
      status: incident.status,
      cat: this.getCategory(incident.type), // Add category for filtering
      icon: this.getIncidentIcon(incident), // Add icon for display
      color: this.getIncidentColor(incident), // Add color for display
    };
  }

  /**
   * Get severity level from numeric severity
   */
  getSeverityLevel(severity) {
    if (severity >= 0.7) return "hi";
    if (severity >= 0.4) return "med";
    return "low";
  }

  /**
   * Get incident title from backend data
   */
  getIncidentTitle(incident) {
    if (incident.summary) {
      return incident.summary;
    }

    // Generate title based on type
    const typeTitles = {
      road_closure: "Road Closure",
      accident: "Traffic Accident",
      congestion: "Traffic Congestion",
      power_outage: "Power Outage",
      water_main_break: "Water Main Break",
      gas_leak: "Gas Leak",
      internet_outage: "Internet Outage",
      crime: "Crime Incident",
      environment: "Environmental Hazard",
      emergency: "Emergency Alert",
    };

    return typeTitles[incident.type] || `${incident.type} Incident`;
  }

  /**
   * Get category for filtering
   */
  getCategory(incidentType) {
    const categoryMap = {
      road_closure: "traffic",
      accident: "traffic",
      congestion: "traffic",
      power_outage: "outage",
      water_main_break: "outage",
      gas_leak: "outage",
      internet_outage: "outage",
      crime: "crime",
      environment: "environment",
      emergency: "emergency",
    };

    return categoryMap[incidentType] || "outage";
  }

  /**
   * Get location description
   */
  getLocationDescription(incident) {
    const lat = incident.lat;
    const lng = incident.lng;

    // City detection with more precise ranges
    const cities = [
      { name: "Washington, DC", latMin: 38.85, latMax: 38.95, lngMin: -77.1, lngMax: -77.0, landmarks: [
        { name: "Downtown DC", latMin: 38.89, latMax: 38.91, lngMin: -77.05, lngMax: -77.03 },
        { name: "Capitol Hill", latMin: 38.88, latMax: 38.92, lngMin: -77.08, lngMax: -77.04 },
        { name: "National Mall", latMin: 38.9, latMax: 38.94, lngMin: -77.06, lngMax: -77.02 }
      ]},
      { name: "New York, NY", latMin: 40.6, latMax: 40.9, lngMin: -74.3, lngMax: -73.7, landmarks: [
        { name: "Manhattan", latMin: 40.7, latMax: 40.8, lngMin: -74.0, lngMax: -73.9 },
        { name: "Brooklyn", latMin: 40.6, latMax: 40.7, lngMin: -74.0, lngMax: -73.9 }
      ]},
      { name: "Los Angeles, CA", latMin: 33.7, latMax: 34.3, lngMin: -118.7, lngMax: -118.1, landmarks: [
        { name: "Downtown LA", latMin: 34.0, latMax: 34.1, lngMin: -118.3, lngMax: -118.2 },
        { name: "Hollywood", latMin: 34.0, latMax: 34.1, lngMin: -118.4, lngMax: -118.3 }
      ]},
      { name: "Seattle, WA", latMin: 47.4, latMax: 47.8, lngMin: -122.5, lngMax: -122.2, landmarks: [
        { name: "Downtown Seattle", latMin: 47.6, latMax: 47.7, lngMin: -122.4, lngMax: -122.3 }
      ]},
      { name: "San Francisco, CA", latMin: 37.7, latMax: 37.9, lngMin: -122.5, lngMax: -122.3, landmarks: [
        { name: "Downtown SF", latMin: 37.7, latMax: 37.8, lngMin: -122.5, lngMax: -122.4 }
      ]},
      { name: "Miami, FL", latMin: 25.6, latMax: 25.9, lngMin: -80.4, lngMax: -80.1, landmarks: [
        { name: "South Beach", latMin: 25.7, latMax: 25.8, lngMin: -80.2, lngMax: -80.1 }
      ]},
      { name: "Chicago, IL", latMin: 41.6, latMax: 42.1, lngMin: -87.9, lngMax: -87.5, landmarks: [
        { name: "Downtown Chicago", latMin: 41.8, latMax: 42.0, lngMin: -87.7, lngMax: -87.6 }
      ]},
      { name: "Dallas, TX", latMin: 32.6, latMax: 33.0, lngMin: -97.0, lngMax: -96.6, landmarks: [
        { name: "Downtown Dallas", latMin: 32.7, latMax: 32.8, lngMin: -96.8, lngMax: -96.7 }
      ]},
      { name: "Las Vegas, NV", latMin: 36.0, latMax: 36.3, lngMin: -115.3, lngMax: -115.0, landmarks: [
        { name: "The Strip", latMin: 36.1, latMax: 36.2, lngMin: -115.2, lngMax: -115.1 }
      ]},
      { name: "Denver, CO", latMin: 39.6, latMax: 39.9, lngMin: -105.2, lngMax: -104.8, landmarks: [
        { name: "Downtown Denver", latMin: 39.7, latMax: 39.8, lngMin: -105.0, lngMax: -104.9 }
      ]}
    ];

    // Find the city and landmark
    for (const city of cities) {
      if (lat >= city.latMin && lat <= city.latMax && lng >= city.lngMin && lng <= city.lngMax) {
        // Check for specific landmarks within the city
        for (const landmark of city.landmarks) {
          if (lat >= landmark.latMin && lat <= landmark.latMax && lng >= landmark.lngMin && lng <= landmark.lngMax) {
            return landmark.name;
          }
        }
        return city.name;
      }
    }

    // Fallback to coordinates for other areas
    return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
  }

  /**
   * Get estimated time to resolution
   */
  getETA(incident) {
    // Simple ETA calculation based on severity
    const severity = incident.severity || 0.5;
    if (severity >= 0.7) return "4h";
    if (severity >= 0.4) return "2h";
    return "1h";
  }

  /**
   * Get incident icon based on type
   */
  getIncidentIcon(incident) {
    const iconMap = {
      road_closure: "🚧",
      accident: "🚗",
      congestion: "🚦",
      power_outage: "⚡",
      water_main_break: "💧",
      gas_leak: "🔥",
      internet_outage: "📡",
      crime: "🚔",
      environment: "🌍",
      emergency: "🚨",
    };

    return iconMap[incident.type] || "⚠️";
  }

  /**
   * Get incident color based on type
   */
  getIncidentColor(incident) {
    const colorMap = {
      road_closure: "#FF9800", // Orange
      accident: "#FF9800", // Orange
      congestion: "#FF9800", // Orange
      power_outage: "#F44336", // Red
      water_main_break: "#2196F3", // Blue
      gas_leak: "#FF5722", // Deep Orange
      internet_outage: "#9C27B0", // Purple
      crime: "#9C27B0", // Purple
      environment: "#4CAF50", // Green
      emergency: "#FF5722", // Deep Orange
    };

    return colorMap[incident.type] || "#757575";
  }
}

// Export for use in other scripts
window.GridWatchAPI = GridWatchAPI;
