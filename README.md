# What

`wamotd` (Weather And Message Of The Day) is a Python service intended to run on a Raspberry Pi with an [Adafruit e-Ink display](https://www.adafruit.com/product/4687) shield attached, in order to display a daily weather forecast alongside a short 'message of the day'. The message of the day can be set manually via a small web application.

## Local development

Make a virtualenv:

```
make venv
```

Activate it:

```
. .venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt -r requirements-dev.txt
```

### Type checking & formatting

```
make check
```

### Running it locally

```
make run-local
open http://localhost:8888
```

## Deployment to Raspberry Pi

### Preparing the Raspberry Pi

The target Raspberry Pi must have Python and `pip` installed already (version 3.9.2). You'll also need a user who you can use to SSH to it, and who has sudo access.

### Deploying to the Raspberry Pi

Edit the `deployuser` and `deployto` variables in the `Makefile` to match your target host & user (these could be extracted into a file, but I'm lazy and haven't).

Then:

```
make deploy
```

### Viewing logs

```
journalctl --unit=wamotd@$USER.service --since=yesterday
```
