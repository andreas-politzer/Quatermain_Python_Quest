import tkinter as tk
import customtkinter as ctk
import random

class QuatermainGUI:
    def __init__(self, root, engine):
        self.root = root
        self.engine = engine
        self.language = "DE"
        
        self.root.title("Quatermain's Python Quest - PCEP Arcade")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        self.arcade_font_title = ("Courier New", 26, "bold")
        self.arcade_font_text = ("Courier New", 14)
        self.arcade_font_btn = ("Courier New", 14, "bold")
        
        self.player_name = "AND"
        self.show_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def toggle_language(self):
        self.language = "EN" if self.language == "DE" else "DE"
        self.clear_screen()
        if hasattr(self, "in_game") and self.in_game:
            self.render_question()
        else:
            self.show_main_menu()

    def show_main_menu(self):
        self.in_game = False
        self.clear_screen()
        
        lang_btn_text = "🌍 Sprache: DE" if self.language == "DE" else "🌍 Language: EN"
        btn_lang = ctk.CTkButton(
            self.root, text=lang_btn_text, font=("Courier New", 11), 
            command=self.toggle_language, width=120, fg_color="#222222", text_color="#00FF00"
        )
        btn_lang.place(x=760, y=10)
        
        title_text = "🤠 QUATERMAIN'S PYTHON QUEST 🐍"
        title_label = ctk.CTkLabel(self.root, text=title_text, font=self.arcade_font_title, text_color="#00FF00")
        title_label.pack(pady=50)
        
        subtitle_text = "--- Drücke Start, um das PCEP-Exam zu stürmen ---" if self.language == "DE" else "--- Press Start to conquer the PCEP Exam ---"
        sub_label = ctk.CTkLabel(self.root, text=subtitle_text, font=self.arcade_font_text, text_color="#A0A0A0")
        sub_label.pack(pady=5)
        
        input_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=2, border_color="#00FF00")
        input_frame.pack(pady=40, padx=150, fill="x")
        
        name_label_text = "TIPIERE DEIN SPIELER-KÜRZEL (3 ZEICHEN):" if self.language == "DE" else "ENTER YOUR INITIALS (3 CHARACTERS):"
        name_label = ctk.CTkLabel(input_frame, text=name_label_text, font=self.arcade_font_text, text_color="#FFFFFF")
        name_label.pack(pady=10)
        
        self.name_entry = ctk.CTkEntry(input_frame, width=120, font=("Courier New", 22, "bold"), justify="center", text_color="#00FF00", fg_color="#000000")
        self.name_entry.insert(0, self.player_name)
        self.name_entry.pack(pady=10)
        
        available_modules = self.engine.get_available_modules()
        dropdown_label_text = "WÄHLE DEINE EBENE:" if self.language == "DE" else "CHOOSE YOUR LEVEL:"
        dropdown_label = ctk.CTkLabel(self.root, text=dropdown_label_text, font=self.arcade_font_text)
        dropdown_label.pack(pady=5)
        
        mixed_text = "Alle Ebenen gemischt" if self.language == "DE" else "All Levels mixed"
        options_list = [mixed_text] + available_modules
        
        self.module_dropdown = ctk.CTkOptionMenu(
            self.root, values=options_list, font=self.arcade_font_text, 
            fg_color="#1E1E1E", button_color="#00FF00", button_hover_color="#00CC00"
        )
        self.module_dropdown.pack(pady=10)
        
        btn_start_text = "QUEST STARTEN" if self.language == "DE" else "START QUEST"
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
            
        selected_mod = self.module_dropdown.get()
        if "gemischt" in selected_mod or "mixed" in selected_mod:
            selected_mod = None
            
        self.engine.start_new_quest(selected_module=selected_mod, num_questions=30)
        self.in_game = True
        self.render_question()

    def render_question(self):
        """Zeichnet die aktuelle Prüfungsfrage."""
        self.clear_screen()
        
        q_data = self.engine.get_current_question()
        if not q_data or self.engine.is_game_over():
            self.show_game_over_screen()
            return
            
        # --- STATUS BAR ---
        status_frame = ctk.CTkFrame(self.root, height=40, fg_color="#111111")
        status_frame.pack(fill="x", side="top")
        
        hearts = "🐍 " * self.engine.lives
        lives_label = ctk.CTkLabel(status_frame, text=f"LIVES: {hearts}", font=("Courier New", 14, "bold"), text_color="#FF3333")
        lives_label.pack(side="left", padx=20)
        
        player_display = ctk.CTkLabel(status_frame, text=f"PLAYER: {self.player_name}", font=("Courier New", 14, "bold"), text_color="#FFFFFF")
        player_display.pack(side="left", padx=50)
        
        score_label = ctk.CTkLabel(status_frame, text=f"SCORE: {self.engine.score}", font=("Courier New", 14, "bold"), text_color="#00FF00")
        score_label.pack(side="right", padx=20)
        
        # --- FRAGEN CONTAINERS ---
        q_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        q_frame.pack(pady=30, padx=50, fill="both", expand=True)
        
        section_label = ctk.CTkLabel(q_frame, text=f"📍 {q_data['section_name']}", font=("Courier New", 12, "italic"), text_color="#A0A0A0")
        section_label.pack(anchor="w", pady=5)
        
        question_text = q_data["question_de"] if self.language == "DE" else q_data["question_en"]
        
        # HIER ERHÖHEN WIR DEN KONTRAST: Knalliges Weiß (#FFFFFF) für den Text
        q_label = ctk.CTkLabel(q_frame, text=question_text, font=("Courier New", 16, "bold"), justify="left", wraplength=750, text_color="#FFFFFF")
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
        """Wird aufgerufen, wenn eine Option geklickt wird."""
        q_data = self.engine.get_current_question()
        
        # Gehirn prüft die Antwort
        is_correct = self.engine.check_answer(selected_opt)
        
        # JETZT NEU: Schalte den Feedback-Bildschirm dazwischen
        self.show_feedback_screen(is_correct, q_data)

    def show_feedback_screen(self, is_correct, q_data):
        """Der neue Arcade-Zwischenbildschirm mit Zitaten und Dschungel-Humor."""
        self.clear_screen()
        
        # Listen für Filmzitate und Dschungelsprüche
        quotes_correct = [
            '"This is the beginning of a wonderful friendship."',
            '"Yippie-ya-yay, Schweinebacke!"',
            '"Uns bleibt immer noch Paris."',
            "Glückwunsch! Die Schlange zieht sich friedlich zurück.",
            "Ein herrlicher Treffer! Quatermain klopft dir auf die Schulter."
        ]
        
        quotes_wrong = [
            '"Wrong, but you\'ll be back!"',
            '"I\'m getting too old for this crap."',
            '"Now you steam!"',
            '"Play it again, Sam."',
            "Aua! Eine bissige Python erwischt Quatermain am Bein!",
            "Verdammt! Ein Krokodil schnappt nach deinen Stiefeln."
        ]
        
        # Wähle ein zufälliges Zitat passend zum Ausgang
        zitat = random.choice(quotes_correct if is_correct else quotes_wrong)
        
        # Titel und Farbe bestimmen
        if is_correct:
            header_text = "✅ KORREKT / CORRECT"
            header_color = "#00FF00" # Giftgrün
        else:
            header_text = "❌ FALSCH / WRONG"
            header_color = "#FF3333" # Schlangen-Rot
            
        header_label = ctk.CTkLabel(self.root, text=header_text, font=("Courier New", 24, "bold"), text_color=header_color)
        header_label.pack(pady=40)
        
        # Das atmosphärische Zitat einblenden
        quote_label = ctk.CTkLabel(self.root, text=zitat, font=("Courier New", 14, "italic"), text_color="#FFFF00") # Gelb für Zitate
        quote_label.pack(pady=10, padx=100)
        
        # Erklärungstext aus der JSON laden
        explanation = q_data["explanation_de"] if self.language == "DE" else q_data["explanation_en"]
        
        box_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=1, border_color=header_color)
        box_frame.pack(pady=20, padx=80, fill="both", expand=True)
        
        expl_label = ctk.CTkLabel(box_frame, text=explanation, font=self.arcade_font_text, text_color="#FFFFFF", justify="left", wraplength=650)
        expl_label.pack(pady=20, padx=20)
        
        # Weiter-Button
        next_btn_text = "WEITER / CONTINUE"
        btn_next = ctk.CTkButton(
            self.root, text=next_btn_text, font=self.arcade_font_btn,
            fg_color="#00FF00", text_color="#000000", hover_color="#00CC00",
            width=200, height=45, command=self.render_question
        )
        btn_next.pack(pady=30)

    def show_game_over_screen(self):
        """Zeigt das Endergebnis und die Arcade-Highscore-Bestenliste an."""
        self.clear_screen()
        
        # 1. Score über die Engine in die JSON-Datei wegspeichern
        self.engine.save_highscore(self.player_name)
        
        # Titel je nach Spielausgang
        if self.engine.lives > 0:
            end_text = "🎉 QUEST ERFOLGREICH! 🎉\n\nDu hast das goldene Python-Idol geborgen!" if self.language == "DE" else "🎉 QUEST SUCCESSFUL! 🎉\n\nYou recovered the golden Python idol!"
            end_color = "#00FF00"
        else:
            end_text = "💀 GAME OVER 💀\n\nDer Tempel stürzt über Quatermain zusammen..." if self.language == "DE" else "💀 GAME OVER 💀\n\nThe temple collapses over Quatermain..."
            end_color = "#FF3333"
            
        end_label = ctk.CTkLabel(self.root, text=end_text, font=self.arcade_font_title, text_color=end_color, justify="center")
        end_label.pack(pady=40)
        
        # --- HIGHSCORE LEADERBOARD BOX ---
        leaderboard_frame = ctk.CTkFrame(self.root, fg_color="#111111", border_width=2, border_color="#FFFF00")
        leaderboard_frame.pack(pady=10, padx=150, fill="both", expand=True)
        
        board_title = "🏆 TOP 10 TEMPELSTÜRMER 🏆" if self.language == "DE" else "🏆 TOP 10 TEMPLE RUNNERS 🏆"
        board_label = ctk.CTkLabel(leaderboard_frame, text=board_title, font=("Courier New", 16, "bold"), text_color="#FFFF00")
        board_label.pack(pady=10)
        
        # Lade die frisch aktualisierten Highscores aus der Engine
        highscores = self.engine.load_highscores()
        
        # Loope durch die Scores und zeichne sie im coolen Tabellen-Stil auf den Schirm
        for idx, entry in enumerate(highscores):
            pos = idx + 1
            name = entry["name"]
            score = entry["score"]
            
            # Formatiere die Zeile (z.B. "1. AND .......... 200 PTS")
            line_text = f"{pos:2d}. {name:<5} {'.' * 25} {score:4d} PTS"
            
            # Aktuellen Spieler hervorheben
            is_current = (name == self.player_name and score == self.engine.score)
            text_color = "#00FF00" if is_current else "#FFFFFF"
            
            score_line = ctk.CTkLabel(leaderboard_frame, text=line_text, font=("Courier New", 13), text_color=text_color)
            score_line.pack(pady=2, anchor="w", padx=100)
            
        # Zurück zum Hauptmenü Button
        btn_menu = ctk.CTkButton(self.root, text="HAUPTMENÜ / MAIN MENU", font=self.arcade_font_btn, command=self.show_main_menu)
        btn_menu.pack(pady=30)