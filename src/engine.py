import json
import random
import os

class QuestEngine:
    def __init__(self, json_path="data/questions.json", score_path="data/highscores.json"):
        self.json_path = json_path
        self.score_path = score_path
        self.all_questions = []      
        self.modules = {}            
        self.active_pool = []        
        self.current_index = 0
        self.lives = 3
        self.score = 0
        
        self.load_database()

    def load_database(self):
        """Lädt alle Fragen aus der JSON und sortiert sie nach Modulen."""
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for section in data.get("quests", []):
                    section_name = section.get("section", "Unbekanntes Modul")
                    if section_name not in self.modules:
                        self.modules[section_name] = []
                    for question in section.get("questions", []):
                        question["section_name"] = section_name
                        self.all_questions.append(question)
                        self.modules[section_name].append(question)
        else:
            print(f"Warnung: {self.json_path} wurde nicht gefunden!")

    def get_available_modules(self):
        return list(self.modules.keys())

    def start_new_quest(self, selected_module=None, num_questions=30):
        self.lives = 3
        self.score = 0
        self.current_index = 0
        
        if selected_module and selected_module in self.modules:
            source_pool = self.modules[selected_module]
        else:
            source_pool = self.all_questions
            
        pool_size = min(num_questions, len(source_pool))
        self.active_pool = random.sample(source_pool, pool_size)

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

    # --- JETZT NEU: DAS HIGHSCORE-SYSTEM ---
    
    def load_highscores(self):
        """Lädt die Highscore-Liste aus der JSON-Datei."""
        if os.path.exists(self.score_path):
            with open(self.score_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_highscore(self, player_name):
        """Speichert einen neuen Score ab und sortiert die Liste nach Punkten."""
        scores = self.load_highscores()
        
        # Neuen Eintrag hinzufügen
        new_entry = {"name": player_name, "score": self.score}
        scores.append(new_entry)
        
        # Sortieren: Höchste Punktzahl nach ganz oben
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)
        
        # Wir behalten im Arcade-Style nur die Top 10 Einträge
        scores = scores[:10]
        
        # Zurück in die Datei schreiben
        with open(self.score_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)