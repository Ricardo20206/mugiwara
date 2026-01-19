# Script pour lancer les tests Chronobio

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHRONOBIO - TESTS UNITAIRES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que pytest est installé
try {
    python -m pytest --version | Out-Null
} catch {
    Write-Host "[ERREUR] pytest n'est pas installe !" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation de pytest..." -ForegroundColor Yellow
    python -m pip install pytest pytest-cov pytest-mock
    Write-Host ""
}

Write-Host "[1/3] Lancement des tests..." -ForegroundColor Green
Write-Host ""

# Lancer les tests avec rapport de couverture
python -m pytest tests/ -v --cov=chronobio_client --cov-report=term-missing --cov-report=html

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTS TERMINES !" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Rapport de couverture genere dans: htmlcov/index.html" -ForegroundColor Yellow
Write-Host "Pour l'ouvrir: start htmlcov/index.html" -ForegroundColor Yellow
Write-Host ""
