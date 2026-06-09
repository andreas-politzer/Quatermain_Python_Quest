import tkinter as tk
import customtkinter as ctk
import random
import sys

class QuatermainGUI:
    def __init__(self, root, engine):
        self.root = root
        self.engine = engine
        self.language = "de"  # Standardmäßig auf Deutsch passend zur Engine
        
        self.root.title("Quatermain's Python Quest - PCEP Arcade")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        self.arcade_font_title = ("Courier New", 26, "bold")
        self.arcade_font_text = ("Courier New", 14)
        self.arcade_font_btn = ("Courier New", 14, "bold")
        
        # Mapping der nostalgischen Arcade-Icons für die Question Types
        self.type_icons = {
            "output_prediction": "⚡ Output Prediction",
            "gap_fill": "🐍 Gap Fill",
            "error_detection": "☠ Error Detection",
            "multiple_choice": "🗿 Temple Challenge",
            "code_analysis": "🔍 Code Analysis"
        }
        
        self.player_name = "AND"
        self.show_main_menu()

    def play_sound(self, sound_type):
        if self.engine.sound_muted:
            return
        try:
            if sys.platform == "win32":
                import winsound
                if sound_type == "correct":
                    winsound.Beep(600, 100)
                    winsound.Beep(900, 150)
                elif sound_type == "wrong":
                    winsound.Beep(300, 250)
                    winsound.Beep(150, 300)
            else:
                if sound_type == "correct":
                    print('\a')
                elif sound_type == "wrong":
                    print('\a\a')
        except Exception:
            pass

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def toggle_language(self):
        """Wechselt die Sprache und zwingt die Engine, die Ordner neu einzulesen."""
        self.language = "en" if self.language == "de" else "de"
        
        # Fliegender Wechsel im Dateisystem
        self.engine.load_database(self.language)
        
        self.clear_screen()
        if hasattr(self, "in_game") and self.in_game:
            self.render_question()
        else:
            self.show_main_menu()

    def toggle_sound(self):
        self.engine.sound_muted = not self.engine.sound_muted
        self.clear_screen()
        self.show_main_menu()

    def format_module_display(self, internal_name):
        """Übersetzt die reinen Ordnernamen in hübsche Menü-Titel."""
        titles = {
            "modul1": "Modul 1: Fundamentals" if self.language == "de" else "Module 1: Fundamentals",
            "modul2": "Modul 2: Control Flow" if self.language == "de" else "Module 2: Control Flow",
            "modul3": "Modul 3: Collections" if self.language == "de" else "Module 3: Collections",
            "modul4": "Modul 4: Functions & Exceptions" if self.language == "de" else "Module 4: Functions & Exceptions"
        }
        return titles.get(internal_name, internal_name)

    def get_internal_module_name(self, display_name):
        """Findet den echten Ordnernamen basierend auf der Menüauswahl."""
        if "Modul 1" in display_name or "Module 1" in display_name: return "modul1"
        if "Modul 2" in display_name or "Module 2" in display_name: return "modul2"
        if "Modul 3" in display_name or "Module 3" in display_name: return "modul3"
        if "Modul 4" in display_name or "Module 4" in display_name: return "modul4"
        return None

    def show_main_menu(self):
        self.in_game = False
        self.clear_screen()
        
        # --- TOP CONTROLS ---
        lang_btn_text = "SPRACHE: DE" if self.language == "de" else "LANGUAGE: EN"
        btn_lang = ctk.CTkButton(
            self.root, text=lang_btn_text, font=("Courier New", 11), 
            command=self.toggle_language, width=120, fg_color="#222222", text_color="#00FF00"
        )
        btn_lang.place(x=760, y=10)
        
        sound_btn_text = "SOUND: ON" if not self.engine.sound_muted else "SOUND: OFF"
        btn_sound = ctk.CTkButton(
            self.root, text=sound_btn_text, font=("Courier New", 11),
            command=self.toggle_sound, width=100, fg_color="#222222", text_color="#FFFF00"
        )
        btn_sound.place(x=640, y=10)
        
        # --- TITLE ---
        title_label = ctk.CTkLabel(self.root, text="QUATERMAIN'S PYTHON QUEST", font=self.arcade_font_title, text_color="#00FF00")
        title_label.pack(pady=50)
        
        subtitle_text = "--- Drücke Start, um das PCEP-Exam zu stürmen ---" if self.language == "de" else "--- Press Start to conquer the PCEP Exam ---"
        sub_label = ctk.CTkLabel(self.root, text=subtitle_text, font=self.arcade_font_text, text_color="#A0A0A0")
        sub_label.pack(pady=5)
        
        # --- PLAYER INPUT ---
        input_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=2, border_color="#00FF00")
        input_frame.pack(pady=40, padx=150, fill="x")
        
        name_label_text = "TIPPE DEIN SPIELER-KÜRZEL (3 ZEICHEN):" if self.language == "de" else "ENTER YOUR INITIALS (3 CHARACTERS):"
        name_label = ctk.CTkLabel(input_frame, text=name_label_text, font=self.arcade_font_text, text_color="#FFFFFF")
        name_label.pack(pady=10)
        
        self.name_entry = ctk.CTkEntry(input_frame, width=120, font=("Courier New", 22, "bold"), justify="center", text_color="#00FF00", fg_color="#000000")
        self.name_entry.insert(0, self.player_name)
        self.name_entry.pack(pady=10)
        
        # --- DYNAMISCHE MODUL-AUSWAHL ---
        raw_modules = self.engine.get_available_modules()
        dropdown_label_text = "WÄHLE DEINE EBENE:" if self.language == "de" else "CHOOSE YOUR LEVEL:"
        dropdown_label = ctk.CTkLabel(self.root, text=dropdown_label_text, font=self.arcade_font_text)
        dropdown_label.pack(pady=5)
        
        mixed_text = "Alle Ebenen gemischt" if self.language == "de" else "All Levels mixed"
        options_list = [mixed_text] + [self.format_module_display(m) for m in raw_modules]
        
        self.module_dropdown = ctk.CTkOptionMenu(
            self.root, values=options_list, font=self.arcade_font_text, 
            fg_color="#1E1E1E", button_color="#00FF00", button_hover_color="#00CC00"
        )
        self.module_dropdown.pack(pady=10)
        
        # --- START BUTTON ---
        btn_start_text = "QUEST STARTEN" if self.language == "de" else "START QUEST"
        btn_start = ctk.CTkButton(
            self.root, text=btn_start_text, font=self.arcade_font_btn, 
            fg_color="#00FF00", text_color="#000000", hover_color="#00CC00",
            height=50, width=280, command=self.press_start
        )
        btn_start.pack(pady=40)

    def press_start(self):
        self.player_name = self.name_entry.get().strip().upper()[:3]
        if not self.player_name: 
            self.player_name = "AND"
            
        selected_display = self.module_dropdown.get()
        selected_mod = self.get_internal_module_name(selected_display)
            
        self.engine.start_new_quest(selected_module=selected_mod, num_questions=30)
        self.in_game = True
        self.render_question()

    def render_question(self):
        self.clear_screen()
        
        q_data = self.engine.get_current_question()
        if not q_data or self.engine.is_game_over():
            self.show_game_over_screen()
            return
            
        # --- STATUS BAR ---
        status_frame = ctk.CTkFrame(self.root, height=40, fg_color="#111111")
        status_frame.pack(fill="x", side="top")
        
        hearts = "HP " * self.engine.lives
        lives_label = ctk.CTkLabel(status_frame, text=f"LIVES: {hearts}", font=("Courier New", 14, "bold"), text_color="#FF3333")
        lives_label.pack(side="left", padx=20)
        
        player_display = ctk.CTkLabel(status_frame, text=f"PLAYER: {self.player_name}", font=("Courier New", 14, "bold"), text_color="#FFFFFF")
        player_display.pack(side="left", padx=50)
        
        score_label = ctk.CTkLabel(status_frame, text=f"SCORE: {self.engine.score}", font=("Courier New", 14, "bold"), text_color="#00FF00")
        score_label.pack(side="right", padx=20)
        
        # --- QUESTION SCREEN ---
        q_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        q_frame.pack(pady=30, padx=50, fill="both", expand=True)
        
        q_type = q_data.get("question_type", "multiple_choice")
        icon_title = self.type_icons.get(q_type, "🗿 Challenge")
        concept_tag = q_data.get("concept", "general")
        difficulty = q_data.get("difficulty", 1)
        
        location_text = f"MODE: {icon_title} | CONCEPT: {concept_tag} | DIFF: {difficulty}/5"
        section_label = ctk.CTkLabel(q_frame, text=location_text, font=("Courier New", 12, "italic"), text_color="#FFFF00")
        section_label.pack(anchor="w", pady=5)
        
        q_label = ctk.CTkLabel(q_frame, text=q_data["question"], font=("Courier New", 16, "bold"), justify="left", wraplength=750, text_color="#FFFFFF")
        q_label.pack(pady=15, anchor="w")
        
        for option in q_data["options"]:
            btn = ctk.CTkButton(
                q_frame, text=option, font=self.arcade_font_text, 
                anchor="w", height=45, fg_color="#1F1F1F", border_width=1, border_color="#444444",
                hover_color="#333333", text_color="#00FF00",
                command=lambda opt=option: self.handle_answer_click(opt)
            )
            btn.pack(pady=8, fill="x")

    def handle_answer_click(self, selected_opt):
        q_data = self.engine.get_current_question()
        is_correct = self.engine.check_answer(selected_opt)
        
        if is_correct:
            self.play_sound("correct")
        else:
            self.play_sound("wrong")
            
        self.show_feedback_screen(is_correct, q_data)

    def show_feedback_screen(self, is_correct, q_data):
        self.clear_screen()
        
        # 1. Spezifischer Override aus der JSON abgreifen (Falls vorhanden)
        specific_feedback = q_data.get("correct_feedback" if is_correct else "incorrect_feedback")
        
        # 2. Falls kein Spezial-Feedback in JSON hinterlegt ist -> Nutze die getrennten Sprachpools
        if specific_feedback:
            zitat = specific_feedback
        else:
            if self.language == "de":
                quotes_correct = [
                    "Du hast weise gewählt.",
                    "Die Python-Priester nicken anerkennend.",
                    "Allan steckt die Machete wieder ein.",
                    "Der Schatzraum öffnet sich."
                ]
                quotes_wrong = [
                    "Autsch. Die Falltür war echt.",
                    "Die Krokodile applaudieren.",
                    "Allan hat schon bessere Entscheidungen gesehen.",
                    "Der Tempel fordert seinen Tribut."
                ]
            else:
                quotes_correct = [
                    '"You have chosen wisely."',
                    '"May the Force be with you."',
                    '"Nice shot, Maverick."',
                    '"You can be my wingman anytime."',
                    '"If you build it, he will come."',
                    "The treasure chamber opens.",
                    "The Python priests approve."
                ]
                quotes_wrong = [
                    '"Game over, man. Game over!"',
                    '"Wrong, but you\'ll be back!"',
                    '"That\'s not a knife... THIS is a bug."',
                    '"Inconceivable!"',
                    '"Nobody puts Baby in a corner. Except this answer."',
                    "The crocodiles are laughing.",
                    "The temple claims another victim."
                ]
            zitat = random.choice(quotes_correct if is_correct else quotes_wrong)
        
        header_text = "CORRECT" if is_correct else ("FALSCH" if self.language == "de" else "WRONG")
        header_color = "#00FF00" if is_correct else "#FF3333"
            
        header_label = ctk.CTkLabel(self.root, text=header_text, font=("Courier New", 24, "bold"), text_color=header_color)
        header_label.pack(pady=40)
        
        quote_label = ctk.CTkLabel(self.root, text=zitat, font=("Courier New", 14, "italic"), text_color="#FFFF00", justify="center", wraplength=700)
        quote_label.pack(pady=10, padx=100)
        
        box_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=1, border_color=header_color)
        box_frame.pack(pady=20, padx=80, fill="both", expand=True)
        
        expl_label = ctk.CTkLabel(box_frame, text=q_data["explanation"], font=self.arcade_font_text, text_color="#FFFFFF", justify="left", wraplength=650)
        expl_label.pack(pady=20, padx=20)
        
        btn_next = ctk.CTkButton(
            self.root, text="CONTINUE" if self.language == "en" else "WEITER", font=self.arcade_font_btn,
            fg_color="#00FF00", text_color="#000000", hover_color="#00CC00",
            width=200, height=45, command=self.render_question
        )
        btn_next.pack(pady=30)

    def show_game_over_screen(self):
        self.clear_screen()
        self.engine.save_highscore(self.player_name)
        
        if self.engine.lives > 0:
            end_text = "QUEST ERFOLGREICH!\n\nDu hast das goldene Python-Idol geborgen!" if self.language == "de" else "QUEST SUCCESSFUL!\n\nYou recovered the golden Python idol!"
            end_color = "#00FF00"
        else:
            end_text = "GAME OVER\n\nDer Tempel stürzt über Quatermain zusammen..." if self.language == "de" else "GAME OVER\n\nThe temple collapses over Quatermain..."
            end_color = "#FF3333"
            
        end_label = ctk.CTkLabel(self.root, text=end_text, font=self.arcade_font_title, text_color=end_color, justify="center")
        end_label.pack(pady=40)
        
        leaderboard_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=2, border_color="#FFFF00")
        leaderboard_frame.pack(pady=10, padx=150, fill="both", expand=True)
        
        board_title = "TOP 10 TEMPELSTÜRMER" if self.language == "de" else "TOP 10 TEMPLE RUNNERS"
        board_label = ctk.CTkLabel(leaderboard_frame, text=board_title, font=("Courier New", 16, "bold"), text_color="#FFFF00")
        board_label.pack(pady=10)
        
        highscores = self.engine.load_highscores()
        
        for idx, entry in enumerate(highscores):
            pos = idx + 1
            name = entry["name"]
            score = entry["score"]
            line_text = f"{pos:2d}. {name:<5} {'.' * 25} {score:4d} PTS"
            
            is_current = (name == self.player_name and score == self.engine.score)
            text_color = "#00FF00" if is_current else "#FFFFFF"
            
            score_line = ctk.CTkLabel(leaderboard_frame, text=line_text, font=("Courier New", 13), text_color=text_color)
            score_line.pack(pady=2, anchor="w", padx=100)
            
        btn_menu = ctk.CTkButton(self.root, text="MAIN MENU" if self.language == "en" else "HAUPTMENÜ", font=self.arcade_font_btn, command=self.show_main_menu)
        btn_menu.pack(pady=30)