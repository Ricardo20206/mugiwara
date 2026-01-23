# Test rapide de la strategie (1 seul joueur)

$PORT = 16211

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST STRATEGIE PROGRESSIVE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Lancement du serveur (port $PORT)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio.game.server -p $PORT --max-players 1 --max-day 100" -WindowStyle Normal
Start-Sleep -Seconds 4

Write-Host "[2/3] Lancement du viewer..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio.viewer -p $PORT --width 1100 --height 700" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "[3/3] Lancement du client mugiwara..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && .venv\Scripts\activate.bat && python -m chronobio_client -p $PORT" -WindowStyle Normal

Write-Host ""
Write-Host "TEST lance! Regardez les fenetres pour voir la strategie." -ForegroundColor Green
Write-Host "Le jeu s'arretera au jour 100 automatiquement." -ForegroundColor Yellow
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer ce script (les fenetres restent ouvertes)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
