import mesa
from decimal import Decimal
from decimal import *

from unique_names_generator import get_random_name

from contracts import router_factory
from agents.buyer import BuyerAgent
from agents.lp_provider import ProviderAgent
from states.params import Params
from contracts.types import DummyProtocolAgent, Tokens

NAME_SET = set()


def balance_track(model):
    return model.router._sa_pool.balance


def get_unique_name():
    name = get_random_name(separator="_")
    while name in NAME_SET:
        name = get_random_name(separator="_")
    NAME_SET.add(name)
    return name


class LifelyPayModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, n):
        super().__init__()
        self.router = router_factory.Router("ETH", "USDC")

        # Initiate w/ $1M Protocol-injected Liquidity
        self.router.process_lp_provider_request(
            DummyProtocolAgent(), Tokens(Decimal(1000000), "USDC")
        )

        self.schedule = mesa.time.RandomActivation(self)
        for i in range(n):
            name = get_unique_name()
            ba = BuyerAgent(i, name, self.router, self)
            # buyer gets infinite ETH to spend
            # amount paid and amount redeemed is tracked separately
            ba.receives(Tokens(Decimal("infinity"), "ETH"))
            self.schedule.add(ba)

        for i in range(n, 2 * n):
            name = get_unique_name()
            pa = ProviderAgent(i, name, self.router, self)
            # provider gets infinite USDC to stake
            # amount staked and amount redeemed is tracked separately
            pa.receives(Tokens(Decimal("infinity"), "USDC"))
            self.schedule.add(pa)

        self.running = True
        self.datacollector = mesa.DataCollector(
            model_reporters={"Balance": balance_track}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


if __name__ == "__main__":
    getcontext().prec = 18
    results = mesa.batch_run(
        LifelyPayModel,
        parameters={"n": 300},
        iterations=300,
        max_steps=300,
        number_processes=1,
        data_collection_period=1,
        display_progress=False,
    )
    print(results)
    Params.hard_reset()
