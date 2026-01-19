setlocal
cd /d %~dp0
:: COLOR_GAN.exe -i temp.png
:: timeout 50 >nul
:: taskkill /im COLOR_GAN.exe 

echo Uruchamiam COLOR_GAN.exe...
:: od tego momentu
if exist temp.png (
	start "" COLOR_GAN.exe -i temp.png
)
else ( if exist temp.jpg (
	start "" COLOR_GAN.exe -i temp.jpg
))
::start "" COLOR_GAN.exe -i temp.png

:CHECK
timeout /t 2 >nul   :: czekaj 2 sekundy (możesz zmienić)

if exist result_colored_out.png (
    taskkill /IM COLOR_GAN.exe /F >nul 2>&1
    exit /b
) else ( if exist result_colored_out.jpg (
	taskkill /IM COLOR_GAN.exe /F >nul 2>&1
    exit /b
))

goto CHECK