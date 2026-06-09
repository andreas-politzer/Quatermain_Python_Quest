import customtkinter as ctk
from src.engine import QuestEngine
from src.gui import QuatermainGUI

def main():
    # 1. Wecke das logische Gehirn auf und lade die JSON-Datenbank
    engine = QuestEngine()
    
    # 2. Erstelle das leere Systemfenster von CustomTkinter
    root = ctk.CTk()
    
    # 3. Verbinde das Gehirn (engine) mit dem Sichtfenster (gui)
    app = QuatermainGUI(root, engine)
    
    # 4. Halte das Fenster in einer unendlichen Betriebsschleife offen
    root.mainloop()

if __name__ == "__main__":
    main()