# agent.py

import os
import vertexai
import subprocess
from typing import List, Dict
from google.cloud import compute_v1
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from google.api_core.exceptions import PermissionDenied

# --- ESZKÖZ (TOOL) DEFINÍCIÓ ---
def list_vm_instances(project_id: str, zone: str) -> List[Dict[str, str]]:
    """Listázza az összes VM instance-ot egy adott GCP projektben és zónában."""
    print(f"\n[Brunella Eszköz Végrehajtás]: VM-ek listázása a '{project_id}' projektben, '{zone}' zónában...")
    try:
        client = compute_v1.InstancesClient()
        request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
        response = client.list(request=request)
        results = [{"name": instance.name, "status": instance.status} for instance in response]
        if not results:
            print("[Brunella Eszköz Eredmény]: Nincsenek VM-ek a megadott helyen.")
            return [{"status": "Nincsenek VM-ek a megadott zónában."}]
        print(f"[Brunella Eszköz Eredmény]: {len(results)} db VM található.")
        return results
    except Exception as e:
        print(f"[Brunella Eszköz Hiba]: Hiba a VM listázásakor: {str(e)}")
        return [{"error": f"Hiba a VM listázásakor: {str(e)}"}]

# --- FŐPROGRAM ---
def main():
    print("--- Brunella Ügynök Indítása ---")
    GCP_PROJECT = "pohi-ai-pro"
    GCP_REGION = "us-central1"
    GCP_ZONE = "us-central1-a"

    print(f"Hitelesítés és inicializálás a '{GCP_PROJECT}' projekthez a '{GCP_REGION}' régióban...")
    try:
        vertexai.init(project=GCP_PROJECT, location=GCP_REGION)
        print(">>> Vertex AI sikeresen inicializálva.")
    except PermissionDenied:
        print(f"!!! Hiba: A Vertex AI API (aiplatform.googleapis.com) valószínűleg nincs engedélyezve a '{GCP_PROJECT}' projektben.")
        print(">>> Megpróbálom automatikusan engedélyezni...")
        try:
            # Automatikus, "önjavító" API engedélyezés
            subprocess.run(
                ["gcloud", "services", "enable", "aiplatform.googleapis.com", f"--project={GCP_PROJECT}"],
                check=True
            )
            print(">>> API sikeresen engedélyezve. Újrapróbálom az inicializálást...")
            vertexai.init(project=GCP_PROJECT, location=GCP_REGION)
            print(">>> Vertex AI sikeresen inicializálva a második próbálkozásra.")
        except Exception as e:
            print(f"!!! Az automatikus API engedélyezés sikertelen: {e}")
            return
    except Exception as e:
        print(f"!!! Váratlan hiba az inicializáláskor: {e}")
        return

    # --- Eszközök Definiálása ---
    list_vms_tool = FunctionDeclaration(
        name="list_vm_instances",
        description="Listázza az összes VM instance-ot egy adott GCP projektben és zónában.",
        parameters={"type": "object", "properties": {"project_id": {"type": "string"}, "zone": {"type": "string"}}, "required": ["project_id", "zone"]},
    )

    # --- Az Agy (Gemini Modell) Létrehozása ---
    agent_model = GenerativeModel("gemini-1.5-flash-001", tools=[Tool([list_vms_tool])])
    chat_session = agent_model.start_chat()

    prompt = f"Szia Brunella, légyszi listázd ki nekem a virtuális gépeket a '{GCP_PROJECT}' projektben, a '{GCP_ZONE}' zónában."
    print(f"\n[Felhasználó Kérése]: {prompt}")
    
    # --- MANUÁLIS FÜGGVÉNYHÍVÁSI CIKLUS ---
    response = chat_session.send_message(prompt)
    
    while response.candidates[0].content.parts[0].function_call.name:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"[Brunella Gondolkodik]: Eszközt kell használnom: '{function_call.name}'")
        
        if function_call.name == "list_vm_instances":
            args = function_call.args
            tool_result = list_vm_ins
