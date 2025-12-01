@echo off
REM Test if SwarmForge web server is accessible

echo Testing SwarmForge Web Server Connectivity...
echo.

REM Test with PowerShell curl (if available)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✓ Server is ONLINE and responding!' -ForegroundColor Green; Write-Host '✓ Status Code: 200 OK' -ForegroundColor Green; Write-Host '✓ Response Length:' $response.Content.Length 'bytes' -ForegroundColor Green } } catch { Write-Host '✗ Server not responding' -ForegroundColor Red; Write-Host '✗ Error: ' $_.Exception.Message -ForegroundColor Red }"

echo.
echo.
echo If server is not responding:
echo.
echo 1. Make sure RUN_WEBAPP.bat is still running
echo 2. Try opening in a different browser
echo 3. Try: http://127.0.0.1:8000 instead
echo 4. Check Windows Firewall settings
echo 5. Try disabling antivirus temporarily
echo.
pause
