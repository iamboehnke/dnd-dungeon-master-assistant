import random
import csv
import pandas as pd
import json
from pathlib import Path
from .markov_model import MarkovNameGenerator
from .model_manager import load_model, save_model
import os

# GPT-2 imports (install with: pip install transformers torch)
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
    GPT2_AVAILABLE = True
except ImportError:
    GPT2_AVAILABLE = False
    print("GPT-2 not available. Install with: pip install transformers torch")

# --- Data Loading Helpers ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Load data
npc_names_df = pd.read_csv(DATA_DIR / "npc_names.csv")
traits_df = pd.read_csv(DATA_DIR / "traits.csv")

with open(DATA_DIR / "encounters.json") as f:
    encounters = json.load(f)

# --- Enhanced Trait Generator with GPT-2 ---
class TraitGenerator:
    """Enhanced trait generator with GPT-2 support for dynamic trait creation"""
    
    def __init__(self, use_gpt2=True, model_name="gpt2"):
        self.traits = traits_df['trait'].tolist()
        self.use_gpt2 = use_gpt2 and GPT2_AVAILABLE
        self.gpt2_model = None
        self.gpt2_tokenizer = None
        self.generator_pipeline = None
        
        # Load GPT-2 model if available and requested
        if self.use_gpt2:
            self._load_gpt2_model(model_name)
    
    def _load_gpt2_model(self, model_name):
        """Load GPT-2 model and tokenizer"""
        try:
            print(f"Loading GPT-2 model: {model_name}...")
            # Use pipeline for easier text generation
            self.generator_pipeline = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                device=-1,  # Use CPU (-1) or GPU (0)
                pad_token_id=50256  # GPT-2's EOS token
            )
            print("GPT-2 model loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load GPT-2 model: {e}")
            self.use_gpt2 = False
    
    def generate_trait(self, race=None, context=None, use_ai=None, creativity=0.8):
        """
        Generate a trait using GPT-2 or fallback to random selection
        
        Args:
            race: Character race for context
            context: Additional context (e.g., "mysterious", "friendly")
            use_ai: Override default AI usage
            creativity: Temperature for GPT-2 generation (0.1-1.0)
        """
        # Determine whether to use AI
        should_use_ai = use_ai if use_ai is not None else self.use_gpt2
        
        if should_use_ai and self.generator_pipeline:
            return self._generate_gpt2_trait(race, context, creativity)
        else:
            return self._generate_random_trait()
    
    def _generate_gpt2_trait(self, race, context, creativity):
        """Generate trait using GPT-2"""
        try:
            # Construct prompt based on available context
            prompt = self._build_trait_prompt(race, context)
            
            # Generate text with GPT-2
            response = self.generator_pipeline(
                prompt,
                max_length=len(prompt.split()) + 5,  
                num_return_sequences=1,
                temperature=creativity,
                truncation=True,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=50256
            )
            
            # Extract and clean the generated trait
            generated_text = response[0]['generated_text']
            trait = self._extract_trait_from_response(generated_text, prompt)
            
            # Validate and clean the trait
            trait = self._clean_trait(trait)
            
            # Fallback to random if generation failed
            if not trait or len(trait) < 5:
                return self._generate_random_trait()
            
            return trait
            
        except Exception as e:
            print(f"GPT-2 generation failed: {e}")
            return self._generate_random_trait()
    
    def _build_trait_prompt(self, race, context):
        """Build a prompt for GPT-2 trait generation"""
        prompts = []
        
        if race and context:
            prompts = [
                f"This {race.lower()} character is {context.lower()} and has a unique trait:",
                f"A {context.lower()} {race.lower()} NPC with the trait:",
                f"Character trait for a {context.lower()} {race.lower()}:",
            ]
        elif race:
            prompts = [
                f"This {race.lower()} character has a distinctive trait:",
                f"A {race.lower()} NPC with the personality trait:",
                f"Character quirk for a {race.lower()}:",
            ]
        elif context:
            prompts = [
                f"This {context.lower()} character has the trait:",
                f"A {context.lower()} NPC with the quirk:",
                f"Personality trait for a {context.lower()} character:",
            ]
        else:
            prompts = [
                "This D&D character has a unique trait:",
                "NPC personality quirk:",
                "Character trait:",
            ]
        
        return random.choice(prompts)
    
    def _extract_trait_from_response(self, generated_text, prompt):
        """Extract the trait from GPT-2 response"""
        # Remove the prompt from the response
        trait = generated_text[len(prompt):].strip()
        
        # Take only the first sentence/phrase
        import re
        sentences = re.split(r'[.!?]\s+', trait)
        if sentences:
            trait = sentences[0].strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            "they ", "he ", "she ", "the character ", "this character ",
            "always ", "often ", "sometimes ", "never "
        ]
        
        for prefix in prefixes_to_remove:
            if trait.lower().startswith(prefix):
                trait = trait[len(prefix):].strip()
        
        return trait
    
    def _clean_trait(self, trait):
        """Clean and validate the generated trait"""
        if not trait:
            return ""
        
        # Capitalize first letter
        trait = trait[0].upper() + trait[1:] if len(trait) > 1 else trait.upper()
        
        # Remove incomplete sentences
        if trait.endswith(',') or trait.endswith(' and') or trait.endswith(' or'):
            trait = trait.rstrip(',').rstrip(' and').rstrip(' or')
        
        # Ensure reasonable length
        if len(trait) > 100:
            trait = trait[:97] + "..."
        
        # Add period if missing and doesn't end with punctuation
        if trait and not trait[-1] in '.!?':
            trait += "."
        
        return trait
    
    def _generate_random_trait(self):
        """Fallback to random trait selection"""
        return random.choice(self.traits)
    
    def add_custom_trait(self, trait):
        """Add a custom trait to the pool"""
        if trait not in self.traits:
            self.traits.append(trait)
            # Also add to CSV for persistence
            new_trait_df = pd.DataFrame({"trait": [trait]})
            new_trait_df.to_csv(DATA_DIR / "traits.csv", mode='a', header=False, index=False, quoting=csv.QUOTE_NONE, line_terminator='\n')
            return f"Added trait: {trait}"
        return "Trait already exists"
    
    def generate_multiple_traits(self, count=5, **kwargs):
        """Generate multiple traits at once"""
        traits = []
        for _ in range(count):
            trait = self.generate_trait(**kwargs)
            if trait not in traits:  # Avoid duplicates
                traits.append(trait)
        return traits
    
    def get_trait_suggestions(self, race=None, context=None, count=3):
        """Get multiple trait suggestions for user to choose from"""
        suggestions = []
        
        # Generate AI traits if available
        if self.use_gpt2:
            for creativity in [0.6, 0.8, 1.0]:  # Different creativity levels
                trait = self.generate_trait(race, context, use_ai=True, creativity=creativity)
                if trait and trait not in suggestions:
                    suggestions.append(trait)
                if len(suggestions) >= count:
                    break
        
        # Fill remaining with random traits if needed
        while len(suggestions) < count:
            trait = self._generate_random_trait()
            if trait not in suggestions:
                suggestions.append(trait)
        
        return suggestions[:count]
    
    def is_gpt2_available(self):
        """Check if GPT-2 is available and loaded"""
        return self.use_gpt2 and self.generator_pipeline is not None
    
    def toggle_gpt2(self, enabled):
        """Enable or disable GPT-2 usage"""
        if enabled and GPT2_AVAILABLE and not self.generator_pipeline:
            self._load_gpt2_model("gpt2")
        self.use_gpt2 = enabled and self.generator_pipeline is not None
        return self.use_gpt2

def load_and_train_model():
    """Load existing model or create and train new one"""
    # Try to load existing model first
    name_generator, load_message = load_model()
    print(load_message)
    
    # If no existing model or we want to retrain, train on current data
    if not name_generator.training_data:  # No previous training data
        print("Training new model...")
        
        # Train general model
        name_generator.train(npc_names_df['name'].tolist())
        
        # Train race-specific models
        for race in npc_names_df['race'].unique():
            race_names = npc_names_df[npc_names_df['race'] == race]['name'].tolist()
            if race_names:  # Only train if there are names for this race
                name_generator.train(race_names, race=race)
        
        # Save the trained model
        save_message = save_model(name_generator)
        print(save_message)
    
    return name_generator

# Initialize models
name_generator = load_and_train_model()
trait_generator = TraitGenerator(use_gpt2=True)  # Enable GPT-2 by default

# Get unique races for random assignment
races = npc_names_df['race'].unique().tolist()

# --- Enhanced NPC Generator ---
def generate_npc(use_markov=True, race_specific=True, starting_letters="", 
                custom_race=None, trait_context=None, use_ai_traits=None):
    """Generate a random NPC with name, race, and AI-generated trait"""
    
    # Determine race
    if custom_race and custom_race in races:
        race = custom_race
    else:
        race = random.choice(races)
    
    # Generate name
    if use_markov:
        if race_specific and race in name_generator.get_trained_races():
            name = name_generator.generate_name(
                race=race, 
                starting_letters=starting_letters
            )
        else:
            name = name_generator.generate_name(
                starting_letters=starting_letters
            )
    else:
        # Use existing name from dataset
        race_names = npc_names_df[npc_names_df['race'] == race]
        if race_names.empty:
            npc = npc_names_df.sample(1).iloc[0]
        else:
            npc = race_names.sample(1).iloc[0]
        name = npc["name"]
        race = npc["race"]
    
    # Generate trait with AI
    trait = trait_generator.generate_trait(
        race=race, 
        context=trait_context,
        use_ai=use_ai_traits
    )
    
    return {
        "name": name,
        "race": race,
        "trait": trait
    }

def get_trait_suggestions(race=None, context=None, count=3):
    """Get multiple trait suggestions"""
    return trait_generator.get_trait_suggestions(race, context, count)

def toggle_ai_traits(enabled):
    """Enable/disable AI trait generation"""
    return trait_generator.toggle_gpt2(enabled)

def is_ai_traits_available():
    """Check if AI trait generation is available"""
    return trait_generator.is_gpt2_available()

def add_custom_trait(trait):
    """Add a custom trait to the trait generator"""
    return trait_generator.add_custom_trait(trait)

def add_names_to_model(names, race=None):
    """Add new names to the model and retrain"""
    if isinstance(names, str):
        names = [names]
    
    # Train the model with new names
    name_generator.train(names, race=race)
    
    # Add to CSV for persistence
    race_values = [race] * len(names) if race else ['Unknown'] * len(names)
    new_df = pd.DataFrame({"name": names, "race": race_values})
    new_df.to_csv(DATA_DIR / "npc_names.csv", mode='a', header=False, index=False)
    
    # Save updated model
    save_model(name_generator)
    
    return f"Added {len(names)} names to model!"

def get_available_races():
    """Get list of all available races"""
    trained_races = name_generator.get_trained_races()
    all_races = set(races + trained_races)
    return sorted(list(all_races))

def get_model_stats():
    """Get statistics about the trained model"""
    stats = {
        "total_names_trained": len(name_generator.training_data),
        "races_with_models": len(name_generator.get_trained_races()),
        "available_races": get_available_races(),
        "total_traits": len(trait_generator.traits),
        "ai_traits_available": trait_generator.is_gpt2_available()
    }
    return stats

# --- Rest of functions remain the same ---
def generate_encounter(level: int):
    """Generate a random encounter based on party level (1-20)."""
    if level <= 3:
        pool = encounters["low_level"]
    elif level <= 10:
        pool = encounters["mid_level"]
    else:
        pool = encounters["high_level"]

    return random.choice(pool)

def generate_multiple_npcs(count=5, **kwargs):
    """Generate multiple NPCs at once"""
    return [generate_npc(**kwargs) for _ in range(count)]

def generate_npc_party(size=4, **kwargs):
    """Generate a party of NPCs with diverse races"""
    party = []
    available_races = get_available_races()
    
    for i in range(size):
        # Try to ensure race diversity in the party
        if i < len(available_races):
            race = available_races[i]
        else:
            race = random.choice(available_races)
        
        npc = generate_npc(custom_race=race, **kwargs)
        party.append(npc)
    
    return party

# Initialize and display model stats on import
if __name__ == "__main__":
    stats = get_model_stats()
    print(f"Model loaded with {stats['total_names_trained']} names across {stats['races_with_models']} races")
    print(f"Available races: {', '.join(stats['available_races'])}")
    print(f"Available traits: {stats['total_traits']}")
    print(f"AI trait generation: {'Enabled' if stats['ai_traits_available'] else 'Disabled'}")