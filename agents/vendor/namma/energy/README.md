# Energy Management Orchestrator

This project implements an energy management orchestrator that utilizes sub LLM agents to handle various tasks related to energy management. The orchestrator coordinates the interactions and data flow between the agents, which operate in parallel to enhance efficiency and responsiveness.

## Project Structure

```
/workspaces/NammaOmniAI/
└── agents/
    └── energy-management-orchestrator/
        ├── agent_config.json           # Agent configuration settings
        ├── agents.py                   # Defines the sub LLM agents (BESCOM Event, Accident, Environment)
        ├── Dockerfile                  # Multi-stage Docker build for Cloud Run deployment
        ├── orca.py                     # Main orchestrator that runs the agents in parallel
        ├── README.md                   # Project documentation
        ├── requirements.txt            # Python dependencies for the project
        └── tools.py                    # Utility functions (logging, data processing, etc.)
```

## File Descriptions

- **agent_config.json**: Structured configuration settings for the agents, including parameters such as agent names, execution settings, and specific configurations required for each sub agent.
- **agents.py**: Defines the sub LLM agents for the energy management orchestrator:
  - **BESCOM Event Agent**: Handles events related to BESCOM operations.
  - **Accident Agent**: Manages incidents and accidents that may affect energy supply or consumption.
  - **Environment Agent**: Monitors environmental factors that influence energy management.
- **Dockerfile**: A multi‑stage Dockerfile that builds and packages the application for deployment on Cloud Run.
- **orca.py**: The main orchestrator that initializes and manages the execution of the sub agents concurrently.
- **requirements.txt**: Lists the required Python packages.
- **tools.py**: Contains utility functions that support data processing and logging for the orchestrator and agents.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd agents/energy-management-orchestrator
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the energy management orchestrator, execute the following command:
```
python orca.py
```

This will initialize the sub agents and start their execution in parallel.

## Agent Functionalities

- **BESCOM Event Agent**: Monitors and responds to events from BESCOM, ensuring timely updates and actions based on electricity supply changes.
- **Accident Agent**: Detects and manages accidents that may disrupt energy supply, coordinating with relevant authorities and providing updates.
- **Environment Agent**: Gathers and analyzes environmental data to inform energy management decisions, helping to optimize energy usage based on external conditions.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.