/**
 * GridWatch API Client
 * Handles communication with the backend API
 */

class GridWatchAPI {
  constructor(baseURL = 'https://gridwatch-backend-554454627121.us-east1.run.app') {
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
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Fetch incidents from backend
   */
  async getIncidents(limit = 20, since = null) {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit);
      if (since) params.append('since', since);
      
      const url = `${this.baseURL}/incidents${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
      return [];
    }
  }

  /**
   * Post evidence to backend (for testing)
   */
  async postEvidence(evidence) {
    try {
      const response = await fetch(`${this.baseURL}/evidence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(evidence)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to post evidence:', error);
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
      console.error('Polling failed:', error);
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
      color: this.getIncidentColor(incident) // Add color for display
    };
  }

  /**
   * Get severity level from numeric severity
   */
  getSeverityLevel(severity) {
    if (severity >= 0.7) return 'hi';
    if (severity >= 0.4) return 'med';
    return 'low';
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
      'road_closure': 'Road Closure',
      'accident': 'Traffic Accident', 
      'congestion': 'Traffic Congestion',
      'power_outage': 'Power Outage',
      'water_main_break': 'Water Main Break',
      'gas_leak': 'Gas Leak',
      'internet_outage': 'Internet Outage',
      'crime': 'Crime Incident',
      'environment': 'Environmental Hazard',
      'emergency': 'Emergency Alert'
    };
    
    return typeTitles[incident.type] || `${incident.type} Incident`;
  }

  /**
   * Get category for filtering
   */
  getCategory(incidentType) {
    const categoryMap = {
      'road_closure': 'traffic',
      'accident': 'traffic', 
      'congestion': 'traffic',
      'power_outage': 'outage',
      'water_main_break': 'outage',
      'gas_leak': 'outage',
      'internet_outage': 'outage',
      'crime': 'crime',
      'environment': 'environment',
      'emergency': 'emergency'
    };
    
    return categoryMap[incidentType] || 'outage';
  }

  /**
   * Get location description
   */
  getLocationDescription(incident) {
    // For Washington, DC area, provide more meaningful locations
    const lat = incident.lat;
    const lng = incident.lng;
    
    // Washington, DC area landmarks
    if (lat >= 38.85 && lat <= 38.95 && lng >= -77.1 && lng <= -77.0) {
      if (lat >= 38.89 && lat <= 38.91 && lng >= -77.05 && lng <= -77.03) {
        return "Downtown DC";
      } else if (lat >= 38.88 && lat <= 38.92 && lng >= -77.08 && lng <= -77.04) {
        return "Capitol Hill Area";
      } else if (lat >= 38.90 && lat <= 38.94 && lng >= -77.06 && lng <= -77.02) {
        return "National Mall";
      } else if (lat >= 38.85 && lat <= 38.89 && lng >= -77.08 && lng <= -77.04) {
        return "Southwest DC";
      } else if (lat >= 38.91 && lat <= 38.95 && lng >= -77.08 && lng <= -77.04) {
        return "Northeast DC";
      } else {
        return "Washington, DC";
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
    if (severity >= 0.7) return '4h';
    if (severity >= 0.4) return '2h';
    return '1h';
  }

  /**
   * Get incident icon based on type
   */
  getIncidentIcon(incident) {
    const iconMap = {
      'road_closure': '🚧',
      'accident': '🚗',
      'congestion': '🚦',
      'power_outage': '⚡',
      'water_main_break': '💧',
      'gas_leak': '🔥',
      'internet_outage': '📡',
      'crime': '🚔',
      'environment': '🌍',
      'emergency': '🚨'
    };
    
    return iconMap[incident.type] || '⚠️';
  }

  /**
   * Get incident color based on type
   */
  getIncidentColor(incident) {
    const colorMap = {
      'road_closure': '#FF9800',    // Orange
      'accident': '#FF9800',         // Orange
      'congestion': '#FF9800',       // Orange
      'power_outage': '#F44336',     // Red
      'water_main_break': '#2196F3', // Blue
      'gas_leak': '#FF5722',         // Deep Orange
      'internet_outage': '#9C27B0',  // Purple
      'crime': '#9C27B0',            // Purple
      'environment': '#4CAF50',      // Green
      'emergency': '#FF5722'         // Deep Orange
    };
    
    return colorMap[incident.type] || '#757575';
  }
}

// Export for use in other scripts
window.GridWatchAPI = GridWatchAPI;
