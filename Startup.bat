@echo off
set WindowNameBase=GenshinStatusBot-
set count=0

set /P user_input="How many bot start? : "

setlocal enabledelayedexpansion

for /l %%n in (1,1,%user_input%) do (
    set /a count=!count!+1
    set WindowName=%WindowNameBase%!count!
    echo Starting !WindowName!
    START /MIN "!WindowName!" py -3 main.py !count!
    pause
)
pause