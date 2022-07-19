from typing import Tuple

import mesa
from utils import types


class ProviderAgent(mesa.Agent, types.AgentType):

    def __init__(self, unique_id: int, name: str, model):
        super().__init__(unique_id, model)
        self._name = name
        self._wallet = types.Wallet(name)
        self._type = 'Provider'

    @property
    def identity(self) -> Tuple[str, str]:
        return self._type, self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def wallet(self) -> types.Wallet:
        return self._wallet

    def receives(self, tokens):
        self._wallet.receives(tokens)

    def sends(self, tokens):
        self._wallet.sends(tokens)
