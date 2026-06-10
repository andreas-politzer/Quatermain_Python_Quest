import customtkinter as ctk
from src.engine import QuestEngine
from src.gui import QuatermainGUI


def main():
    # Setze das schicke dunkle Arcade-Design standardmäßig
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.geometry("900x650")  # Erzwingt das perfekte Breitbild-Format
    root.resizable(False, False)  # Verhindert, dass jemand das Layout verzerrt

    # Instanziierung der beiden Kern-Komponenten
    engine = QuestEngine()
    app = QuatermainGUI(root, engine)

    root.mainloop()


if __name__ == "__main__":
    main()