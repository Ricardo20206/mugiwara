"""Gestion de l'état du jeu."""

from typing import Any


class Field:
    """Représente un champ."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialise un champ à partir des données JSON."""
        # Gérer les deux formats possibles : "location" (FIELD1, FIELD2) ou "number" (1, 2)
        location = data.get("location", "")
        if isinstance(location, str) and location.startswith("FIELD"):
            # Extraire le numéro de "FIELD1" -> 1
            self.number: int = int(location.replace("FIELD", ""))
        else:
            self.number: int = data.get("number", 0)

        # Gérer "content" ou "vegetable" pour le légume
        content = data.get("content", "")
        if content and content != "NONE":
            self.vegetable: str | None = content
        else:
            self.vegetable: str | None = data.get("vegetable")
            if self.vegetable == "NONE":
                self.vegetable = None

        self.water_needed: int = data.get("needed_water", data.get("water_needed", 0))
        self.watered: int = data.get("watered", 0)
        self.harvestable: bool = data.get("harvestable", False)
        self.harvest_in_progress: bool = data.get("harvest_in_progress", False)
        self.days_until_harvest: int = data.get("days_until_harvest", 0)
        self.bought: bool = data.get("bought", True)  # Par défaut, les champs possédés sont "bought"

    def needs_watering(self) -> bool:
        """Vérifie si le champ nécessite de l'arrosage."""
        return self.water_needed > 0

    def is_ready_to_harvest(self) -> bool:
        """Vérifie si le champ est prêt à être récolté."""
        return self.harvestable and not self.harvest_in_progress


class Tractor:
    """Représente un tracteur."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialise un tracteur à partir des données JSON."""
        self.number: int = data.get("number", 0)
        self.location: int = data.get("location", 0)
        self.worker: int | None = data.get("worker")


class Worker:
    """Représente un ouvrier."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialise un ouvrier à partir des données JSON."""
        self.number: int = data.get("number", 0)
        self.location: int = data.get("location", 0)
        self.tractor: int | None = data.get("tractor")
        self.salary: int = data.get("salary", 0)


class GameState:
    """Gère l'état du jeu."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialise l'état du jeu à partir des données JSON."""
        self.day: int = data.get("day", 0)
        self.money: int = data.get("money", 0)
        self.blocked: bool = data.get("blocked", False)
        self.name: str = data.get("name", "client")
        self.score: int = data.get("score", 0)

        # Filtrer les champs pour ne garder que ceux qui sont achetés
        all_fields_data = data.get("fields", [])
        self.fields: list[Field] = [
            Field(field_data) for field_data in all_fields_data
            if field_data.get("bought", True)  # Par défaut True si absent (ancien format)
        ]

        self.tractors: list[Tractor] = [
            Tractor(tractor_data) for tractor_data in data.get("tractors", [])
        ]
        self.workers: list[Worker] = [
            Worker(worker_data) for worker_data in data.get("workers", [])
        ]
        self.soup_factory_stock: dict[str, int] = data.get(
            "soup_factory_stock", {}
        )
        self.soup_factory_shutdown: int = data.get("soup_factory_shutdown", 0)
        self.loans: list[dict[str, Any]] = data.get("loans", [])

    def get_field(self, field_number: int) -> Field | None:
        """Récupère un champ par son numéro."""
        for field in self.fields:
            if field.number == field_number:
                return field
        return None

    def get_available_fields(self) -> list[int]:
        """Retourne la liste des champs disponibles (non achetés)."""
        # Les champs dans self.fields sont ceux qui sont achetés
        owned_fields = {field.number for field in self.fields}
        all_fields = {1, 2, 3, 4, 5}
        return sorted(all_fields - owned_fields)

    def get_next_field_to_buy(self) -> int | None:
        """Retourne le prochain champ à acheter."""
        available = self.get_available_fields()
        return available[0] if available else None

    def get_worker(self, worker_number: int) -> Worker | None:
        """Récupère un ouvrier par son numéro."""
        for worker in self.workers:
            if worker.number == worker_number:
                return worker
        return None

    def get_tractor(self, tractor_number: int) -> Tractor | None:
        """Récupère un tracteur par son numéro."""
        for tractor in self.tractors:
            if tractor.number == tractor_number:
                return tractor
        return None

    def get_fields_needing_watering(self) -> list[Field]:
        """Retourne la liste des champs nécessitant un arrosage."""
        return [field for field in self.fields if field.needs_watering()]

    def get_harvestable_fields(self) -> list[Field]:
        """Retourne la liste des champs prêts à être récoltés."""
        return [field for field in self.fields if field.is_ready_to_harvest()]

    def get_empty_fields(self) -> list[Field]:
        """Retourne la liste des champs vides (sans légume)."""
        return [field for field in self.fields if field.vegetable is None]

    def get_available_workers(self) -> list[Worker]:
        """Retourne la liste des ouvriers disponibles (pas sur un tracteur)."""
        return [worker for worker in self.workers if worker.tractor is None]

    def get_available_tractors(self) -> list[Tractor]:
        """Retourne la liste des tracteurs disponibles (sans ouvrier)."""
        return [tractor for tractor in self.tractors if tractor.worker is None]









