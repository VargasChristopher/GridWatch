from google.adk.agents import LlmAgent
from orca import load_agent_config

# Load the entire configuration from agent_config.json
config_map = load_agent_config('agent_config.json')

# Extract individual agent configurations
road_block_config = config_map.get("RoadBlockAgent")
accident_config = config_map.get("AccidentAgent")
environment_config = config_map.get("EnvironmentAgent")

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