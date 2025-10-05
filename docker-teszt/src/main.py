# main.py
print("Helló a Python szkriptből a konténeren belül!")

try:
    with open("/app/data/uzenet.txt", "r", encoding="utf-8") as f:
        uzenet = f.read()
        print(f"Az uzenet.txt tartalma: '{uzenet}'")
    print("Sikeresen olvastuk a külső fájlt!")
except FileNotFoundError:
    print("HIBA: Az uzenet.txt fájl nem található a /app/data/ helyen!")
except Exception as e:
    print(f"HIBA: Ismeretlen hiba történt: {e}")
