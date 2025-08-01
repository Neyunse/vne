from vne import Core
from vne.aes import AES
from vne import config as CONFIG
from vne.config import key, engine_version
import os

if __name__ == "__main__":
    try:
      engine = Core(os.path.abspath("."))
      engine.run()
    except Exception as e:
      pass