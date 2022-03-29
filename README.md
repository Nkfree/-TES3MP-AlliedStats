# -TES3MP-AlliedStats
Python client and server aiming to display Health, Magicka and Fatigue bars for allies of players via lua script that regularly generates .json that is further read by server.

## Supported OS
Windows

## Installation

- Download .rar file from releases tab
- Open the archive and put **alliesHealthBars.lua** in _server/scripts/custom_ of your tes3mp folder.
- Open **customScripts.lua** and at the bottom add this line: **require("custom.alliesHealthBars")**
- Back in the archive extract the folders **client** and **server** anywhere in your computer, depending on whether you want to start both the server and client or just any of the two

## 

## Server setup
1. Open _server_config.json_ and change the settings to match your needs:
   - **file_path** - add absolute path to the _alliesHealthBars.json_ that will be created in <tes3mp_folder>/server/data/, example is within the config file
   - **local_address** - IP address at which the server is accessible, use the one of _TES3MP Server_
   - **port** - port at which the server will listen to incoming connections, use different port than your _TES3MP Server_, 8000 should work fine
   - **magicka_enabled** - can be either _true_ or _false_, determines whether server allows clients to display magicka stats bar
   - **fatigue_enabled** - can be either _true_ or _false_, determines whether server allows clients to display fatigue stats bar

2. Save _server_config.json_ and launch _server.exe_. If everything went fine, your server should launch and be in the state of listening for connections. Console will inform you briefly about actions taking place inside the server.

## Client setup
1. Open _client_config.json_ and change the settings to match your needs:
   - **destination_address** - change to IP address of the server, for example: _127.0.0.1_ (which corresponds to localhost)
   - **port** - change to the port at which the server is listening
   - **player_name** - change to your _TES3MP_ login name
   - **magicka_enabled** - can be either _true_ or _false_, determines whether you want to display magicka bar in the GUI (has to be enabled by server)
   - **fatigue_enabled** - can be either _true_ or _false_, determines whether you want to display fatigue bar in the GUI (has to be enabled by server)
2. Save _client_config.json_ and launch _client.exe_, if the server is running and there are no firewall obstructions you should be able to connect and see message about that in console

## Logging
- Both server and client store logs in their respective folders (those where .exe files are located) very similar to tes3mp.

## Bug reporting
If for some reason client or server closes on you without any info in the log, open command promt by typing _cmd_ inside search bar of the _File Explorer_ (in the client or server) folder and press enter

Depending on whether you are in client or server folder type _client_ or _server_ inside the command prompt and hit enter

It should give you extra info on why it crashed, please provide the lines related to crash within bug report, or a screenshot

### Credits
[PodSixNet](https://github.com/chr15m/PodSixNet) - python networking library

Tkinter - python UI library

Pillow - python image library

screeninfo - python library to fetch screen dimensions

_openmw_frame.png_ is cut out of OpenMW
