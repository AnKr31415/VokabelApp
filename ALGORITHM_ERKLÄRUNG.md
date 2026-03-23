# Intelligentes Vokabel-Lern-Algorithmus

## Wie es funktioniert

Das neue System fragt Vokabeln nicht mehr zufällig, sondern nach einem intelligenten Algorithmus basierend auf:

### 1. **Schwierigkeitsbewertung** (Sie bestimmen!)
- Klicken Sie auf eine Vokabel in der Liste
- Wählen Sie eine Schwierigkeit (1-5):
  - **1** = Kann ich kaum → wird **sehr häufig** gefragt
  - **2** = Schwer → wird häufig gefragt
  - **3** = Mittel → mittelhäufig
  - **4** = Leicht → seltener gefragt
  - **5** = Kann ich sehr gut → wird **fast nicht** gefragt

### 2. **Ihre Performance**
Das System verfolgt automatisch:
- ✓ **Richtige Antworten**: Vokabeln, die Sie kennen, werden weniger häufig gefragt
- ✗ **Falsche Antworten**: Vokabeln, die Sie nicht wissen, werden **immer häufiger** gefragt

### 3. **Zeitliche Abstände** (Spaced Repetition)
- **Richtig beantwortet** → nächste Wiederholung in **24 Stunden**
- **Falsch beantwortet** → nächste Wiederholung in **5 Minuten** (sofort üben!)

## Die Prioritätsformel

Die App berechnet einen Prioritätsscore für jede Vokabel:

```
Priorität = (6 - Schwierigkeit) × 1,5 + 
            (Fehler × 2) - 
            (Erfolge × 0,5) +
            Zeit-Bonus
```

**Was das bedeutet:**
- Niedrige Schwierigkeit → höhere Priorität (häufiger gefragt)
- Viele Fehler → höhere Priorität  
- Viele Erfolge → niedrigere Priorität
- Lange nicht gefragt → Bonus-Punkte

## Beispiele

| Vokabel | Schwierigkeit | Erfolge | Fehler | Häufigkeit |
|---------|---------------|---------|--------|-----------|
| Fenster | 1 (Kaum) | 2 | 8 | ⭐⭐⭐⭐⭐ Sehr oft |
| Wasser | 3 (Mittel) | 5 | 3 | ⭐⭐⭐ Normal |
| Haus | 5 (Sehr gut) | 12 | 0 | ⭐ Selten |

## Training nutzen

**Flashcard-Modus:**
- Zum Wort swipen:
  - **Rechts** = Ich kenne es ✓
  - **Links** = Ich kenne es nicht ✗

**Eingabe-Modus:**
- Das deutsche Wort wird gezeigt
- Sie geben die englische Übersetzung ein
- System prüft automatisch & speichert das Ergebnis

=> Je häufiger Sie trainieren, desto intelligenter wird die Auswahl!
