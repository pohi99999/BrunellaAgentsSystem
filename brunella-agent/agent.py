import subprocess
from typing import List, Dict

import vertexai
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


def _get_function_call(response):
    """Best-effort extraction of a function call from a Vertex response."""
    try:
        parts = response.candidates[0].content.parts  # type: ignore[attr-defined]
    except Exception:
        return None

    for part in parts:
        function_call = getattr(part, "function_call", None)
        if function_call and getattr(function_call, "name", None):
            return function_call
    return None


def _response_text(response) -> str:
    """Extract printable text from a Vertex response."""
    text = getattr(response, "text", None)
    if text:
        return text
    try:
        parts = response.candidates[0].content.parts  # type: ignore[attr-defined]
        return "".join([getattr(p, "text", "") for p in parts]).strip()
    except Exception:
        return str(response)


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
    
    max_tool_turns = 10
    tool_turns = 0

    function_call = _get_function_call(response)
    while function_call and tool_turns < max_tool_turns:
        tool_turns += 1
        print(f"[Brunella Gondolkodik]: Eszközt kell használnom: '{function_call.name}'")
        
        if function_call.name == "list_vm_instances":
            args = dict(getattr(function_call, "args", {}) or {})
            tool_result = list_vm_instances(
                project_id=args.get("project_id", GCP_PROJECT),
                zone=args.get("zone", GCP_ZONE),
            )
        else:
            tool_result = {"error": f"Ismeretlen eszköz: {function_call.name}"}

        # Tool result back to the model.
        response = chat_session.send_message(
            Part.from_function_response(
                name=function_call.name,
                response={"result": tool_result},
            )
        )
        function_call = _get_function_call(response)

    if tool_turns >= max_tool_turns:
        print("!!! Figyelem: túl sok tool-kör, megszakítva a végtelen ciklus elkerülésére.")

    final_text = _response_text(response)
    if final_text:
        print(f"\n[Brunella Válasza]:\n{final_text}")
    else:
        print("\n[Brunella Válasza]: (nincs szöveges válasz)")


if __name__ == "__main__":
    main()
