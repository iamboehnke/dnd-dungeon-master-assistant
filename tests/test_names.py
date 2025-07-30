from src.markov_model import MarkovNameGenerator

fantasy_names = [
    "Thorin", "Goro", "Lorin", "Galwen", "Elandril", "Arwen", "Elrond", "Faramir", 
    "Legolas", "Gandalf", "Boromir", "Celeborn", "Glorfindel", "Melian", "Elendil", 
    "Isildur", "Durin", "Dain", "Balin", "Balinor", "Thranduil", "Maeglin", "Nimrodel",
    "Tauriel", "Silmarien", "Vanyar", "Finrod", "Eärendil", "Melkor", "Sauron", "Radagast",
    "Morgoth", "Glorfindel", "Celeborn", "Galadriel", "Elwing", "Círdan", "Anarion",
    "Gil-galad", "Aegnor", "Haldir", "Ecthelion", "Thingol", "Feanor", "Turin", "Noldor"
]

model = MarkovNameGenerator()
model.train(fantasy_names)

print("✨ Generated Fantasy Names ✨")
for _ in range(10):
    print("-", model.generate_name())