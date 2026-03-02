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
    import pytz
    from datetime import datetime

    # Convert €/MWh → c/kWh
    prices_cents = [p / 10 for p in prices]

    avg = sum(prices_cents) / len(prices_cents)
    min_price = min(prices_cents)
    max_price = max(prices_cents)

    min_hour = hours[prices_cents.index(min_price)]
    max_hour = hours[prices_cents.index(max_price)]

    # ----- FIND BEST 3-HOUR WINDOW BETWEEN 08–20 -----

    # Create list of (hour, price) tuples
    hour_price = list(zip(hours, prices_cents))

    # Filter between 08:00 and 20:00
    filtered = [
        (h, p) for h, p in hour_price
        if 8 <= int(h.split(":")[0]) < 20
    ]

    best_window = None
    best_avg = float("inf")

    for i in range(len(filtered) - 2):
        window = filtered[i:i+3]
        window_prices = [p for _, p in window]
        window_avg = sum(window_prices) / 3

        if window_avg < best_avg:
            best_avg = window_avg
            best_window = window

    start_hour = best_window[0][0]
    end_hour = filtered[filtered.index(best_window[-1])][0]

    # Format date
    today = datetime.now(
        pytz.timezone("Europe/Helsinki")
    ).strftime("%d.%m.%Y")

    return f"""⚡ Electricity Prices Finland – {today}

Average: {avg:.2f} c/kWh

⬇ Lowest: {min_hour} – {min_price:.2f} c/kWh
⬆ Highest: {max_hour} – {max_price:.2f} c/kWh

🟢 Best 3h window (08–20):
{start_hour}–{int(start_hour[:2])+3:02d}:00
Avg: {best_avg:.2f} c/kWh
"""


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)


if __name__ == "__main__":
    hours, prices = get_prices()
    message = build_message(hours, prices)
    send_telegram(message)
