"""Tests pour le module __main__."""

import sys
from unittest.mock import Mock, patch

import pytest

from chronobio_client.__main__ import main


class TestMainArgparse:
    """Tests pour le parsing des arguments."""

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_with_required_args(self, mock_client):
        """Test avec les arguments requis."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.return_value = None

        test_args = ['prog', '-p', '12345', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args):
            main()

        mock_client.assert_called_once_with('localhost', 12345, 'testuser')
        mock_instance.run.assert_called_once()

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_with_custom_address(self, mock_client):
        """Test avec une adresse personnalisée."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.return_value = None

        test_args = ['prog', '-a', '192.168.1.100', '-p', '8080', '-u', 'player1']
        with patch.object(sys, 'argv', test_args):
            main()

        mock_client.assert_called_once_with('192.168.1.100', 8080, 'player1')

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_with_long_args(self, mock_client):
        """Test avec les arguments longs."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.return_value = None

        test_args = ['prog', '--address', 'server.com', '--port', '16210', '--username', 'mugiwara']
        with patch.object(sys, 'argv', test_args):
            main()

        mock_client.assert_called_once_with('server.com', 16210, 'mugiwara')

    def test_main_missing_port(self):
        """Test sans le port (argument requis)."""
        test_args = ['prog', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            main()

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_default_username(self, mock_client):
        """Test que le username par défaut est 'mugiwara'."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.side_effect = KeyboardInterrupt  # Arrêt immédiat
        
        test_args = ['prog', '-p', '12345']
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit) as exc_info:
            main()
        
        # Vérifier que le client a été créé avec 'mugiwara' comme username
        mock_client.assert_called_once_with('localhost', 12345, 'mugiwara')
        assert exc_info.value.code == 0

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_keyboard_interrupt(self, mock_client):
        """Test de l'interruption clavier."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.side_effect = KeyboardInterrupt()

        test_args = ['prog', '-p', '12345', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args), patch('builtins.print'):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_main_exception(self, mock_client):
        """Test d'une exception générique."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.side_effect = Exception("Test error")

        test_args = ['prog', '-p', '12345', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args), patch('builtins.print'):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestMainDefaults:
    """Tests des valeurs par défaut."""

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_default_address_is_localhost(self, mock_client):
        """Test que l'adresse par défaut est localhost."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.return_value = None

        test_args = ['prog', '-p', '12345', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args):
            main()

        # Vérifier que l'adresse est 'localhost' par défaut
        args = mock_client.call_args[0]
        assert args[0] == 'localhost'


class TestMainPortValidation:
    """Tests de validation du port."""

    @patch('chronobio_client.__main__.PlayerGameClient')
    def test_valid_port_numbers(self, mock_client):
        """Test avec différents numéros de port valides."""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.run.return_value = None

        valid_ports = ['80', '8080', '12345', '16210', '65535']
        for port in valid_ports:
            test_args = ['prog', '-p', port, '-u', 'testuser']
            with patch.object(sys, 'argv', test_args):
                main()

            args = mock_client.call_args[0]
            assert args[1] == int(port)

    def test_invalid_port_not_a_number(self):
        """Test avec un port invalide (pas un nombre)."""
        test_args = ['prog', '-p', 'abc', '-u', 'testuser']
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            main()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
