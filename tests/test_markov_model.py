import pytest
import pandas as pd
from src.markov_model import MarkovNameGenerator

def test_markov_training_and_generation():
    path_to_csv = "data/npc_names.csv"
    df = pd.read_csv(path_to_csv)
    names = df['name'].tolist()

    model = MarkovNameGenerator()
    model.train(names)

    generated_name = model.generate_name(min_length=4, max_length=14)
    print(f"Generated name: {generated_name!r}")  # debug print

    assert generated_name is not None, "generate_name returned None"
    assert 4 <= len(generated_name) <= 14
    assert generated_name[0].isupper()
    assert generated_name.isalpha() or "-" in generated_name
if __name__ == "__main__":
    pytest.main()