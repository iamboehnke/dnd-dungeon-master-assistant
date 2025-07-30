# dnd-dungeon-master-assistant
# D&D Dungeon Master Assistant with AI

A desktop app to help Dungeon Masters quickly generate NPCs, balanced encounters, and even AI‑enhanced personalities and traits. Built in Python with a Tkinter GUI and an extendable AI backend (Markov name generator + GPT‑2 mini for traits).

---

## Features

- **NPC Generator**  
  - Toggle between Markov‑chain names or custom lists  
  - Race‑specific or random  
  - AI‑generated personality traits (via mini GPT‑2)  
  - Bulk name & trait training

- **Encounter Builder**  
  - Balanced monster encounters by party level

- **Training Tab**  
  - Add single or bulk names (per race)  
  - Add custom traits

- **AI Settings**  
  - Enable/disable AI‑generated traits  
  - Reload name & trait models on the fly

- **Statistics**  
  - View total names trained, races supported, trait counts, etc.

---

## Repository Structure
```
dnd-dungeon-master-assistant/
│
├─ data/
│ └─ npc_names.csv        #Name – race pairs for Markov training
│
├─ src/
│ └─ app.py               #Tkinter GUI entrypoint
│ └─ generator.py         #Core logic: NPC, encounters, training
│ └─ markov_model.py      #Name generator
│ └─ trait_generator.py   #AI trait logic
│
├─ launcher.py            #(optional) builds .exe or wraps another UI
├─ requirements.txt       #Python dependencies
├─ launcher.spec          #PyInstaller spec for .exe bundling
└─ README.md
```

---

## Installation & Run from Source

1. **Clone the repo**  
  git clone https://github.com/YOUR_USERNAME/dnd-dungeon-master-assistant.git
  cd dnd-dungeon-master-assistant

2. **Create & activate a virtualenv (or Conda env):**
  python -m venv .venv
  .venv\Scripts\activate #Windows PowerShell or macOS/Linux: source .venv/bin/activate 

4. **Install dependencies**
  pip install -r requirements.txt

5. **Run the app**
  python src/app.py

