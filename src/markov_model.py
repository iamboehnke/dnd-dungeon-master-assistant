import random
from collections import defaultdict
import json
import os
from pathlib import Path

class MarkovNameGenerator:
    def __init__(self, state_size=2):
        self.model = defaultdict(list)
        self.state_size = state_size
        self.training_data = []
        self.race_models = {}  # Separate models per race
        self.training_stats = {}  # Track training statistics
    
    def train(self, name_list, race=None):
        """Train the Markov model on a list of names for a specific race"""
        if not name_list:
            return
            
        # Initialize race model if needed
        if race and race not in self.race_models:
            self.race_models[race] = defaultdict(list)
            self.training_stats[race] = 0
        
        model = self.race_models[race] if race else self.model
        
        names_added = 0
        for name in name_list:
            if not name or not isinstance(name, str):
                continue
                
            name = name.strip()
            if not name:
                continue
            
            # Track training data for saving/reloading
            training_entry = f"{race}:{name}" if race else name
            if training_entry not in self.training_data:
                self.training_data.append(training_entry)
                names_added += 1
            
            # Add start and end markers
            name_processed = '^' * self.state_size + name.lower() + '$'
            
            # Build transitions
            for i in range(len(name_processed) - self.state_size):
                current_state = name_processed[i:i+self.state_size]
                next_char = name_processed[i+self.state_size]
                model[current_state].append(next_char)
        
        # Update training statistics
        if race:
            self.training_stats[race] = self.training_stats.get(race, 0) + names_added
        
        return names_added
    
    def generate_name(self, race=None, starting_letters="", max_length=12, min_length=2):
        """Generate a new name with optional race and starting letters"""
        model = self.race_models.get(race, self.model) if race else self.model
        
        # If no model available, fall back to general model
        if not model and race and self.model:
            model = self.model
        
        if not model:
            return "Unknown"  # Fallback if no model trained
        
        name = starting_letters.lower()
        max_attempts = 50  # Prevent infinite loops
        
        for attempt in range(max_attempts):
            current_name = name
            
            # Handle starting state
            if current_name:
                # Pad with start markers if needed
                state = ('^' * max(0, self.state_size - len(current_name))) + current_name
                state = state[-self.state_size:]
            else:
                state = '^' * self.state_size
                current_name = ""
            
            # Generate name
            while len(current_name) < max_length:
                if state not in model or not model[state]:
                    break
                    
                next_char = random.choice(model[state])
                if next_char == '$':
                    break
                    
                current_name += next_char
                state = state[1:] + next_char  # shift window forward
            
            # Check if name meets requirements
            if len(current_name) >= min_length:
                return current_name.capitalize()
            
            # If name too short, try again
            name = starting_letters.lower()
        
        # Fallback: return starting letters + random extension
        if starting_letters:
            return (starting_letters + "ara").capitalize()
        return "Unnamed"
    
    def generate_multiple_names(self, count=10, race=None, starting_letters="", unique_only=True):
        """Generate multiple names at once"""
        names = []
        seen = set() if unique_only else None
        max_attempts = count * 10  # Prevent infinite loops
        
        attempts = 0
        while len(names) < count and attempts < max_attempts:
            name = self.generate_name(race=race, starting_letters=starting_letters)
            
            if unique_only:
                if name not in seen:
                    names.append(name)
                    seen.add(name)
            else:
                names.append(name)
            
            attempts += 1
        
        return names
    
    def save_model(self, file_path):
        """Save model and training data to a file"""
        model_data = {
            "state_size": self.state_size,
            "model": {k: v for k, v in self.model.items()},
            "race_models": {
                race: {k: v for k, v in model.items()} 
                for race, model in self.race_models.items()
            },
            "training_data": self.training_data,
            "training_stats": self.training_stats
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
    
    def load_model(self, file_path):
        """Load model from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        self.state_size = model_data.get("state_size", 2)
        
        # Load general model
        general_model = model_data.get("model", {})
        self.model = defaultdict(list)
        for k, v in general_model.items():
            self.model[k] = v
        
        # Load race-specific models
        race_models = model_data.get("race_models", {})
        self.race_models = {}
        for race, model in race_models.items():
            self.race_models[race] = defaultdict(list)
            for k, v in model.items():
                self.race_models[race][k] = v
        
        self.training_data = model_data.get("training_data", [])
        self.training_stats = model_data.get("training_stats", {})
    
    def get_trained_races(self):
        """Get list of races with trained models"""
        return list(self.race_models.keys())
    
    def get_model_info(self):
        """Get detailed information about the model"""
        info = {
            "state_size": self.state_size,
            "total_training_names": len(self.training_data),
            "general_model_states": len(self.model),
            "race_models": {}
        }
        
        for race in self.race_models:
            info["race_models"][race] = {
                "states": len(self.race_models[race]),
                "training_names": self.training_stats.get(race, 0)
            }
        
        return info
    
    def clear_model(self):
        """Clear all training data and reset model"""
        self.model = defaultdict(list)
        self.race_models = {}
        self.training_data = []
        self.training_stats = {}
    
    def remove_race_model(self, race):
        """Remove a specific race model"""
        if race in self.race_models:
            del self.race_models[race]
            # Remove from training data
            self.training_data = [
                entry for entry in self.training_data 
                if not entry.startswith(f"{race}:")
            ]
            if race in self.training_stats:
                del self.training_stats[race]
            return True
        return False
    
    def get_sample_names(self, race=None, count=5):
        """Get sample names that the model was trained on"""
        if race:
            prefix = f"{race}:"
            race_names = [
                entry.split(":", 1)[1] for entry in self.training_data 
                if entry.startswith(prefix)
            ]
            return random.sample(race_names, min(count, len(race_names)))
        else:
            general_names = [
                entry for entry in self.training_data 
                if ":" not in entry
            ]
            return random.sample(general_names, min(count, len(general_names)))