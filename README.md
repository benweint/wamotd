# What

`wamotd` (Weather And Message Of The Day) is a Python service intended to run on a Raspberry Pi with an Adafruit e-Ink display shield attached, in order to display a daily weather forecast alongside a short 'message of the day'. The message of the day can be set manually via a Flask web application.

## Installation

TODO: Python dependency installation

Copy over relevant files:

```
just sync
```

```
sudo systemctl daemon-reload
sudo systemctl enable wamotd@$USER.service
sudo reboot
```
