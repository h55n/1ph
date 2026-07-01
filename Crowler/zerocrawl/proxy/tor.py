"""Tor integration via stem."""
from __future__ import annotations
from typing import Optional
from loguru import logger

TOR_SOCKS = "socks5://127.0.0.1:9050"

class TorController:
    def __init__(self, control_port: int = 9051, password: str = ""):
        self.control_port = control_port
        self.password = password
        self._controller = None

    def connect(self) -> bool:
        try:
            from stem import Signal
            from stem.control import Controller
            self._controller = Controller.from_port(port=self.control_port)
            self._controller.authenticate(password=self.password)
            logger.info("Connected to Tor control port")
            return True
        except Exception as e:
            logger.error(f"Tor connect failed: {e}")
            return False

    def new_circuit(self) -> bool:
        try:
            from stem import Signal
            self._controller.signal(Signal.NEWNYM)
            return True
        except Exception as e:
            logger.debug(f"Tor new circuit failed: {e}")
            return False

    def get_proxy_url(self) -> str:
        return TOR_SOCKS

    def disconnect(self) -> None:
        if self._controller:
            try:
                self._controller.close()
            except Exception:
                pass
