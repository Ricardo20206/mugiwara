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

    client: PlayerGameClient | None = None
    try:
        client = PlayerGameClient(args.address, args.port, args.username)
        client.run()
    except KeyboardInterrupt:
        print("\nArrêt du client...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

        # Afficher les infos de debug utiles
        if client:
            print("\n🔍 Informations de debug:")
            print(f"  Serveur: {args.address}:{args.port}")
            print(f"  Utilisateur: {args.username}")
            print(f"  Dernières commandes envoyées: {client._commands}")

        sys.exit(1)


if __name__ == "__main__":
    main()
