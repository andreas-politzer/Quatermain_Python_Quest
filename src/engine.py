import json
import random
import os

class QuestEngine:
    def __init__(self, data_dir="data", score_path="data/highscores.json"):
        self.data_dir = data_dir
        self.score_path = score_path
        
        # Speicherstrukturen für die geladenen Fragen
        self.all_questions = []      # Flacher Pool für "Alle Ebenen gemischt"
        self.modules = {}            # Gruppiert nach Modul-Ordner: {"modul1": [...], "modul2": [...]}
        
        # Spielzustand
        self.active_pool = []        
        self.current_index = 0
        self.lives = 3
        self.score = 0
        self.sound_muted = False
        
        # Beim Start laden wir die deutsche Version als Standard
        self.load_database(lang="de")

    def load_database(self, lang):
        """
        Scannt autonom den Ordner data/{lang}/ nach allen Unterordnern und 
        JSON-Dateien ab und fusioniert sie im Speicher.
        """
        self.all_questions = []
        self.modules = {}
        
        target_path = os.path.join(self.data_dir, lang)
        
        if not os.path.exists(target_path):
            print(f"Warnung: Verzeichnis {target_path} existiert nicht!")
            return

        # os.walk durchkämmt alle Unterordner (modul1, modul2, etc.)
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    
                    # Ordnername extrahieren (z. B. "modul1")
                    module_name = os.path.basename(root)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            questions_list = json.load(f)
                            
                            if module_name not in self.modules:
                                self.modules[module_name] = []
                                
                            for q in questions_list:
                                # Herkunftsmodul injizieren
                                q["module_id"] = module_name
                                
                                self.all_questions.append(q)
                                self.modules[module_name].append(q)
                                
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Fehler beim Einlesen von {file_path}: {e}")

    def get_available_modules(self):
        """Gibt eine sortierte Liste aller gefundenen Modul-Ordnernamen zurück."""
        return sorted(list(self.modules.keys()))

    def start_new_quest(self, selected_module=None, num_questions=30):
        """Erstellt einen zufälligen Fragenpool für die aktuelle Spielrunde."""
        self.lives = 3
        self.score = 0
        self.current_index = 0
        
        if selected_module and selected_module in self.modules:
            source_pool = self.modules[selected_module]
        else:
            source_pool = self.all_questions
            
        pool_size = min(num_questions, len(source_pool))
        if pool_size > 0:
            self.active_pool = random.sample(source_pool, pool_size)
        else:
            self.active_pool = []

    def get_current_question(self):
        if self.current_index < len(self.active_pool) and self.lives > 0:
            return self.active_pool[self.current_index]
        return None

    def check_answer(self, selected_option):
        current_q = self.get_current_question()
        if not current_q:
            return False
            
        is_correct = (selected_option == current_q["correct"])
        if is_correct:
            self.score += 100
        else:
            self.lives -= 1
            
        self.current_index += 1
        return is_correct

    def is_game_over(self):
        return self.lives <= 0 or self.current_index >= len(self.active_pool)

    def load_highscores(self):
        if os.path.exists(self.score_path):
            with open(self.score_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_highscore(self, player_name):
        scores = self.load_highscores()
        new_entry = {"name": player_name, "score": self.score}
        scores.append(new_entry)
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)
        scores = scores[:10]
        
        with open(self.score_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)