import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_prices():
    url = "https://www.nordpoolgroup.com/api/marketdata/page/10?currency=EUR"
    r = requests.get(url)
    data = r.json()

    rows = data["data"]["Rows"]

    prices = []
    hours = []

    for row in rows:
        hour = row["Name"]
        for col in row["Columns"]:
            if col["Name"] == "FI":
                price = col["Value"]
                if price != "":
                    prices.append(float(price.replace(",", ".")))
                    hours.append(hour)

    return hours, prices


def build_message(hours, prices):
    avg = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    min_hour = hours[prices.index(min_price)]
    max_hour = hours[prices.index(max_price)]

    today = datetime.now().strftime("%d.%m.%Y")

    return f"""⚡ Electricity Prices – {today}

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
