import pytest
from src.generator import generate_npc, generate_encounter
from src.markov_model import MarkovNameGenerator

def test_npc_generator():
    npc = generate_npc()
    assert "name" in npc and "race" in npc and "trait" in npc

def test_encounter_generator():
    encounter = generate_encounter(2)
    assert "name" in encounter and "monsters" in encounter and "difficulty" in encounter

def test_markov_model():
    # Test Markov name generation
    generator = MarkovNameGenerator(state_size=2)
    names = ["Eltharion", "Thorin", "Lyra", "Morgath", "Kaelen"]
    generator.train(names)
    
    for _ in range(5):
        new_name = generator.generate_name()
        assert isinstance(new_name, str)
        assert len(new_name) > 2