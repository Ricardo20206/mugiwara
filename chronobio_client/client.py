"""Client de connexion au serveur Chronobio."""

import argparse
import time
from typing import Any, NoReturn

from chronobio.game.exceptions import ChronobioNetworkError
from chronobio.network.client import Client

from chronobio_client.strategy import Strategy


class PlayerGameClient(Client):
    def __init__(
        self: "PlayerGameClient", server_addr: str, port: int, username: str
    ) -> None:
        super().__init__(server_addr, port, username, spectator=False)
        self._commands: list[str] = []
        self._max_retries = 3
        self._retry_delay = 1.0  # secondes
        self._strategy = Strategy()  # Stratégie de jeu

    def read_json_with_retry(self: "PlayerGameClient") -> dict[str, Any]:
        """Lit les données JSON avec gestion des erreurs réseau."""
        for attempt in range(self._max_retries):
            try:
                data: dict[str, Any] = self.read_json()
                return data
            except ChronobioNetworkError:
                if attempt < self._max_retries - 1:
                    print(f"\n⚠️ Erreur réseau (tentative {attempt + 1}/{self._max_retries})")
                    print(f"   Nouvelle tentative dans {self._retry_delay}s...")
                    time.sleep(self._retry_delay)
                else:
                    print(f"\n❌ Erreur réseau après {self._max_retries} tentatives")
                    raise
        # Ne devrait jamais arriver ici
        raise ChronobioNetworkError("Échec de lecture après tous les essais")

    def run(self: "PlayerGameClient") -> NoReturn:
        """Boucle principale du client."""
        while True:
            # Lire les données du serveur
            game_data = self.read_json_with_retry()

            # Trouver notre ferme
            my_farm = None
            for farm in game_data["farms"]:
                if farm["name"] == self.username:
                    my_farm = farm
                    break

            if my_farm is None:
                raise ValueError(f"My farm is not found ({self.username})")

            # Afficher les informations importantes
            day = game_data.get("day", 0)
            money = my_farm.get("money", 0)
            blocked = my_farm.get("blocked", False)
            score = my_farm.get("score", 0)
            fields = [f for f in my_farm.get("fields", []) if f.get("bought", False)]
            employees = my_farm.get("employees", [])
            stock = my_farm.get("soup_factory", {}).get("stock", {})

            print(f"\n[Jour {day}] {self.username}")
            print(f"  💰 Argent: {money} EUR | 🏆 Score: {score} EUR")
            print(f"  🌾 Champs: {len(fields)} | 👷 Ouvriers: {len(employees)}")

            # Calculer les salaires totaux
            total_salaries = sum(emp.get("salary", 0) for emp in employees)

            # Gérer le cas où la ferme est bloquée
            if blocked:
                print("  *** FERME BLOQUEE ***")
                print("  Raison: plus d'argent pour payer les salaires")
                print(f"  💰 Argent disponible: {money} EUR")
                print(f"  💸 Salaires totaux: {total_salaries} EUR/jour")
                if total_salaries > 0:
                    days_left = money // total_salaries
                    print(f"  ⏱️  Jours de salaires restants: {days_left}")

                # Envoyer une commande vide
                self.send_commands()
                continue

            # Afficher les alertes si l'argent est critique
            if total_salaries > 0:
                days_remaining = money // total_salaries
                if days_remaining < 10:
                    print(f"  🔴 URGENCE: {days_remaining} jours de salaires!")
                elif days_remaining < 15:
                    print(f"  🟡 ALERTE: {days_remaining} jours de salaires")
                elif days_remaining < 20:
                    print(f"  🟠 Attention: {days_remaining} jours de salaires")

            # Afficher l'état détaillé
            total_stock = sum(stock.values())
            factory_days_off = my_farm.get("soup_factory", {}).get("days_off", 0)
            available = [e for e in employees if e.get("location") == "FARM"]
            busy = [e for e in employees if e.get("location") != "FARM"]

            print(f"  👥 Ouvriers: {len(available)} dispo, {len(busy)} occupés")
            print(f"  🌱 Stock: P:{stock.get('POTATO',0)} T:{stock.get('TOMATO',0)} Po:{stock.get('LEEK',0)} O:{stock.get('ONION',0)} C:{stock.get('ZUCCHINI',0)} | Total: {total_stock}")
            print(f"  🍲 Usine: {'✅ PRÊTE' if factory_days_off == 0 else f'⏳ Occupée {factory_days_off}j'}")

            # Appliquer la stratégie de jeu
            commands = self._strategy.get_actions(my_farm)
            for command in commands:
                self.add_command(command)

            # Afficher un résumé des actions
            if len(commands) > 0:
                print(f"  📋 {len(commands)} action(s) planifiée(s)")
            else:
                print("  😴 Aucune action ce tour")

            # Envoyer les commandes au serveur
            self.send_commands()

    def add_command(self: "PlayerGameClient", command: str) -> None:
        """Ajoute une commande à la liste."""
        self._commands.append(command)

    def send_commands(self: "PlayerGameClient") -> None:
        """Envoie les commandes au serveur avec gestion d'erreurs."""
        # Créer une copie de la liste pour éviter les effets de bord
        data = {"commands": []} if not self._commands else {"commands": self._commands.copy()}

        print(f"📤 Envoi de {len(self._commands)} commande(s):", data)

        try:
            self.send_json(data)
            self._commands.clear()
        except ChronobioNetworkError as e:
            print(f"⚠️ Erreur lors de l'envoi des commandes: {e}")
            # Ne pas effacer les commandes en cas d'erreur
            # On les renverra au prochain tour
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game client.")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="name of server on the network",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="location where server listens",
        default=16210,
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="name of the user",
        default="unknown",
        required=True,
    )
    args = parser.parse_args()

    PlayerGameClient(args.address, args.port, args.username).run()
