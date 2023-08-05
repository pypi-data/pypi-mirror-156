from time import sleep
from pybit import usdt_perpetual

# Set up logging (optional)
import logging
logging.basicConfig(filename="websocket_example_vigilante.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

# Connect with authentication!
ws = usdt_perpetual.WebSocket(
    test=False, trace_logging=True, ping_interval=10, ping_timeout=5
)

def handle_message(message):
    print(message)
    pass

ws.trade_stream(handle_message, "BICOUSDT")

while True:
    # This while loop is required for the program to run. You may execute
    # additional code for your trading logic here.
    sleep(1)
