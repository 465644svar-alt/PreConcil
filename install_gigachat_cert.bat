@echo off
echo Установка корневого сертификата НУЦ Минцифры для GigaChat...
echo.
echo ВНИМАНИЕ: Для работы GigaChat требуется установить специальный сертификат.
echo Это необходимо сделать один раз.
echo.
pause
curl -k "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer" -w "\n" >> $(python -m certifi)
echo.
echo Сертификат установлен. Перезапустите приложение.
pause