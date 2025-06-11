import turtle
import tkinter as tk
from back.Automate import Automate
from back.Etat import Etat
from interfaces.turtle_visualizer_interface import TurtleVisualizer
from typing import Dict, Tuple

class TurtleVisualizerImpl(TurtleVisualizer):
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        self.screen = turtle.Screen()
        self.screen.setup(canvas_width, canvas_height)
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.hideturtle()
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def dessiner_automate(self, automate: Automate) -> None:
        self.effacer_canvas()  # Clear before drawing
        positions = self.calculer_positions_etats(automate)
        for etat, (x, y) in positions.items():
            self.dessiner_etat(etat, x, y)
        for etat_source in automate.transitions:
            for symbole, destinations in automate.transitions[etat_source].items():
                for etat_dest in destinations:
                    self.dessiner_transition(etat_source, etat_dest, symbole)

    def dessiner_etat(self, etat: Etat, x: int, y: int, couleur: str = "lightblue") -> None:
        self.turtle.penup()
        self.turtle.goto(x, y - 20)
        self.turtle.fillcolor(couleur)
        self.turtle.begin_fill()
        self.turtle.circle(20)
        self.turtle.end_fill()
        self.turtle.write(str(etat))
        if etat.est_final:
            self.turtle.circle(15)

    def dessiner_transition(self, etat_source: Etat, etat_dest: Etat, symbole: str) -> None:
        positions = self.calculer_positions_etats({etat_source, etat_dest})
        x1, y1 = positions[etat_source]
        x2, y2 = positions[etat_dest]
        self.turtle.penup()
        self.turtle.goto(x1, y1)
        self.turtle.pendown()
        self.turtle.goto(x2, y2)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        self.turtle.penup()
        self.turtle.goto(mid_x, mid_y + 10)
        self.turtle.write(symbole)

    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        pass

    def animer_determinisation(self, and_automate: 'AND') -> None:
        pass

    def calculer_positions_etats(self, automate: Automate) -> Dict[Etat, Tuple[int, int]]:
        positions = {}
        n = len(automate.etats)
        import math
        for i, etat in enumerate(automate.etats):
            angle = i * 2 * math.pi / n
            x = 150 * math.cos(angle)
            y = 100 * math.sin(angle)
            positions[etat] = (x, y)
        return positions

    def effacer_canvas(self) -> None:
        self.turtle.clear()
        # Reinitialize the screen to ensure the canvas is valid
        self.screen = turtle.Screen()
        self.screen.setup(self.canvas_width, self.canvas_height)
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.hideturtle()

    def sauvegarder_image(self, nom_fichier: str) -> None:
        try:
            # Ensure the screen is active
            if not self.screen:
                self.screen = turtle.Screen()
                self.screen.setup(self.canvas_width, self.canvas_height)
            canvas = self.screen.getcanvas()
            canvas.postscript(file=nom_fichier)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'image: {e}")