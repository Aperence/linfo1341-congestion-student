@echo off

call:init_device_dirs client1
call:init_device_dirs client2
call:init_device_dirs server1
call:init_device_dirs server2

call:init_router router1
call:init_router router2

call:init_main

cd lab 
kathara lstart --noterminals

call:start_server server1 "10.0.1.1" > server1.logs
call:start_server server2 "10.0.1.2" > server2.logs

goto:eof

::--------------------------------------------------------
::-- Function section starts below here
::--------------------------------------------------------

:init_device_dirs

    set name=%~1

    ::- create the directories for devices
    mkdir lab\%name%
    mkdir lab\%name%\home
    mkdir lab\%name%\home\certs
    mkdir lab\%name%\home\data
    mkdir lab\%name%\home\src

    ::- copy the certs needed to run the server
    copy certs lab\%name%\home\certs >NUL

    ::- copy the data files
    copy data\ lab\%name%\home\data >NUL

    ::- copy the init script file
    copy lab\scripts\init lab\%name%\home\init >NUL

    ::- copy the server and client files
    copy src lab\%name%\home\src >NUL

    ::- copy the public key used for ssh
    copy ssh_keys\ssh_keys.pub lab\%name%\home >NUL

goto:eof

:init_router

    set name=%~1

    mkdir lab\%name%

    ::- copy the public key used by main
    copy ssh_keys\ssh_keys.pub lab\%name% >NUL
    ::- copy the impairement script
    copy lab\scripts\impair_itf lab\%name% >NUL

goto:eof


:init_main
    mkdir lab\main
    mkdir lab\main\scenarios

    ::- copy the private key to main
    copy ssh_keys\ssh_keys lab\main >NUL
    ::- copy the connect script
    copy lab\scripts\connect lab\main >NUL
    ::- copy the scenarios
    copy scenarios lab\main\scenarios >NUL
 
goto:eof

:start_server
    set name=%~1
    set ip=%~2

    ::- start a quic + iperf server
    start /b kathara exec %name% -- sh -c "cd /home && /venv/bin/python src/server.py --host %ip% -v 1"
    start /b kathara exec %name% -- sh -c "iperf -s"
goto:eof

