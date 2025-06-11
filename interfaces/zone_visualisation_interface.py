# front/zone_visualisation_interface.py
from abc import ABC, abstractmethod
import customtkinter as ctk
from back.Automate import Automate
from typing import List, Set

class ZoneVisualisation(ctk.CTkFrame, ABC):
    @abstractmethod
    def afficher_automate(self, automate: Automate) -> None:
        pass

    @abstractmethod
    def creer_controles_visualisation(self) -> None:
        pass

    @abstractmethod
    def integrer_visualiseur(self, type_visualiseur: str) -> None:
        pass

    @abstractmethod
    def mode_animation(self, activer: bool) -> None:
        pass

    @abstractmethod
    def mode_comparaison(self, automates: List[Automate]) -> None:
        pass

    @abstractmethod
    def afficher_automate_texte(self, automate: Automate) -> None:
        pass

    @abstractmethod
    def afficher_automate_graphique(self, automate: Automate) -> None:
        pass

    @abstractmethod
    def afficher_resultat_reconnaissance(self, mot: str, resultat: bool) -> None:
        pass

    @abstractmethod
    def afficher_proprietes(self, est_deterministe: bool, est_complet: bool) -> None:
        pass

    @abstractmethod
    def afficher_matrice(self, matrice: List[List[Set]], etats: List[str], alphabet: List[str]) -> None:
        pass

    @abstractmethod
    def animer_reconnaissance(self, automate: Automate, mot: str) -> None:
        pass

    @abstractmethod
    def animer_determinisation(self, automate: 'AND') -> None:
        pass

    @abstractmethod
    def exporter_image(self, nom_fichier: str) -> None:
        pass