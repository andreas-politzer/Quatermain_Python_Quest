# 🤠 Quatermain's Python Quest – PCEP Arcade 🐍

An interactive, 80s-inspired retro arcade quiz game designed to conquer the OpenEDG Python Institute PCEP-30-02 certification! Join Allan Quatermain in the depths of the Python Temple, dodge treacherous syntax traps, and recover the golden Python idol.

![Quatermain's Python Quest Menu](assets/hauptmenue.jpg)

## 🏛️ Project Architecture
The game is built using a clean **Model-View-Controller (MVC)** approach to decouple game logic from the user interface and database:
* `data/` – Houses the JSON question database and the local arcade leaderboard.
* `src/engine.py` – The mathematical "brain" managing state, randomized pooling, and module filters.
* `src/gui.py` – The CustomTkinter-powered visual machine running in glorious 80s pixel-aesthetics.

## 🕹️ Game Features
* **Dynamic Module Selector:** Practice specific exam blocks or brave the entire temple at once.
* **80s Movie Quotes:** Featuring algorithmic motivation and classic movie punchlines on every feedback screen.
* **Arcade Leaderboard:** Save your 3-character initials to the local top 10 highscore board.
* **Dual-Language Engine:** Live-switch the entire interface and explanations between German and English.

## 🚀 How to Play
1. Clone the repository:
   ```bash
   git clone [https://github.com/DEIN_BENUTZERNAME/Quatermain_Python_Quest.git](https://github.com/DEIN_BENUTZERNAME/Quatermain_Python_Quest.git)