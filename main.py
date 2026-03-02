import os
from datetime import datetime
from nordpool import elspot
import pytz
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_prices():
    prices_spot = elspot.Prices()

    data = prices_spot.hourly(
        areas=["FI"]
    )

    fi_prices = data["areas"]["FI"]["values"]

    hours = []
    prices = []

    for entry in fi_prices:
        hours.append(entry["start"].strftime("%H:%M"))
        prices.append(entry["value"])  # €/MWh

    return hours, prices


def build_message(hours, prices):
    avg = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    min_hour = hours[prices.index(min_price)]
    max_hour = hours[prices.index(max_price)]

    today = datetime.now(pytz.timezone("Europe/Helsinki")).strftime("%d.%m.%Y")

    return f"""⚡ Electricity Prices Finland – {today}

Average: {avg:.2f} €/MWh

⬇ Lowest: {min_hour} – {min_price:.2f}
⬆ Highest: {max_hour} – {max_price:.2f}
"""


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)


if __name__ == "__main__":
    hours, prices = get_prices()
    message = build_message(hours, prices)
    send_telegram(message)
