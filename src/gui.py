import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from src.generator import (
    generate_npc, generate_encounter, generate_multiple_npcs, 
    generate_npc_party, add_names_to_model, add_custom_trait,
    get_available_races, get_model_stats, get_trait_suggestions,
    toggle_ai_traits, is_ai_traits_available,
    load_and_train_model, TraitGenerator
)
import datetime

class DnDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Dungeon Master Assistant with AI")
        self.root.geometry("750x650")
        self.root.resizable(True, True)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize variables
        self.use_markov = tk.BooleanVar(value=True)
        self.race_specific = tk.BooleanVar(value=True)
        self.starting_letters = tk.StringVar(value="")
        self.selected_race = tk.StringVar(value="Random")
        self.npc_count = tk.IntVar(value=1)
        
        # AI Trait variables
        self.use_ai_traits = tk.BooleanVar(value=is_ai_traits_available())
        self.trait_context = tk.StringVar(value="")
        
        # Get available races for dropdowns
        self.available_races = ["Random"] + get_available_races()
        
        # Create models
        global name_generator, trait_generator
        name_generator = load_and_train_model()
        trait_generator = TraitGenerator(use_gpt2=self.use_ai_traits.get())
        
        # Create tabs
        self.create_npc_tab()
        self.create_encounter_tab()
        self.create_training_tab()
        self.create_ai_settings_tab()
        self.create_stats_tab()
        
        # Footer
        footer_frame = ttk.Frame(root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # AI status indicator
        ai_status = "🤖 AI Traits: ON" if self.use_ai_traits.get() else "AI Traits: OFF"
        self.ai_status_label = ttk.Label(footer_frame, text=ai_status)
        self.ai_status_label.pack(side=tk.LEFT)
        
        ttk.Label(footer_frame, text="Made with LOVE for DMs").pack(side=tk.LEFT, padx=(20, 0))
        
        # Stats button in footer
        ttk.Button(
            footer_frame, 
            text="Refresh Stats", 
            command=self.refresh_stats
        ).pack(side=tk.RIGHT)
    
    def create_npc_tab(self):
        # NPC Generator Tab
        self.npc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.npc_frame, text="NPC Generator")
        
        ttk.Label(self.npc_frame, text="Generate Unique NPCs with AI", font=("Arial", 14)).pack(pady=10)
        
        # Main controls frame
        controls_frame = ttk.LabelFrame(self.npc_frame, text="Generation Options", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Row 1: Basic toggles
        row1 = ttk.Frame(controls_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(
            row1,
            text="Use AI Name Generator",
            variable=self.use_markov
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            row1,
            text="Race-Specific Names",
            variable=self.race_specific
        ).pack(side=tk.LEFT, padx=15)
        
        ttk.Checkbutton(
            row1,
            text="AI-Generated Traits",
            variable=self.use_ai_traits,
            command=self.update_ai_status
        ).pack(side=tk.LEFT, padx=15)
        
        # Row 2: Starting letters and race selection
        row2 = ttk.Frame(controls_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Start with:").pack(side=tk.LEFT)
        ttk.Entry(
            row2, 
            width=8,
            textvariable=self.starting_letters
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Race:").pack(side=tk.LEFT, padx=(20, 5))
        race_combo = ttk.Combobox(
            row2, 
            textvariable=self.selected_race, 
            values=self.available_races,
            width=12,
            state="readonly"
        )
        race_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Count:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(
            row2,
            from_=1,
            to=10,
            width=5,
            textvariable=self.npc_count
        ).pack(side=tk.LEFT, padx=5)
        
        # Row 3: AI Trait context
        row3 = ttk.Frame(controls_frame)
        row3.pack(fill=tk.X, pady=5)
        
        ttk.Label(row3, text="Trait Context:").pack(side=tk.LEFT)
        context_entry = ttk.Entry(
            row3, 
            width=20,
            textvariable=self.trait_context
        )
        context_entry.pack(side=tk.LEFT, padx=5)
        
        # Help text for context
        ttk.Label(
            row3, 
            text="(e.g., 'mysterious', 'friendly', 'scholarly')",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=5)
        
        # Generation buttons frame
        buttons_frame = ttk.Frame(self.npc_frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(
            buttons_frame, 
            text="Generate NPC(s)", 
            command=self.generate_npcs,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="Generate Party (4)", 
            command=self.generate_party
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="Get Trait Ideas", 
            command=self.show_trait_suggestions
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="Clear Results", 
            command=self.clear_npc_results
        ).pack(side=tk.LEFT, padx=5)
        
        # NPC Display
        self.npc_result = scrolledtext.ScrolledText(
            self.npc_frame, 
            height=12, 
            width=70,
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        self.npc_result.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)
        self.npc_result.config(state=tk.DISABLED)
        
    
    def create_encounter_tab(self):
        # Encounter Generator Tab
        self.encounter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.encounter_frame, text="Encounter Builder")
        
        ttk.Label(self.encounter_frame, text="Build Balanced Encounters", font=("Arial", 14)).pack(pady=10)
        
        # Level Selector
        level_frame = ttk.Frame(self.encounter_frame)
        level_frame.pack(pady=5)
        ttk.Label(level_frame, text="Party Level:").pack(side=tk.LEFT)
        
        self.level_var = tk.IntVar(value=5)
        ttk.Spinbox(
            level_frame, 
            from_=1, 
            to=20, 
            width=5,
            textvariable=self.level_var
        ).pack(side=tk.LEFT, padx=5)
        
        # Generate Button
        ttk.Button(
            self.encounter_frame, 
            text="Create Encounter", 
            command=self.generate_encounter,
            style="Accent.TButton"
        ).pack(pady=5)
        
        # Encounter Display
        self.encounter_result = scrolledtext.ScrolledText(
            self.encounter_frame, 
            height=12, 
            width=70,
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        self.encounter_result.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)
        self.encounter_result.config(state=tk.DISABLED)
    
    def create_training_tab(self):
        # Training Tab
        self.training_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.training_frame, text="Training")
        
        ttk.Label(self.training_frame, text="Improve the AI Models", font=("Arial", 14)).pack(pady=10)
        
        # Name Training Section
        name_section = ttk.LabelFrame(self.training_frame, text="Add New Names", padding=10)
        name_section.pack(fill=tk.X, padx=10, pady=5)
        
        name_row1 = ttk.Frame(name_section)
        name_row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(name_row1, text="Name:").pack(side=tk.LEFT)
        self.new_name = tk.StringVar()
        name_entry = ttk.Entry(name_row1, textvariable=self.new_name, width=20)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(name_row1, text="Race:").pack(side=tk.LEFT, padx=(20, 5))
        self.new_race = tk.StringVar()
        race_combo = ttk.Combobox(
            name_row1, 
            textvariable=self.new_race, 
            values=self.available_races[1:] + ["Custom"],  # Exclude "Random"
            width=12
        )
        race_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            name_row1, 
            text="Add Name", 
            command=self.train_new_name
        ).pack(side=tk.LEFT, padx=10)
        
        # Bulk name training
        name_row2 = ttk.Frame(name_section)
        name_row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_row2, text="Bulk Names (one per line):").pack(anchor=tk.W)
        self.bulk_names = tk.Text(name_row2, height=4, width=40)
        self.bulk_names.pack(fill=tk.X, pady=2)
        
        bulk_controls = ttk.Frame(name_row2)
        bulk_controls.pack(fill=tk.X, pady=2)
        
        ttk.Label(bulk_controls, text="Race for all:").pack(side=tk.LEFT)
        self.bulk_race = tk.StringVar()
        ttk.Combobox(
            bulk_controls,
            textvariable=self.bulk_race,
            values=self.available_races[1:] + ["Custom"],
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bulk_controls,
            text="Add All Names",
            command=self.train_bulk_names
        ).pack(side=tk.LEFT, padx=10)
        
        # Trait Training Section
        trait_section = ttk.LabelFrame(self.training_frame, text="Add New Traits", padding=10)
        trait_section.pack(fill=tk.X, padx=10, pady=5)
        
        trait_row = ttk.Frame(trait_section)
        trait_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(trait_row, text="New Trait:").pack(side=tk.LEFT)
        self.new_trait = tk.StringVar()
        ttk.Entry(trait_row, textvariable=self.new_trait, width=50).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            trait_row, 
            text="Add Trait", 
            command=self.train_new_trait
        ).pack(side=tk.LEFT, padx=10)
        
        # Training Log
        ttk.Label(self.training_frame, text="Training Log:", font=("Arial", 11)).pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.training_log = scrolledtext.ScrolledText(
            self.training_frame,
            height=6,
            width=70,
            font=("Consolas", 10)
        )
        self.training_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.training_log.config(state=tk.DISABLED)
    
    def create_ai_settings_tab(self):
            # AI Settings Tab (continued)
            self.ai_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.ai_frame, text="AI Settings")

            ttk.Label(self.ai_frame, text="AI Configuration", font=("Arial", 14)).pack(pady=10)

            # AI Status Section
            status_section = ttk.LabelFrame(self.ai_frame, text="AI Status", padding=10)
            status_section.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(status_section, text="Toggle AI-generated traits on or off:").pack(side=tk.LEFT, padx=5)
            ttk.Checkbutton(
                status_section,
                text="Enable AI Traits",
                variable=self.use_ai_traits,
                command=self.toggle_ai_traits
            ).pack(side=tk.LEFT, padx=5)

            # Reset Models Section
            reset_section = ttk.LabelFrame(self.ai_frame, text="Model Management", padding=10)
            reset_section.pack(fill=tk.X, padx=10, pady=5)

            ttk.Button(
                reset_section,
                text="Reload Models",
                command=self.reload_models,
                style="Accent.TButton"
            ).pack(padx=5, pady=5)

    def create_stats_tab(self):
        # Statistics Tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")

        ttk.Label(self.stats_frame, text="Model Statistics", font=("Arial", 14)).pack(pady=10)

        self.stats_display = scrolledtext.ScrolledText(
            self.stats_frame,
            height=15,
            width=70,
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.stats_display.config(state=tk.DISABLED)

        self.refresh_stats()

    # --- Command callbacks and helpers ---

    def update_ai_status(self):
        status = "AI Traits: ON" if self.use_ai_traits.get() else "AI Traits: OFF"
        self.ai_status_label.config(text=status)

    def toggle_ai_traits(self):
        enabled = self.use_ai_traits.get()
        toggle_ai_traits(enabled)
        self.update_ai_status()

    def reload_models(self):
        global name_generator, trait_generator
        name_generator = load_and_train_model()
        trait_generator = TraitGenerator(use_gpt2=self.use_ai_traits.get())
        messagebox.showinfo("Models Reloaded", "Name and trait models have been reloaded.")

    def generate_npcs(self):
        count = self.npc_count.get()
        race = None if self.selected_race.get() == "Random" else self.selected_race.get()
        context = self.trait_context.get() or None

        if count == 1:
            npc = generate_npc(
                use_markov=self.use_markov.get(),
                race_specific=self.race_specific.get(),
                starting_letters=self.starting_letters.get(),
                custom_race=race,
                trait_context=context,
                use_ai_traits=self.use_ai_traits.get()
            )
            text = self.format_npc(npc)
            text += f"{text}\n{'-'*50}\n"
        else:
            npcs = generate_multiple_npcs(
                count=count,
                use_markov=self.use_markov.get(),
                race_specific=self.race_specific.get(),
                starting_letters=self.starting_letters.get(),
                custom_race=race,
                trait_context=context,
                use_ai_traits=self.use_ai_traits.get()
            )
            text = f"\n{'='*50}\nGenerated {count} NPCs:\n{'='*50}\n\n"
            for i, npc in enumerate(npcs, 1):
                text += f"NPC #{i}:\n{self.format_npc(npc)}"
                if i < count: text += "\n" + "-"*30 + "\n"

        self.append_to_result(self.npc_result, text)

    def generate_party(self):
        party = generate_npc_party(
            size=4,
            use_markov=self.use_markov.get(),
            race_specific=self.race_specific.get(),
            starting_letters=self.starting_letters.get(),
            trait_context=self.trait_context.get() or None,
            use_ai_traits=self.use_ai_traits.get()
        )
        text = f"\n{'='*50}\nGenerated Adventure Party:\n{'='*50}\n\n"
        for i, npc in enumerate(party, 1):
            text += f"Party Member #{i}:\n{self.format_npc(npc)}"
            if i < len(party): text += "\n" + "-"*30 + "\n"
        self.append_to_result(self.npc_result, text)

    def show_trait_suggestions(self):
        race = None if self.selected_race.get() == "Random" else self.selected_race.get()
        context = self.trait_context.get() or None
        suggestions = get_trait_suggestions(race=race, context=context, count=5)
        text = "\nTrait suggestions:\n" + "\n".join(f" • {t}" for t in suggestions) + "\n"
        self.append_to_result(self.npc_result, text)

    def generate_encounter(self):
        level = self.level_var.get()
        enc = generate_encounter(level)
        text = (f"\nEncounter for Level {level} Party:\n{'='*40}\n"
                f"Name: {enc['name']}\n"
                f"Monsters: {', '.join(enc['monsters'])}\n"
                f"Difficulty: {enc['difficulty']}\n{'='*40}\n")
        self.append_to_result(self.encounter_result, text)

    def train_new_name(self):
        name = self.new_name.get().strip()
        race = self.new_race.get().strip()
        if not name or not race:
            messagebox.showerror("Error", "Enter both name and race.")
            return
        result = add_names_to_model([name], race=race)
        self.log_training(f"Added name '{name}' for race '{race}': {result}")
        self.new_name.set("")
        self.refresh_race_lists()

    def train_bulk_names(self):
        names = [n.strip() for n in self.bulk_names.get("1.0", tk.END).splitlines() if n.strip()]
        race = self.bulk_race.get().strip()
        if not names or not race:
            messagebox.showerror("Error", "Provide names and race.")
            return
        result = add_names_to_model(names, race=race)
        self.log_training(f"Bulk added {len(names)} names for race '{race}': {result}")
        self.bulk_names.delete("1.0", tk.END)
        self.refresh_race_lists()

    def train_new_trait(self):
        trait = self.new_trait.get().strip()
        if not trait:
            messagebox.showerror("Error", "Enter a trait.")
            return
        result = add_custom_trait(trait)
        self.log_training(f"{result}")
        self.new_trait.set("")

    def refresh_stats(self):
        stats = get_model_stats()
        text = ("D&D Assistant Model Statistics\n" + "="*40 + "\n\n"
                f"• Total names trained: {stats['total_names_trained']}\n"
                f"• Races with models: {stats['races_with_models']}\n"
                f"• Total traits available: {stats['total_traits']}\n\n"
                "Available Races:\n" +
                "\n".join(f" • {r}" for r in stats['available_races']) +
                "\n")
        self.display_result(self.stats_display, text)

    def refresh_race_lists(self):
        self.available_races = ["Random"] + get_available_races()
        # update all comboboxes
        def recurse(widget):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Combobox):
                    vals = child['values']
                    if "Random" in vals:
                        child['values'] = self.available_races
                    else:
                        child['values'] = self.available_races[1:] + ["Custom"]
                recurse(child)
        recurse(self.root)

    def format_npc(self, npc):
        return f"Name: {npc['name']}\nRace: {npc['race']}\nTrait: {npc['trait']}\n"

    def log_training(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        self.training_log.config(state=tk.NORMAL)
        self.training_log.insert(tk.END, entry)
        self.training_log.see(tk.END)
        self.training_log.config(state=tk.DISABLED)

    def clear_npc_results(self):
        self.npc_result.config(state=tk.NORMAL)
        self.npc_result.delete("1.0", tk.END)
        self.npc_result.config(state=tk.DISABLED)

    def display_result(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def append_to_result(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        from ttkthemes import ThemedStyle
    except ImportError:
        ThemedStyle = None

    root = tk.Tk()
    if ThemedStyle:
        style = ThemedStyle(root)
        style.set_theme("arc")
    app = DnDApp(root)
    root.mainloop()
