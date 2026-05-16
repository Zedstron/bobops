# bobops
BobOps is an autonomous AI engineering organization that detects production incidents, performs root cause analysis, generates fixes, validates security and QA, and opens production-ready pull requests on github for human review and ready to go patch.

## Background
So eventually in a running production app its apparently proved that when a endpoint or any service crashes end user starts yelling and we need to investigate server logs, which is a pain in the ass experiance since its take time and mapping the info with actual project location e.g. performing RCA (root cause analysis) is the greatest problem. This project aims to automate this entire flow by monitoring a production app logs in realtime and raise the incidents in realtime in a UI, human will only escalate e.g. tell Bob to fix the specific issue/error and Bob will do it himself in background and creates the PR when done for review.

## How to setup
think the system as a "Team of Bobs", the project calls the bob from shell using non interactive methods and defining a mode/role

to get started first follow the official steps from IBM website to download the bob for shell, do not run in CMD instead copy the inner PS command and run directly in powershell this worked for me atleast.

Please not this project is using Bob shell integration so shell access is mandatory. setup your credentials so that you can actually call bob from shell

once done, copy the .bob which contains custom modes of Bob into the user directory in windows/linux

## How to Run
now you are good to go, start the ui server by running py app.py for windows or for linux python3 app.py, this is developed in windows but supposed to be compaitible with linux as well but not tested for linux.

once server is running open browser and access the UI at http://localhost:8000
Follow following steps to start the system
1) connect repository by entering the full url or repo name
2) start the project to let team of bobs monitor the logs in realtime
3) try to produce or call something which generates error and check UI for incidents
4) click on any incident and invoke Bob so that it can be fixed.
5) Once Bob is done he will automatically create the PR containing fixes, simply review and enjoy.