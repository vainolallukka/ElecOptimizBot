import os
from datetime import datetime
from nordpool import elspot
import pytz
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_prices():
    prices_spot = elspot.Prices()

    import pytz
    from datetime import datetime

    tz = pytz.timezone("Europe/Helsinki")
    today = datetime.now(tz).date()

    data = prices_spot.hourly(
        areas=["FI"],
        end_date=today
    )

    if data is None:
        raise Exception("No price data returned from Nord Pool.")

    fi_prices = data["areas"]["FI"]["values"]

    hours = []
    prices = []

    for entry in fi_prices:
        hours.append(entry["start"].strftime("%H:%M"))
        prices.append(entry["value"])

    return hours, prices


def build_message(hours, prices):
    # Convert €/MWh to c/kWh
    prices_cents = [p / 10 for p in prices]

    avg = sum(prices_cents) / len(prices_cents)
    min_price = min(prices_cents)
    max_price = max(prices_cents)

    min_hour = hours[prices_cents.index(min_price)]
    max_hour = hours[prices_cents.index(max_price)]

    from datetime import datetime
    import pytz

    today = datetime.now(
        pytz.timezone("Europe/Helsinki")
    ).strftime("%d.%m.%Y")

    return f"""⚡ Electricity Prices Finland – {today}

Average: {avg:.2f} c/kWh

⬇ Lowest: {min_hour} – {min_price:.2f} c/kWh
⬆ Highest: {max_hour} – {max_price:.2f} c/kWh
"""


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)


if __name__ == "__main__":
    hours, prices = get_prices()
    message = build_message(hours, prices)
    send_telegram(message)
