@echo off

rmdir /S /Q lab\client1
rmdir /S /Q lab\client2
rmdir /S /Q lab\server1
rmdir /S /Q lab\server2
rmdir /S /Q lab\main
rmdir /S /Q lab\router1
rmdir /S /Q lab\router2
del /f lab\server1.logs
del /f lab\server2.logs
rmdir /S /Q lab\shared

cd lab
kathara lclean