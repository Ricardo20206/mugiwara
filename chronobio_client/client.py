"""
Client Chronobio PRO - Stratégie PROGRESSIVE "Légumes d'abord"
Optimisé pour survie garantie et score maximum.
"""

import argparse
import time
from enum import Enum
from typing import Any, NoReturn

from chronobio.game.exceptions import ChronobioNetworkError
from chronobio.network.client import Client

from chronobio_client.strategy import Strategy


class GamePhase(Enum):
    """Phases du jeu pour analyse."""
    EARLY = "Démarrage"     # Jours 1-50
    MID = "Consolidation"   # Jours 51-200
    LATE = "Expansion"      # Jours 201+


class PlayerGameClient(Client):
    def __init__(
        self: "PlayerGameClient", server_addr: str, port: int, username: str
    ) -> None:
        super().__init__(server_addr, port, username, spectator=False)
        self._commands: list[str] = []
        self._max_retries = 3
        self._retry_delay = 1.0  # secondes
        self._strategy = Strategy()  # Stratégie de jeu

        # Statistiques pour analyse
        self._day = 0
        self._last_money = 0
        self._total_profit = 0
        self._phase = GamePhase.EARLY
        self._max_money = 0
        self._max_stock = 0

    def _update_phase(self: "PlayerGameClient") -> None:
        """Met à jour la phase de jeu selon le jour actuel."""
        if self._day <= 50:
            self._phase = GamePhase.EARLY
        elif self._day <= 200:
            self._phase = GamePhase.MID
        else:
            self._phase = GamePhase.LATE

    def _display_dashboard(
        self: "PlayerGameClient",
        day: int,
        my_farm: dict[str, Any]
    ) -> None:
        """Affiche un tableau de bord professionnel."""
        money = my_farm.get("money", 0)
        score = my_farm.get("score", 0)
        fields = [f for f in my_farm.get("fields", []) if f.get("bought", False)]
        employees = my_farm.get("employees", [])
        tractors = my_farm.get("tractors", [])
        stock = my_farm.get("soup_factory", {}).get("stock", {})
        factory_days_off = my_farm.get("soup_factory", {}).get("days_off", 0)

        # Calculer les stats
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        total_stock = sum(stock.values())
        available = [e for e in employees if e.get("location") == "FARM" and not e.get("tractor")]
        busy = len(employees) - len(available)

        # Calculer le profit
        profit_today = money - self._last_money if self._day > 1 else 0
        self._total_profit += profit_today
        self._last_money = money

        # Mettre à jour les records
        self._max_money = max(self._max_money, money)
        self._max_stock = max(self._max_stock, total_stock)

        # Affichage professionnel
        print(f"\n{'='*70}")
        phase_name = self._phase.value
        print(f"📅 JOUR {day:3d} | Phase: {phase_name:15s} | 🏷️  Stratégie: PROGRESSIVE")
        print(f"{'='*70}")

        # Ligne finances
        profit_symbol = "📈" if profit_today > 0 else "📉" if profit_today < 0 else "➡️"
        print(f"💰 Capital: {money:7.0f}€ | {profit_symbol} Profit: {profit_today:+6.0f}€ | 🏆 Score: {score:7.0f}€")

        # Ligne infrastructure
        print(f"🌾 Infrastructure: {len(fields):2d} champs | 🚜 {len(tractors):2d} tracteurs | 👷 {len(employees):2d} ouvriers")

        # Ligne main d'œuvre
        print(f"👥 Main d'œuvre: {len(available):2d} dispo, {busy:2d} occupés | 💸 Salaires: {total_salaries:4.0f}€/j")

        # Ligne stock
        print(f"📦 Stock: 🥔{stock.get('POTATO',0):3d} 🍅{stock.get('TOMATO',0):3d} 🥬{stock.get('LEEK',0):3d} 🧅{stock.get('ONION',0):3d} 🥒{stock.get('ZUCCHINI',0):3d} | Total: {total_stock:4d}")

        # Ligne usine
        factory_status = "✅ PRÊTE" if factory_days_off == 0 else f"⏳ Occupée {factory_days_off}j"
        print(f"🍲 Usine: {factory_status}")

        # Alertes salaires
        if total_salaries > 0:
            days_remaining = money // total_salaries
            if days_remaining < 10:
                print(f"  🔴 URGENCE: {days_remaining} jours de salaires!")
            elif days_remaining < 20:
                print(f"  🟡 ALERTE: {days_remaining} jours de salaires")
            elif days_remaining < 30:
                print(f"  🟠 Attention: {days_remaining} jours de salaires")

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
        """Boucle principale du client avec dashboard professionnel."""
        print("⏳ En attente du début de la partie...")
        print(f"👤 Joueur: {self.username}")
        print("🎯 Stratégie: PROGRESSIVE - Légumes d'abord")
        print("✨ Objectif: Survie garantie + Score maximum\n")

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
                raise ValueError(f"Ferme non trouvée: {self.username}")

            # Mettre à jour le jour et la phase
            self._day = game_data.get("day", self._day + 1)
            self._update_phase()

            # Vérifier si la ferme est bloquée
            blocked = my_farm.get("blocked", False)
            if blocked:
                money = my_farm.get("money", 0)
                employees = my_farm.get("employees", [])
                total_salaries = sum(emp.get("salary", 0) for emp in employees)

                print(f"\n{'='*70}")
                print(f"❌ FERME BLOQUÉE AU JOUR {self._day}")
                print(f"{'='*70}")
                print(f"💰 Capital final: {money:,.0f}€")
                print(f"💸 Salaires: {total_salaries:,.0f}€/jour")
                if total_salaries > 0:
                    print(f"⏱️  Jours restants: {money // total_salaries}")
                print(f"🏆 Score final: {my_farm.get('score', 0):,.0f}€")
                print(f"📊 Records: Max capital {self._max_money:,.0f}€ | Max stock {self._max_stock}")
                print(f"{'='*70}")

                self.send_commands()
                continue

            # Afficher le dashboard professionnel
            self._display_dashboard(self._day, my_farm)

            # Appliquer la stratégie de jeu
            commands = self._strategy.get_actions(my_farm)
            for command in commands:
                self.add_command(command)

            # Afficher un résumé des actions
            if len(commands) > 0:
                print(f"📋 Actions: {len(commands)} commande(s) planifiée(s)")
                # Afficher les types d'actions
                action_types: dict[str, int] = {}
                for cmd in commands:
                    action_type = cmd.split()[1] if len(cmd.split()) > 1 else "UNKNOWN"
                    action_types[action_type] = action_types.get(action_type, 0) + 1

                action_summary = " | ".join([f"{act}×{cnt}" for act, cnt in action_types.items()])
                print(f"🎯 Détails: {action_summary}")
            else:
                print("😴 Aucune action ce tour")

            # CRITIQUE : Toujours envoyer au moins une liste vide
            # pour que le jeu ne considère pas la ferme comme abandonnée
            self.send_commands()

    def add_command(self: "PlayerGameClient", command: str) -> None:
        """Ajoute une commande à la liste."""
        self._commands.append(command)

    def send_commands(self: "PlayerGameClient") -> None:
        """Envoie les commandes au serveur avec gestion d'erreurs."""
        # TOUJOURS envoyer une réponse, même vide
        data = {"commands": self._commands.copy() if self._commands else []}

        if len(self._commands) > 0:
            print(f"📤 Envoi: {len(self._commands)} commande(s)")
        else:
            # Même si aucune commande, on envoie une liste vide
            # pour que le serveur sache qu'on est toujours actif
            pass

        try:
            self.send_json(data)
            self._commands.clear()
        except ChronobioNetworkError as e:
            print(f"⚠️ Erreur lors de l'envoi des commandes: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Client Chronobio PRO - Strategie PROGRESSIVE 'mugiwara'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
STRATEGIE PROGRESSIVE - Legumes d'abord:
  Phase 1 (J1-200):  Production legumes uniquement (gerant seul)
  Phase 2 (Capital): Soupes SI 100k+ EUR ET 200+ stock
  Phase 3 (150k+):   Expansion prudente (ouvriers + tracteurs)

CONFIGURATION:
  * Jour 0: 3 champs + 1 tracteur + 0 ouvriers
  * Capital: 40k EUR restants (vs 10k autres strategies)
  * Embauche: Capital > 150k EUR minimum
  * Cuisine: Capital > 100k EUR ET stock > 200 de chaque

OBJECTIFS:
  * Survie garantie: 1799 jours (0 blocage salaires)
  * Score attendu: 300k-500k EUR
  * Stock diversifie des le debut
  * Robustesse maximale
        """,
    )

    parser.add_argument(
        "-a",
        "--address",
        type=str,
        default="localhost",
        help="Adresse du serveur (défaut: localhost)",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=16210,
        help="Port du serveur (défaut: 16210)",
    )

    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default="mugiwara",
        help="Nom d'utilisateur (défaut: mugiwara)",
    )

    args = parser.parse_args()

    # Afficher l'en-tête
    print("=" * 70)
    print("🤖 CLIENT CHRONOBIO PRO - Stratégie PROGRESSIVE")
    print("=" * 70)
    print(f"👤 Joueur: {args.username}")
    print(f"🌐 Serveur: {args.address}:{args.port}")
    print("🎯 Stratégie: Légumes d'abord → Capital → Soupes → Expansion")
    print("✨ Spécialité: Gérant autonome (0 salaires au départ)")
    print("=" * 70)
    print()

    # Lancer le client
    try:
        PlayerGameClient(args.address, args.port, args.username).run()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {type(e).__name__}: {e}")
        raise
