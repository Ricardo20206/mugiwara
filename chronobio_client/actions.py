"""Actions possibles dans le jeu."""

from typing import List, Optional


class Actions:
    """Génère les commandes d'actions pour le jeu."""

    @staticmethod
    def buy_field(manager: int = 0) -> str:
        """Acheter un champ."""
        return f"{manager} ACHETER_CHAMP"

    @staticmethod
    def sow(worker: int, vegetable: str, field: int) -> str:
        """Semer un légume sur un champ."""
        return f"{worker} SEMER {vegetable} {field}"

    @staticmethod
    def water(worker: int, field: int) -> str:
        """Arroser un champ."""
        return f"{worker} ARROSER {field}"

    @staticmethod
    def sell(manager: int, field: int) -> str:
        """Vendre les légumes d'un champ."""
        return f"{manager} VENDRE {field}"

    @staticmethod
    def buy_tractor(manager: int = 0) -> str:
        """Acheter un tracteur."""
        return f"{manager} ACHETER_TRACTEUR"

    @staticmethod
    def store(worker: int, field: int, tractor: int) -> str:
        """Stocker des légumes d'un champ dans l'usine."""
        return f"{worker} STOCKER {field} {tractor}"

    @staticmethod
    def cook(worker: int) -> str:
        """Cuisiner des soupes."""
        return f"{worker} CUISINER"

    @staticmethod
    def employ(manager: int = 0) -> str:
        """Employer un ouvrier."""
        return f"{manager} EMPLOYER"

    @staticmethod
    def fire(manager: int, worker: int) -> str:
        """Licencier un ouvrier."""
        return f"{manager} LICENCIER {worker}"

    @staticmethod
    def borrow(manager: int, amount: int) -> str:
        """Emprunter de l'argent à la banque."""
        return f"{manager} EMPRUNTER {amount}"

    @staticmethod
    def move(worker: int, location: int) -> Optional[str]:
        """Déplacer un ouvrier vers un lieu."""
        # Le déplacement n'est pas une action, mais nécessaire pour certaines actions
        # Cette méthode retourne None car le déplacement se fait automatiquement
        # lors des actions si nécessaire
        return None












