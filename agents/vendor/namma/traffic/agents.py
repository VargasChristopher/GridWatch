import json
from google.adk.agents import LlmAgent

# Load agent configs locally to avoid circular import with orca.py
def _load_agent_configs(path: str = 'agent_config.json'):
    with open(path, 'r') as f:
        cfg = json.load(f)
    road_block_config = None
    accident_config = None
    environment_config = None
    for agent in cfg.get("agents", []):
        name = agent.get("name", "")
        if "RoadBlock" in name:
            road_block_config = agent
        elif "Accident" in name:
            accident_config = agent
        elif "Environment" in name:
            environment_config = agent
    return road_block_config, accident_config, environment_config

road_block_config, accident_config, environment_config = _load_agent_configs('agent_config.json')

# Create LLM agents using attributes from configuration
road_block_agent = LlmAgent(
    name=road_block_config["name"],
    model=road_block_config["model"],
    instruction=road_block_config["instruction"],
    input_schema=road_block_config.get("input_schema"),
    output_key=road_block_config["output_key"],
)

accident_agent = LlmAgent(
    name=accident_config["name"],
    model=accident_config["model"],
    instruction=accident_config["instruction"],
    input_schema=accident_config.get("input_schema"),
    output_key=accident_config["output_key"],
)

environment_agent = LlmAgent(
    name=environment_config["name"],
    model=environment_config["model"],
    instruction=environment_config["instruction"],
    input_schema=environment_config.get("input_schema"),
    output_key=environment_config["output_key"],
)