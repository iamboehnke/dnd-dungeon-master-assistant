from pathlib import Path
from .markov_model import MarkovNameGenerator
import os

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "name_generator.json"

def ensure_models_directory():
    """Ensure the models directory exists"""
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

def save_model(generator):
    """Save the trained model to file"""
    ensure_models_directory()
    
    try:
        generator.save_model(MODEL_PATH)
        return f"Model saved to {MODEL_PATH}"
    except Exception as e:
        return f"Error saving model: {str(e)}"

def load_model():
    """Load a trained model from file"""
    generator = MarkovNameGenerator()
    
    if MODEL_PATH.exists():
        try:
            generator.load_model(MODEL_PATH)
            return generator, f"Model loaded from {MODEL_PATH}"
        except Exception as e:
            return generator, f"Error loading model: {str(e)} - using new instance"
    else:
        return generator, "No saved model found - using new instance"

def backup_model(backup_name=None):
    """Create a backup of the current model"""
    if not MODEL_PATH.exists():
        return "No model to backup"
    
    ensure_models_directory()
    
    if backup_name is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"name_generator_backup_{timestamp}.json"
    
    backup_path = MODELS_DIR / backup_name
    
    try:
        import shutil
        shutil.copy2(MODEL_PATH, backup_path)
        return f"Model backed up to {backup_path}"
    except Exception as e:
        return f"Error creating backup: {str(e)}"

def list_backups():
    """List all available model backups"""
    if not MODELS_DIR.exists():
        return []
    
    backups = []
    for file in MODELS_DIR.iterdir():
        if file.name.startswith("name_generator_backup_") and file.suffix == ".json":
            backups.append(file.name)
    
    return sorted(backups, reverse=True)  # Most recent first

def restore_backup(backup_name):
    """Restore a model from backup"""
    backup_path = MODELS_DIR / backup_name
    
    if not backup_path.exists():
        return f"Backup {backup_name} not found"
    
    try:
        import shutil
        # Backup current model first
        if MODEL_PATH.exists():
            backup_model("pre_restore_backup.json")
        
        shutil.copy2(backup_path, MODEL_PATH)
        return f"Model restored from {backup_name}"
    except Exception as e:
        return f"Error restoring backup: {str(e)}"