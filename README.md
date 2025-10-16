# 🚀 GridWatch - Multi-Incident Monitoring System

GridWatch is a comprehensive city management system that monitors and displays real-time incidents across 5 different categories using AI agents. Built for the DevFestDC 25 Agentic AI Hackathon.

## 🌐 **Live System**
- **Frontend**: [https://gridwatch.dev/](https://gridwatch.dev/)
- **Backend API**: `https://gridwatch-backend-554454627121.us-east1.run.app`
- **Status**: ✅ Production Ready

## 📊 **What GridWatch Monitors**

| Incident Type | Icon | Description | Sources |
|---------------|------|-------------|---------|
| 🚗 **Traffic** | 🚗 | Congestion, accidents, road closures | BBMP, BTP, social media |
| ⚡ **Outage** | ⚡ | Power outages, utility failures | BESCOM, news reports |
| 🚔 **Crime** | 🚔 | Police reports, public safety alerts | Police, news, social media |
| 🌍 **Environment** | 🌍 | Weather, air quality, environmental hazards | NWS, EPA, USGS |
| 🚨 **Emergency** | 🚨 | Road closures, emergency services, public alerts | DOT, 911, FEMA |

## 🚀 **Quick Start**

### **1. Check Your Live System**
```bash
# Health check
curl https://gridwatch-backend-554454627121.us-east1.run.app/health

# View current incidents
curl https://gridwatch-backend-554454627121.us-east1.run.app/incidents
```

### **2. Run All Agents**
```bash
# Run once (testing)
python3.11 run_agents_live.py

# Run continuously (production)
python3.11 integration/enhanced_agent_runner.py

# Easy startup
./start_all_agents.sh
```

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    GridWatch System                     │
├─────────────────────────────────────────────────────────┤
│  Frontend (Web App)                                     │
│  ├─ Real-time incident display                          │
│  ├─ Interactive map with filtering                     │
│  └─ Live updates from backend                          │
├─────────────────────────────────────────────────────────┤
│  Live Firebase Backend                                  │
│  ├─ FastAPI server                                      │
│  ├─ Firestore database                                 │
│  └─ REST API endpoints                                  │
├─────────────────────────────────────────────────────────┤
│  AI Agent System (5 Agents)                            │
│  ├─ 🚗 Traffic Agent    (congestion, accidents)        │
│  ├─ ⚡ Outage Agent     (power failures)              │
│  ├─ 🚔 Crime Agent      (public safety)               │
│  ├─ 🌍 Environment Agent (weather, air quality)       │
│  └─ 🚨 Emergency Agent  (road closures, alerts)       │
└─────────────────────────────────────────────────────────┘
```

## 🔧 **Core Files**

### **Essential Scripts (Only 3!)**
- **`run_agents_live.py`** - Run all agents once
- **`integration/enhanced_agent_runner.py`** - Run agents continuously
- **`start_all_agents.sh`** - Easy startup script

### **Backend**
- **`backend/`** - FastAPI server with Firestore integration
- **`frontend/webapp/`** - Web application with real-time updates

### **Agents**
- **`agents/vendor/namma/traffic/`** - Traffic monitoring
- **`agents/vendor/namma/energy/`** - Power outage monitoring
- **`agents/vendor/namma/crime/`** - Crime monitoring
- **`agents/vendor/namma/environment/`** - Environmental monitoring
- **`agents/vendor/namma/emergency/`** - Emergency monitoring

## 🌐 **Live Backend Features**

✅ **Real-time Data** - Incidents automatically saved to Firestore  
✅ **REST API** - `/health` and `/incidents` endpoints  
✅ **CORS Enabled** - Frontend can access the backend  
✅ **All 5 Incident Types** - Traffic, Outage, Crime, Environment, Emergency  
✅ **Secure** - Environment variables stored in cloud  

## 🎯 **Current Status**

Your live backend is already working with:
- **12+ incidents** currently stored
- **All 5 incident types** supported
- **Real-time updates** from agents
- **Frontend integration** with proper styling

## 🔒 **Security**

- ✅ **No API keys in code** - All sensitive data in cloud environment
- ✅ **Secure cloud storage** - Environment variables encrypted
- ✅ **Production ready** - Same environment as deployed backend

## 📚 **Documentation**

- **`AGENTS_SUMMARY.md`** - Complete agent documentation
- **`COMPLETE_ARCHITECTURE.md`** - System architecture details
- **`CLOUD_SETUP.md`** - Cloud environment setup guide

## 🚀 **Deployment**

### **Local Development**
```bash
# Run agents locally (posts to cloud backend)
python3.11 run_agents_live.py
```

### **Production**
```bash
# Run agents continuously
python3.11 integration/enhanced_agent_runner.py
```

### **Monitoring**
- **Backend Health**: `https://gridwatch-backend-554454627121.us-east1.run.app/health`
- **Incidents API**: `https://gridwatch-backend-554454627121.us-east1.run.app/incidents`
- **Frontend**: [https://gridwatch.dev/](https://gridwatch.dev/)

## 🎉 **What You Have Now**

✅ **Live Firebase Backend** - All 5 incident types supported  
✅ **Real-time Agent System** - Runs locally, posts to cloud  
✅ **Frontend Integration** - Automatic connection to live backend  
✅ **Production Ready** - Secure, clean, and efficient  
✅ **Clean Codebase** - Only essential scripts, no redundancy  

## 📞 **Support**

- **Backend Issues**: Check health endpoint and logs
- **Agent Issues**: Check individual agent logs
- **Frontend Issues**: Check browser console and network tab
- **General**: Review documentation files

---

**GridWatch - Comprehensive Multi-Incident Monitoring System** 🚀

*Built for DevFestDC 25 Agentic AI Hackathon*