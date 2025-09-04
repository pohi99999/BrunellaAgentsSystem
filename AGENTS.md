# BrunellaAgentSystem - Ügynökök és Komponensek

Ez a dokumentum a BrunellaAgentSystem projekt felépítését írja le, hogy segítse Jules munkáját.

## Áttekintés

A projekt egy több-ügynökös AI rendszer, amely egy Python alapú backendből és egy React alapú frontendből áll. A rendszer Docker konténerekben fut, a `docker-compose.yml` fájl írja le a szolgáltatásokat.

### Főbb Komponensek

-   **Brunella (Fő koordinátor):** A `main.py`-ban és a `backend/src` könyvtárban található logika felelős a bejövő kérések feldolgozásáért és a feladatok delegálásáért a specializált ügynököknek.
-   **Backend:** Egy FastAPI/Flask alkalmazás, amely az ügynökök logikáját és az API végpontokat tartalmazza.
-   **Frontend:** Egy React alkalmazás, amely a felhasználói felületet biztosítja.

### Hogyan tesztelj?

A backend tesztek a `pytest` használatával futtathatók a `backend/tests` mappából. A `docker-compose.yml` elindítja a teljes rendszert.
