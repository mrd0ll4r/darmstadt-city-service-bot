# Darmstadt City Service Appointments Bot

An **unofficial(!)** Telegram bot to notify you when there are appointments for a service at the Meldebehörde.
I'm not responsible or liable for you and your appointments.

The bot will try to find appointments every five minutes.

## Running

Either run this directly via `poetry install` and `poetry run python main.py` or, preferably, within Docker.

## Configuration

Configured via environment variables, optionally loaded from a `.env` file:
```
TELEGRAM_BOT_TOKEN="<Your Telegram bot token>"
TELEGRAM_CHAT_ID="<Telegram chat ID>"
SERVICE_ID="<ID of a service to search for>" # e.g., cnc-1916 is for Anmeldung
LOCATION_ID=<ID of a location to search for> # e.g., 42 is for Luisencenter
USER_AGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0; you@your-domain.com" # Add your email to this to be nice
```

Fill out the Telegram details and add your email address to the user agent, to be nice.
You can figure out the IDs of services and locations from the website.
This bot currently only supports appointments at the Meldebehörde (https://tevis.ekom21.de/stdar/select2?md=4).

## License

MIT, see [LICENSE](LICENSE).