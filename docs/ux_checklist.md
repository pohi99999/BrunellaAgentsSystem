# UX & Lighthouse ellenőrző lista

1. **Hero szekció**
   - Részecske / háttér animáció akadás nélkül fut (60fps körül).
   - Elsődleges CTA 44x44px érintési méret.

2. **Navigáció**
   - MotionNavbar minden breakpointon jól olvasható.
   - Billentyűzettel is bejárható (Tab sorrend).

3. **Chat + űrlap**
   - Placeholder és hibaüzenetek magyarul, kontraszt > 4.5:1.
   - Enter megnyomása küldi az üzenetet, ESC megszakítja a futást.

4. **Általános hozzáférhetőség**
   - `npm run lint` + `npm run test:e2e` hibamentes.
   - Lighthouse Accessibility >= 0.9 (CI ezt enforce-olja).

5. **Teljesítmény**
   - `npm run audit:ux` futtatása minden vizuális változtatás után.
   - Render-blocking assetek száma minimalizálva (vite split chunks).
