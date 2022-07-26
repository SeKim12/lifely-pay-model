import mesa
from decimal import *
import pandas as pd
from IPython.display import display

from contracts import router_factory
from agents.buyer import BuyerAgent
from agents.oracle import Oracle
from agents.lp_provider import ProviderAgent
from states.params import Params
from contracts.types import DummyProtocolAgent, Tokens

"""Model Data Collector Methods"""


def sa_balance(model):
    return model.router._sa_pool.balance


def fee_balance(model):
    return model.router._fee_pool.balance


def va_balance(model):
    return model.router._va_pool.balance * Oracle.get_price_of("ETH")


def total(model):
    return (
        model.router._sa_pool.balance
        + model.router._fee_pool.balance
        + model.router._va_pool.balance * Oracle.get_price_of("ETH")
    )


def num_triggered(model):
    return model.router.num_triggered


def num_rebalanced(model):
    return model.router.num_rebalanced


class LifelyPayModel(mesa.Model):
    def __init__(self, n):
        super().__init__()
        self.router = router_factory.Router("ETH", "USDC")

        # Initiate w/ $1M Protocol-injected Liquidity
        self.router.process_lp_provider_request(
            DummyProtocolAgent(), Tokens(Decimal(1000000), "USDC")
        )

        self.schedule = mesa.time.RandomActivation(self)
        for i in range(n):
            ba = BuyerAgent(i, "DIMWIT-" + str(i), self.router, self)
            # buyer gets infinite ETH to spend
            # amount paid and amount redeemed is tracked separately
            ba.initiate_with("ETH")
            self.schedule.add(ba)

        for i in range(n, 2 * n):
            pa = ProviderAgent(i, "DIPSHIT-" + str(i), self.router, self)
            # provider gets infinite USDC to stake
            # amount staked and amount redeemed is tracked separately
            pa.initiate_with("USDC")
            self.schedule.add(pa)

        self.running = True
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "USDC Pool Balance USD": sa_balance,
                "ETH Pool Balance USD": va_balance,
                "Fee Pool Balance USDC": fee_balance,
                "Total Asset Value USD": total,
                "# Emergency Triggers": num_triggered,
                "# Pool Rebalancing": num_rebalanced,
            },
            agent_reporters={
                "buyer_spent_eth_usd": "spent_eth_usd",
                "buyer_redeemed_eth_usd": "redeemed_eth_usd",
                "buyer_remaining_vouchers": "remaining_vouchers",
                "staker_staked_usd": "staked_usd",
                "staker_redeemed_usd": "redeemed_usd",
                "staker_APY": "apy",
            },
        )

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)


if __name__ == "__main__":
    getcontext().prec = 18
    results = mesa.batch_run(
        LifelyPayModel,
        parameters={"n": 50},
        iterations=1,
        max_steps=300,
        number_processes=1,
        data_collection_period=1,
        display_progress=False,
    )
    Params.hard_reset()
    rdf = pd.DataFrame(results)
    one_iteration = rdf[(rdf.iteration == 0)]
