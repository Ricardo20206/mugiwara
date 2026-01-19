# Script pour lancer Chronobio avec 5 clients
# Le serveur attend 5 joueurs avant de demarrer

# ============================================
# 🎮 CONFIGURATION - MODIFIEZ ICI
# ============================================
$NOM_DE_VOTRE_FERME = "mugiwara"  # ← Changez ce nom comme vous voulez!
$PORT = 16210
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHRONOBIO - LANCEMENT 5 CLIENTS" -ForegroundColor Green
Write-Host "  (Le serveur attend 5 joueurs)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/7] Lancement du serveur (port $PORT)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Serveur && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio.game.server -p $PORT" -WindowStyle Normal
Start-Sleep -Seconds 4

Write-Host "[2/7] Lancement du viewer..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Viewer && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio.viewer -p $PORT --width 1100 --height 700" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "[3/7] Lancement Client 1 (VOTRE ferme: $NOM_DE_VOTRE_FERME)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title $NOM_DE_VOTRE_FERME && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -a localhost -p $PORT -u $NOM_DE_VOTRE_FERME" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host "[4/7] Lancement Client 2..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Client2 && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -a localhost -p $PORT -u Client2" -WindowStyle Normal
Start-Sleep -Seconds 1

Write-Host "[5/7] Lancement Client 3..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Client3 && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -a localhost -p $PORT -u Client3" -WindowStyle Normal
Start-Sleep -Seconds 1

Write-Host "[6/7] Lancement Client 4..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Client4 && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -a localhost -p $PORT -u Client4" -WindowStyle Normal
Start-Sleep -Seconds 1

Write-Host "[7/7] Lancement Client 5..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "title Client5 && cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -a localhost -p $PORT -u Client5" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TOUS LES COMPOSANTS SONT LANCES !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "7 fenetres CMD sont ouvertes:" -ForegroundColor White
Write-Host "  1. [Serveur]            - Traite les actions" -ForegroundColor Gray
Write-Host "  2. [Viewer]             - Interface graphique" -ForegroundColor Yellow
Write-Host "  3. [$NOM_DE_VOTRE_FERME]           - Votre strategie" -ForegroundColor Cyan
Write-Host "  4-7. [Client2-5]        - Fermes factices" -ForegroundColor Gray
Write-Host ""
Write-Host "Avec 5 clients, le serveur va DEMARRER IMMEDIATEMENT!" -ForegroundColor Green
Write-Host ""
Write-Host "REGARDEZ LA FENETRE [Viewer]:" -ForegroundColor Green
Write-Host "  -> Panneau 'Events' sur le cote" -ForegroundColor White
Write-Host "  -> Vous devriez voir les actions de TOUS les clients!" -ForegroundColor White
Write-Host ""
Write-Host "Le jeu devrait maintenant tourner SANS blocage!" -ForegroundColor Green
Write-Host ""
