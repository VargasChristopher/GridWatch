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

    // Washington, DC area landmarks
    if (lat >= 38.85 && lat <= 38.95 && lng >= -77.1 && lng <= -77.0) {
      if (lat >= 38.89 && lat <= 38.91 && lng >= -77.05 && lng <= -77.03) {
        return "Downtown DC";
      } else if (
        lat >= 38.88 &&
        lat <= 38.92 &&
        lng >= -77.08 &&
        lng <= -77.04
      ) {
        return "Capitol Hill Area";
      } else if (
        lat >= 38.9 &&
        lat <= 38.94 &&
        lng >= -77.06 &&
        lng <= -77.02
      ) {
        return "National Mall";
      } else if (
        lat >= 38.85 &&
        lat <= 38.89 &&
        lng >= -77.08 &&
        lng <= -77.04
      ) {
        return "Southwest DC";
      } else if (
        lat >= 38.91 &&
        lat <= 38.95 &&
        lng >= -77.08 &&
        lng <= -77.04
      ) {
        return "Northeast DC";
      } else {
        return "Washington, DC";
      }
    }

    // New York, NY area landmarks
    if (lat >= 40.6 && lat <= 40.9 && lng >= -74.3 && lng <= -73.7) {
      if (lat >= 40.7 && lat <= 40.8 && lng >= -74.0 && lng <= -73.9) {
        return "Manhattan";
      } else if (lat >= 40.6 && lat <= 40.7 && lng >= -74.0 && lng <= -73.9) {
        return "Brooklyn";
      } else if (lat >= 40.6 && lat <= 40.8 && lng >= -74.1 && lng <= -73.9) {
        return "Queens";
      } else if (lat >= 40.8 && lat <= 40.9 && lng >= -74.0 && lng <= -73.9) {
        return "Bronx";
      } else {
        return "New York, NY";
      }
    }

    // Los Angeles, CA area landmarks
    if (lat >= 33.7 && lat <= 34.3 && lng >= -118.7 && lng <= -118.1) {
      if (lat >= 34.0 && lat <= 34.1 && lng >= -118.3 && lng <= -118.2) {
        return "Downtown LA";
      } else if (lat >= 34.0 && lat <= 34.1 && lng >= -118.5 && lng <= -118.4) {
        return "Beverly Hills";
      } else if (lat >= 33.8 && lat <= 34.2 && lng >= -118.4 && lng <= -118.1) {
        return "Hollywood";
      } else if (lat >= 33.9 && lat <= 34.1 && lng >= -118.6 && lng <= -118.3) {
        return "Santa Monica";
      } else {
        return "Los Angeles, CA";
      }
    }

    // Chicago, IL area landmarks
    if (lat >= 41.6 && lat <= 42.1 && lng >= -87.9 && lng <= -87.5) {
      if (lat >= 41.8 && lat <= 42.0 && lng >= -87.7 && lng <= -87.6) {
        return "Downtown Chicago";
      } else if (lat >= 41.7 && lat <= 41.9 && lng >= -87.8 && lng <= -87.6) {
        return "North Side";
      } else if (lat >= 41.6 && lat <= 41.8 && lng >= -87.8 && lng <= -87.6) {
        return "South Side";
      } else {
        return "Chicago, IL";
      }
    }

    // Houston, TX area landmarks
    if (lat >= 29.5 && lat <= 30.1 && lng >= -95.8 && lng <= -95.0) {
      if (lat >= 29.7 && lat <= 29.8 && lng >= -95.4 && lng <= -95.3) {
        return "Downtown Houston";
      } else {
        return "Houston, TX";
      }
    }

    // Phoenix, AZ area landmarks
    if (lat >= 33.2 && lat <= 33.7 && lng >= -112.3 && lng <= -111.8) {
      if (lat >= 33.4 && lat <= 33.5 && lng >= -112.1 && lng <= -112.0) {
        return "Downtown Phoenix";
      } else {
        return "Phoenix, AZ";
      }
    }

    // Philadelphia, PA area landmarks
    if (lat >= 39.8 && lat <= 40.1 && lng >= -75.3 && lng <= -74.9) {
      if (lat >= 39.9 && lat <= 40.0 && lng >= -75.2 && lng <= -75.1) {
        return "Center City Philadelphia";
      } else {
        return "Philadelphia, PA";
      }
    }

    // San Antonio, TX area landmarks
    if (lat >= 29.2 && lat <= 29.6 && lng >= -98.7 && lng <= -98.3) {
      if (lat >= 29.4 && lat <= 29.5 && lng >= -98.5 && lng <= -98.4) {
        return "Downtown San Antonio";
      } else {
        return "San Antonio, TX";
      }
    }

    // San Diego, CA area landmarks
    if (lat >= 32.5 && lat <= 32.9 && lng >= -117.3 && lng <= -117.0) {
      if (lat >= 32.7 && lat <= 32.8 && lng >= -117.2 && lng <= -117.1) {
        return "Downtown San Diego";
      } else {
        return "San Diego, CA";
      }
    }

    // Dallas, TX area landmarks
    if (lat >= 32.6 && lat <= 33.0 && lng >= -97.0 && lng <= -96.6) {
      if (lat >= 32.7 && lat <= 32.8 && lng >= -96.8 && lng <= -96.7) {
        return "Downtown Dallas";
      } else {
        return "Dallas, TX";
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
