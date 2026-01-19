"""Point d'entrée principal du client Chronobio."""

import argparse
import sys

from chronobio_client.client import PlayerGameClient


def main() -> None:
    """Fonction principale pour lancer le client."""
    parser = argparse.ArgumentParser(
        description="Client pour le jeu Chronobio"
    )
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        default="localhost",
        help="Adresse IP du serveur de jeu (défaut: localhost)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Port du serveur de jeu",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        required=True,
        help="Nom d'utilisateur du client",
    )

    args = parser.parse_args()

    try:
        client = PlayerGameClient(args.address, args.port, args.username)
        client.run()
    except KeyboardInterrupt:
        print("\nArrêt du client...")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
