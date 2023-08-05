import logging

from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.
from pybit import usdc_options  # <-- import HTTP & WSS for inverse perp
from pybit import spot  # <-- import HTTP & WSS for spot
from pybit import inverse_futures, usdt_perpetual, inverse_perpetual

api_key = "RdHxmhZAaqqFn3aI19"
api_secret = "XCgnXkuRGwrk6NdWIGt0SNmC1nr671UsZfaS"

logging.basicConfig(filename="my_http_example_2022-06-01.py.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")


## Authenticated
session = inverse_perpetual.HTTP(
    endpoint="https://api-testnet.bybit.com",
    api_key=api_key,
    api_secret=api_secret,
    logging_level=logging.DEBUG
)
from time import time, sleep

while True:
    print(session.latest_information_for_symbol(symbol="ETHUSDT"))
    #sleep(0.1)
    sleep(1)



exit()


# We can fetch our wallet balance using an auth'd session.
session_auth.get_wallet_balance(coin="BTC")


"""
Spot & other APIs.
from pybit import HTTP  <-- supports inverse perp & futures, usdt perp, spot.
from pybit.spot import HTTP   <-- exclusively supports spot.
"""

# Reassign session_auth to exclusively use spot.
session_auth = spot.HTTP(
    endpoint="https://api.bybit.com",
    api_key="...",
    api_secret="..."
)


# Prefer spot endpoint via the `spot` arg
session_unauth = HTTP(endpoint="https://api.bybit.com", spot=True)

# Require spot endpoint (`spot` arg unnecessary)
session_auth.get_wallet_balance(coin="BTC")
