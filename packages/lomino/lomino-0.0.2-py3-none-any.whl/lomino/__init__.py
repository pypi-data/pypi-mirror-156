from .client import Client
import requests as req
new=req.get("https://pypi.python.org/pypi/lomino/json").json()["info"]["version"]
now = "0.0.2"
if now!=new:
	print(f"lomino new version {new} (using {now})")