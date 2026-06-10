import tkinter as tk
import customtkinter as ctk
import random
import sys
import threading
import time
import os
import subprocess
from PIL import Image, ImageTk

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


class QuatermainGUI:
    def __init__(self, root, engine):
        self.root = root
        self.engine = engine
        self.language = "de"  # Standardmäßig auf Deutsch passend zur Engine
        
        self.root.title("Quatermain's Python Quest - PCEP Arcade")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.arcade_font_title = ("Courier New", 26, "bold")
        self.arcade_font_text = ("Courier New", 14)
        self.arcade_font_btn = ("Courier New", 14, "bold")
        
        # --- SOUND & FX KONTROLLE ---
        self.fx_muted = False  
        self.music_thread = None
        self.stop_music_event = threading.Event()
        self.current_playing_track = None  # Speichert, ob gerade "normal" oder "boss" läuft
        self.current_proc = None
        
        # --- DYNAMIC THEME COLORS ---
        self.type_colors = {
            "output_prediction": "#FFFF00", # Gelb (Warnung/Code-Blitz)
            "gap_fill": "#00FF00",          # Grün (Schlangen/Natur)
            "error_detection": "#FF3333",   # Rot (Gefahr/Absturz)
            "multiple_choice": "#00CCFF",   # Cyan (Klassisch)
            "code_analysis": "#FFA500",     # Orange (Denkarbeit)
            "boss": "#FFD700"               # Gold (Endgegner/Schatz ab Diff 5)
        }
        
        # Mapping der nostalgischen Arcade-Icons für die Question Types
        self.type_icons = {
            "output_prediction": "⚡ Output Prediction",
            "gap_fill": "🐍 Gap Fill",
            "error_detection": "☠ Error Detection",
            "multiple_choice": "🗿 Temple Challenge",
            "code_analysis": "🔍 Code Analysis"
        }
        
        self.player_name = "AND"
        
        # C64-Blink-Steuerung
        self.blink_state = True
        self.sub_label = None
        
        # Lade Bilder in den Speicher
        self.load_background_images()
        
        # Starte das normale Title-Theme direkt beim Laden
        self.start_music_loop("main-theme.mp3")
        self.show_main_menu()
        
        # Starte den C64-Blink-Loop
        self.run_blink_loop()

    def load_background_images(self):
        """Lädt die Grafiken vorab und konvertiert sie für Tkinter."""
        graphics_dir = resource_path("graphics")
        
        if not os.path.exists(graphics_dir):
            os.makedirs(graphics_dir)
            
        self.bg_images = {}
        files = {
            "menu": "menu-bg.png",
            "jungle": "jungle-bg.png",
            "temple": "temple-bg.png"
        }
        
        for key, filename in files.items():
            path = os.path.join(graphics_dir, filename)
            if os.path.exists(path):
                pil_img = Image.open(path).resize((900, 650), Image.Resampling.LANCZOS)
                self.bg_images[key] = ImageTk.PhotoImage(pil_img)
            else:
                self.bg_images[key] = None

    def set_full_background(self, bg_key):
        """Hängt ein vollflächiges Hintergrundbild ganz nach hinten ins UI."""
        if self.bg_images.get(bg_key):
            bg_label = tk.Label(self.root, image=self.bg_images[bg_key])
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()

    def run_blink_loop(self):
        """Ein unendlicher Loop für das klassische NES/C64 Start-Text-Blinken direkt auf der Grafik."""
        if self.sub_label and self.sub_label.winfo_exists():
            if self.blink_state:
                self.sub_label.configure(text_color="#FFFF00") # Knallgelber Arcade-Blitz
            else:
                self.sub_label.configure(text_color="#FF3333") # Wechselt auf Gefahren-Rot
            self.blink_state = not self.blink_state
        self.root.after(500, self.run_blink_loop)

    def get_theme_color(self, q_data):
        """Ermittelt die Farbe basierend auf Typ und Schwierigkeit (Diff 5 = Boss)."""
        if q_data.get("difficulty", 1) >= 5:
            return self.type_colors["boss"]
        q_type = q_data.get("question_type", "multiple_choice")
        return self.type_colors.get(q_type, "#00FF00")

    def get_audio_path(self, filename):
        """Ermittelt den absoluten Pfad zu einer Sounddatei im audio/-Ordner."""
        return resource_path(os.path.join("audio", filename))

    def start_music_loop(self, track_name):
        """Startet eine Hintergrundmusik im Loop, falls sie nicht schon läuft."""
        if self.engine.sound_muted or self.current_playing_track == track_name:
            return
            
        self.stop_title_music()
        
        self.current_playing_track = track_name
        self.stop_music_event.clear()
        self.music_thread = threading.Thread(target=self._loop_music_thread, args=(track_name,), daemon=True)
        self.music_thread.start()

    def _loop_music_thread(self, track_name):
        """Spielt den ausgewählten Track in einer Endlosschleife ab."""
        sound_path = self.get_audio_path(track_name)
        
        while not self.stop_music_event.is_set():
            if not os.path.exists(sound_path):
                break
                
            if sys.platform == "win32":
                import winsound
                try: winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                except Exception: time.sleep(1)
            else:
                self.current_proc = subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                while self.current_proc.poll() is None:
                    if self.stop_music_event.is_set():
                        self.current_proc.terminate()
                        break
                    time.sleep(0.2)
            time.sleep(0.1)

    def stop_title_music(self):
        self.stop_music_event.set()
        self.current_playing_track = None
        if self.current_proc and self.current_proc.poll() is None:
            self.current_proc.terminate()

    def play_sound(self, sound_type):
        """Feuert einmalige Soundeffekte ab, ohne das UI zu blockieren."""
        if self.fx_muted:
            return
            
        filename_map = {
            "correct": "correct.mp3",
            "wrong": "wrong.mp3",
            "game_over": "game-over.mp3",
            "success": "quest-success.mp3",
            "start": "start-level.mp3"
        }
        
        filename = filename_map.get(sound_type)
        if not filename:
            return
            
        sound_path = self.get_audio_path(filename)
        if not os.path.exists(sound_path):
            return
            
        try:
            if sys.platform == "win32":
                import winsound
                if sound_type == "correct": winsound.Beep(600, 150)
                elif sound_type == "wrong": winsound.Beep(200, 400)
            else:
                subprocess.Popen(["afplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def toggle_language(self):
        """Wechselt die Sprache und zwingt die Engine, die Ordner neu einzulesen."""
        self.language = "en" if self.language == "de" else "de"
        self.engine.load_database(self.language)
        self.clear_screen()
        if hasattr(self, "in_game") and self.in_game:
            self.render_question()
        else:
            self.show_main_menu()

    def toggle_sound(self):
        """Schaltet das Title-Theme an/aus."""
        self.engine.sound_muted = not self.engine.sound_muted
        if self.engine.sound_muted:
            self.stop_title_music()
        else:
            if hasattr(self, "in_game") and self.in_game:
                q_data = self.engine.get_current_question()
                track = "boss-theme.mp3" if (q_data and q_data.get("difficulty", 1) >= 5) else "main-theme.mp3"
                self.start_music_loop(track)
            else:
                self.start_music_loop("main-theme.mp3")
        self.clear_screen()
        self.show_main_menu()

    def toggle_fx(self):
        """Schaltet die Soundeffekte (Fanfare/Tröte) an/aus."""
        self.fx_muted = not self.fx_muted
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
        
        # Setze das geile vollflächige Kinoplakat-Hintergrundbild
        self.set_full_background("menu")
        self.start_music_loop("main-theme.mp3")
        
        # --- TOP CONTROLS (Frei schwebend vor dem Bild, dünn umrandet) ---
        lang_btn_text = "SPRACHE: DE" if self.language == "de" else "LANGUAGE: EN"
        btn_lang = ctk.CTkButton(
            self.root, text=lang_btn_text, font=("Courier New", 11, "bold"), 
            command=self.toggle_language, width=120, fg_color="#0A0A0A", text_color="#00FF00", border_width=1, border_color="#00FF00"
        )
        btn_lang.place(x=760, y=10)
        
        sound_btn_text = "SOUND: ON" if not self.engine.sound_muted else "SOUND: OFF"
        btn_sound = ctk.CTkButton(
            self.root, text=sound_btn_text, font=("Courier New", 11, "bold"),
            command=self.toggle_sound, width=100, fg_color="#0A0A0A", text_color="#FFFF00", border_width=1, border_color="#FFFF00"
        )
        btn_sound.place(x=640, y=10)
        
        fx_btn_text = "FX: ON" if not self.fx_muted else "FX: OFF"
        btn_fx = ctk.CTkButton(
            self.root, text=fx_btn_text, font=("Courier New", 11, "bold"),
            command=self.toggle_fx, width=80, fg_color="#0A0A0A", text_color="#00CCFF", border_width=1, border_color="#00CCFF"
        )
        btn_fx.place(x=540, y=10)
        
        # --- TITEL SYSTEM DIREKT AUF DIE GRAFIK (Ohne verdeckende Box!) ---
        title_label = ctk.CTkLabel(self.root, text="QUATERMAIN'S PYTHON QUEST", font=self.arcade_font_title, text_color="#00FF00", fg_color="transparent")
        title_label.place(x=50, y=60, relwidth=0.88)
        
        subtitle_text = "--- Drücke Start, um das PCEP-Exam zu stürmen ---" if self.language == "de" else "--- Press Start to conquer the PCEP Exam ---"
        self.sub_label = ctk.CTkLabel(self.root, text=subtitle_text, font=self.arcade_font_text, text_color="#A0A0A0", fg_color="transparent")
        self.sub_label.place(x=50, y=200, relwidth=0.88)
        
        # --- PLAYER INPUT (FIX 1: Groesse fest im Konstruktor) ---
        input_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=2, border_color="#00FF00", width=500, height=95)
        input_frame.place(x=200, y=320)
        
        name_label_text = "TIPPE DEIN SPIELER-KÜRZEL (3 ZEICHEN):" if self.language == "de" else "ENTER YOUR INITIALS (3 CHARACTERS):"
        name_label = ctk.CTkLabel(input_frame, text=name_label_text, font=self.arcade_font_text, text_color="#FFFFFF")
        name_label.pack(pady=(8, 2))
        
        self.name_entry = ctk.CTkEntry(input_frame, width=120, font=("Courier New", 22, "bold"), justify="center", text_color="#00FF00", fg_color="#000000", border_color="#00FF00")
        self.name_entry.insert(0, self.player_name)
        self.name_entry.pack(pady=(0, 8))
        
        # --- DYNAMISCHE MODUL-AUSWAHL (FIX 2: Groesse fest im Konstruktor) ---
        dropdown_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=1, border_color="#444444", width=500, height=85)
        dropdown_frame.place(x=200, y=435)
        
        raw_modules = self.engine.get_available_modules()
        dropdown_label_text = "WÄHLE DEINE EBENE:" if self.language == "de" else "CHOOSE YOUR LEVEL:"
        dropdown_label = ctk.CTkLabel(dropdown_frame, text=dropdown_label_text, font=self.arcade_font_text, text_color="#FFFFFF")
        dropdown_label.pack(pady=(5, 2))
        
        mixed_text = "Alle Ebenen gemischt" if self.language == "de" else "All Levels mixed"
        options_list = [mixed_text] + [self.format_module_display(m) for m in raw_modules]
        
        self.module_dropdown = ctk.CTkOptionMenu(
            dropdown_frame, values=options_list, font=self.arcade_font_text, dropdown_font=self.arcade_font_text,
            fg_color="#1E1E1E", button_color="#00FF00", button_hover_color="#00CC00", width=450
        )
        self.module_dropdown.pack(pady=(0, 10))
        
        # --- START BUTTON ---
        btn_start_text = "QUEST STARTEN" if self.language == "de" else "START QUEST"
        btn_start = ctk.CTkButton(
            self.root, text=btn_start_text, font=self.arcade_font_btn, 
            fg_color="#00FF00", text_color="#000000", hover_color="#00CC00",
            height=45, width=280, command=self.press_start
        )
        btn_start.place(x=310, y=545)

    def press_start(self):
        self.player_name = self.name_entry.get().strip().upper()[:3]
        if not self.player_name: 
            self.player_name = "AND"
            
        selected_display = self.module_dropdown.get()
        selected_mod = self.get_internal_module_name(selected_display)
            
        self.engine.start_new_quest(selected_module=selected_mod, num_questions=30)
        self.in_game = True
        
        self.play_sound("start")
        self.render_question()

    def render_question(self):
        self.clear_screen()
        
        q_data = self.engine.get_current_question()
        if not q_data or self.engine.is_game_over():
            self.show_game_over_screen()
            return
            
        # Dynamische Bild- & Musik-Wahl
        if q_data.get("difficulty", 1) >= 5:
            self.set_full_background("temple")
            self.start_music_loop("boss-theme.mp3")
        else:
            self.set_full_background("jungle")
            self.start_music_loop("main-theme.mp3")
            
        # --- STATUS BAR ---
        status_frame = ctk.CTkFrame(self.root, height=35, fg_color="#0A0A0A", border_width=1, border_color="#333333")
        status_frame.pack(fill="x", side="top")
        
        quit_btn_text = "❌ MENÜ" if self.language == "de" else "❌ QUIT"
        btn_quit = ctk.CTkButton(
            status_frame, text=quit_btn_text, font=("Courier New", 12, "bold"),
            fg_color="#331111", hover_color="#551111", text_color="#FF3333",
            width=70, height=24, command=self.show_main_menu
        )
        btn_quit.pack(side="left", padx=10)
        
        hearts = "🐍 " * self.engine.lives
        lives_label = ctk.CTkLabel(status_frame, text=f"LIVES: {hearts}", font=("Courier New", 14, "bold"), text_color="#FF3333")
        lives_label.pack(side="left", padx=10)
        
        player_display = ctk.CTkLabel(status_frame, text=f"PLAYER: {self.player_name}", font=("Courier New", 14, "bold"), text_color="#FFFFFF")
        player_display.pack(side="left", padx=40)
        
        score_label = ctk.CTkLabel(status_frame, text=f"SCORE: {self.engine.score}", font=("Courier New", 14, "bold"), text_color="#00FF00")
        score_label.pack(side="right", padx=20)
        
        # --- THE RETRO SPLITSCREEN (FIX 3: Groesse fest im Konstruktor) ---
        theme_color = self.get_theme_color(q_data)
        q_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=2, border_color=theme_color, width=800, height=420)
        q_frame.place(x=50, y=200)
        
        q_type = q_data.get("question_type", "multiple_choice")
        icon_title = self.type_icons.get(q_type, "🗿 Challenge")
        concept_tag = q_data.get("concept", "general")
        difficulty = q_data.get("difficulty", 1)
        
        location_text = f"MODE: {icon_title} | CONCEPT: {concept_tag} | DIFF: {difficulty}/5"
        
        section_label = ctk.CTkLabel(q_frame, text=location_text, font=("Courier New", 12, "italic"), text_color=theme_color)
        section_label.pack(anchor="w", pady=(10, 2), padx=15)
        
        q_label = ctk.CTkLabel(q_frame, text=q_data["question"], font=("Courier New", 16, "bold"), justify="left", wraplength=760, text_color="#FFFFFF")
        q_label.pack(pady=10, anchor="w", padx=15)
        
        for option in q_data["options"]:
            btn = ctk.CTkButton(
                q_frame, text=option, font=self.arcade_font_text, 
                anchor="w", height=42, fg_color="#1F1F1F", border_width=1, border_color="#444444",
                hover_color="#333333", text_color="#00FF00",
                command=lambda opt=option: self.handle_answer_click(opt)
            )
            btn.pack(pady=6, fill="x", padx=15)

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
        
        if q_data.get("difficulty", 1) >= 5:
            self.set_full_background("temple")
        else:
            self.set_full_background("jungle")
            
        theme_color = self.get_theme_color(q_data)
        specific_feedback = q_data.get("correct_feedback" if is_correct else "incorrect_feedback")
        
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
            
        # --- FEEDBACK SCREEN (FIX 4 & FIX 5: Groesse fest im Konstruktor) ---
        top_feedback_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=1, border_color=header_color, width=800, height=100)
        top_feedback_frame.place(x=50, y=200)
        
        header_label = ctk.CTkLabel(top_feedback_frame, text=header_text, font=("Courier New", 24, "bold"), text_color=header_color)
        header_label.pack(pady=(12, 2))
        
        quote_label = ctk.CTkLabel(top_feedback_frame, text=zitat, font=("Courier New", 14, "italic"), text_color="#FFFF00", justify="center", wraplength=750)
        quote_label.pack(pady=(0, 12), padx=20)
        
        box_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=1, border_color=theme_color, width=800, height=240)
        box_frame.place(x=50, y=315)
        
        expl_label = ctk.CTkLabel(box_frame, text=q_data["explanation"], font=self.arcade_font_text, text_color="#FFFFFF", justify="left", wraplength=750)
        expl_label.pack(pady=20, padx=20)
        
        btn_next = ctk.CTkButton(
            self.root, text="CONTINUE" if self.language == "en" else "WEITER", font=self.arcade_font_btn,
            fg_color="#00FF00", text_color="#000000", hover_color="#00CC00",
            width=200, height=45, command=self.render_question
        )
        btn_next.place(x=350, y=570)

    def show_game_over_screen(self):
        self.clear_screen()
        self.engine.save_highscore(self.player_name)
        self.stop_title_music()
        
        self.set_full_background("menu")
        
        if self.engine.lives > 0:
            self.play_sound("success")
            end_text = "QUEST ERFOLGREICH!\n\nDu hast das goldene Python-Idol geborgen!" if self.language == "de" else "QUEST SUCCESSFUL!\n\nYou recovered the golden Python idol!"
            end_color = "#00FF00"
        else:
            self.play_sound("game_over")
            end_text = "GAME OVER\n\nDer Tempel stürzt über Quatermain zusammen..." if self.language == "de" else "GAME OVER\n\nThe temple collapses over Quatermain..."
            end_color = "#FF3333"
            
        # --- GAME OVER / HIGHSCORE SCREEN (FIX 6 & FIX 7: Groesse fest im Konstruktor) ---
        end_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=2, border_color=end_color, width=700, height=100)
        end_frame.place(x=100, y=140)
        
        end_label = ctk.CTkLabel(end_frame, text=end_text, font=self.arcade_font_title, text_color=end_color, justify="center")
        end_label.pack(pady=20)
        
        leaderboard_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A", border_width=2, border_color="#FFFF00", width=600, height=290)
        leaderboard_frame.place(x=150, y=260)
        
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
        btn_menu.place(x=360, y=575)

    def _on_close(self):
        self.stop_title_music()
        self.root.destroy()