# main.py
import customtkinter as ctk
from front.application import ApplicationImpl

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ApplicationImpl()
    app.lancer_application()

if __name__ == "__main__":
    main()