# Stellar Frame

Framed Pimoroni's Stellar Unicorn[^1] with HTTP API.


## Setup

Put a file `WIFI_CONFIG.py` into the project's root folder (and on the target device) with the following content:
```python
SSID = "<your_ssid>"
PSK = "<your_psk>"
COUNTRY = "<your local two-letter ISO 3166-1 country code>"  
```

Synchronize all files to Stellar Unicorn's root directory.

Reboot.



[^1]: See https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/stellar_unicorn
