# agents/gridwatch_agents/src/run_orchestrator.py
import json, os
from google.cloud import firestore
from google.adk.runtime import run_agent_from_config  # ADK runtime

CITY = os.getenv("GRIDWATCH_CITY", "Washington, DC")
BBOX = json.loads(os.getenv("GRIDWATCH_BBOX", "[-77.12,38.80,-76.90,39.00]"))

def main():
    agent = run_agent_from_config("agents/gridwatch_agents/configs/gridwatch_orchestrator.yaml")
    result = agent.invoke({"city": CITY, "bbox": BBOX})
    incidents = result["incidents"] if isinstance(result, dict) else result

    db = firestore.Client()
    col = db.collection("cities").document("dc").collection("incidents")
    batch = db.batch()
    for inc in incidents:
        doc = col.document(f"{inc['type']}-{inc['lat']:.4f}-{inc['lng']:.4f}")
        batch.set(doc, inc, merge=True)
    batch.commit()

if __name__ == "__main__":
    main()
