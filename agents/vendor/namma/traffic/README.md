# Traffic Update Orchestrator

This project implements a traffic update orchestrator that utilizes sub LLM agents to handle various tasks related to traffic management. The orchestrator coordinates the interactions and data flow between the agents, which operate in parallel to enhance efficiency and responsiveness.

## Project Structure

```
traffic-update-orchestrator/
├── agent_config.json           # Agent configuration settings
├── agents.py                   # Defines the sub LLM agents (Road Block, Accident, Environment)
├── Dockerfile                  # Multi-stage Docker build for Cloud Run deployment
├── orca.py                     # Main orchestrator that runs the agents in parallel
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies for the project
```

## File Descriptions

- **agent_config.json**: Structured configuration settings for the agents, including parameters such as agent names, execution settings, and specific configurations required for each sub-agent.
- **agents.py**: Defines the sub LLM agents for the traffic update orchestrator:
  - **RoadBlockAgent**: Handles updates related to road blocks.
  - **AccidentAgent**: Monitors and responds to accident reports affecting traffic.
  - **EnvironmentAgent**: Tracks environmental conditions that may impact traffic flow.
- **Dockerfile**: A multi-stage Dockerfile that builds and packages the application for deployment on Cloud Run.
- **orca.py**: The main orchestrator that initializes and manages the execution of the sub-agents concurrently.
- **requirements.txt**: Lists the required Python packages.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd traffic-update-orchestrator
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the traffic update orchestrator, execute the following command:
```
python orca.py
```

This will initialize the sub-agents and start their execution in parallel.

## Agent Functionalities

- **RoadBlockAgent**: Provides updates on road blocks in the area, ensuring timely information for traffic management.
- **AccidentAgent**: Detects and manages accidents that may disrupt traffic flow, coordinating with relevant authorities and providing updates.
- **EnvironmentAgent**: Gathers and analyzes environmental data to inform traffic management decisions, helping to optimize traffic flow based on external conditions.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.