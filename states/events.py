from typing import List
from decimal import Decimal
from states.interfaces import PoolI, TokenI, EventBusI, AgentI


class Events:
    class Pool:
        class Initialized(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, tokens: TokenI):
                return "{} Pool Initialized with {:.2f} {}".format(
                    pool.type, *tokens.decompose()
                )

        class WithdrawSuccess(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, tokens: TokenI):
                return "Withdrew {:.2f} {} from {} Pool".format(
                    *tokens.decompose(), pool.type
                )

        class DepositSuccess(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, tokens: TokenI):
                return "Deposited {:.2f} {} to {} Pool".format(
                    *tokens.decompose(), pool.type
                )

        class Dry(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, required: TokenI):
                return "Remaining: {:.2f} {}, Need: {:.2f} {}".format(
                    pool.balance, pool.denom, *required.decompose()
                )

        class AttemptingLiquidation(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, required: TokenI):
                return "Attempting to Liquidate {} {}".format(*required.decompose())

        class SuccessLiquidation(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, liquidated: TokenI):
                return "Liquidated {:.2f} {} from {} Pool".format(
                    *liquidated.decompose(), pool.type
                )

        class SuccessRedeem(EventBusI):
            @staticmethod
            def fmt(pool: PoolI, recipient: AgentI, redeemed: TokenI):
                return "Redeemed {:.2f} {} from {} Pool to {} {}".format(
                    *redeemed.decompose(), pool.type, recipient.type, recipient.name
                )

    class Params:
        class Change(EventBusI):
            @staticmethod
            def fmt(param_type: str, og_val: Decimal, cur_val: Decimal):
                return "Parameter *{}* changed from {:.2f} to {:.2f}".format(
                    param_type, og_val, cur_val
                )

    class Test:
        class ChangePrice(EventBusI):
            @staticmethod
            def fmt(denom: str, og_val: Decimal, cur_val: Decimal):
                return "{} Price Changed from ${:.2f} to ${:.2f}".format(
                    denom, og_val, cur_val
                )

    class Provider:
        class AttemptingProvide(EventBusI):
            @staticmethod
            def fmt(provider: AgentI, tokens: TokenI):
                return "\nProvider {} Attempting to Provide {:.2f} {}".format(
                    provider.name, *tokens.decompose()
                )

        class SuccessProvide(EventBusI):
            @staticmethod
            def fmt(provider: AgentI, tokens_sa: TokenI):
                return "Provider {} Successfully Provided {:.2f} {} to Pool\n".format(
                    provider.name, *tokens_sa.decompose()
                )

        class AttemptingRedeem(EventBusI):
            @staticmethod
            def fmt(provider: AgentI, tokens_lp: TokenI):
                return "\nProvider {} Attempting to Redeem {:.2f} {}".format(
                    provider.name, *tokens_lp.decompose()
                )

        class SuccessRedeem(EventBusI):
            @staticmethod
            def fmt(provider: AgentI, redeemed_sa: TokenI):
                return "Provider {} Successfully Redeemed {:.2f} {}\n".format(
                    provider.name, *redeemed_sa.decompose()
                )

    class Buyer:
        class AttemptingBuy(EventBusI):
            @staticmethod
            def fmt(buyer: AgentI, tokens: TokenI):
                return "\nBuyer {} Attempting to Buy using {:.2f} {}".format(
                    buyer.name, *tokens.decompose()
                )

        class AttemptingRedeem(EventBusI):
            @staticmethod
            def fmt(buyer: AgentI, vouchers: TokenI):
                return "\nBuyer {} Attempting to Redeem {:.2f} {} Tokens".format(
                    buyer.name, *vouchers.decompose()
                )

        class SuccessBuy(EventBusI):
            @staticmethod
            def fmt(buyer: AgentI, paid_va: TokenI, price_usd: Decimal):
                return "Buyer {} Successfully Bought Using {:.2f} {}, worth ${:.2f}\n".format(
                    buyer.name, *paid_va.decompose(), price_usd
                )

        class SuccessRedeem(EventBusI):
            @staticmethod
            def fmt(buyer: AgentI, redeemed_va: TokenI, redeemed_usd: Decimal):
                return "Buyer {} Successfully redeemed {} {}, worth ${}\n".format(
                    buyer.name, *redeemed_va.decompose(), redeemed_usd
                )

    class TokenContract:
        class Burned(EventBusI):
            @staticmethod
            def fmt(tokens: TokenI):
                return "Burned {:.2f} {} Tokens".format(*tokens.decompose())

        class Minted(EventBusI):
            @staticmethod
            def fmt(tokens: TokenI, recipient: AgentI):
                return "Minted {:.2f} {} Tokens to {} {}".format(
                    *tokens.decompose(), recipient.type, recipient.name
                )

    class Router:
        class FailRedeem(EventBusI):
            @staticmethod
            def fmt(vouchers: TokenI, cause: str):
                return "{}: Cannot Redeem anything for {:.2f} {} Tokens".format(
                    cause, *vouchers.decompose()
                )

        class AttemptingAutomatedConversion(EventBusI):
            @staticmethod
            def fmt(tokens: TokenI):
                return (
                    "Initiating Automated Conversion of {} {} for DANGER level".format(
                        *tokens.decompose()
                    )
                )

        class NothingToRedeem(EventBusI):
            @staticmethod
            def fmt(tokens: TokenI, cause: str):
                return "{} : Cannot redeem anything for {:.2f} {} Tokens".format(
                    cause, *tokens.decompose()
                )

    class Balancer:
        class TriggerEmergencyProtocol(EventBusI):
            @staticmethod
            def fmt(
                assets: List[Decimal],
                principal: Decimal,
                nominal: Decimal,
                real: Decimal,
            ):
                return "VA POOL: ${:.2f}, SA POOL: ${:.2f}, FEE POOL: ${:.2f}...TOTAL ${:.2f} / PRINCIPAL ${:.2f}...${:.2f} <= ${:.2f}\n\n TRIGGERING EMERGENCY LIQUIDATION \n\n".format(
                    *assets, sum(assets), principal, nominal, real
                )

        class Rebalacing(EventBusI):
            @staticmethod
            def fmt(balance: Decimal, tolerant: Decimal, content: Decimal):
                return "SA Pool: ${:.2f}, Lower than Tolerance ${:.2f}...Refilling to ${:.2f}".format(
                    balance, tolerant, content
                )


def fmt(prefix):
    return prefix and prefix + ": "


# done
# def TestChangePrice(denom, og, now, prefix=''):
#     return '{}{} Price Changed from ${:.2f} to ${:.2f}'.format(fmt(prefix), denom, og, now)


# # done
# def WithdrawSuccessEvent(amount, denom, prefix=''):
#     return '{}Withdrew {:.2f} {} from {} Pool'.format(fmt(prefix), amount, denom, denom)

#
# # done
# def DepositSuccessEvent(amount, denom, pool_type=None, prefix=''):
#     return '{}Deposited {:.2f} {} to {} Pool'.format(fmt(prefix), amount, denom, pool_type or denom)
#
#
# # done
# def PoolDryEvent(balance, required, denom, prefix=''):
#     return '{}Remaining: {:.2f} {}, Need: {:.2f} {}'.format(fmt(prefix), balance, denom, required, denom)

#
# # done
# def AttemptingLiquidationEvent(required_tokens: types.Tokens, prefix=''):
#     return '{}Attempting to Liquidate {:.2f} {}'.format(fmt(prefix), *required_tokens.decompose())

#
# # done
# def LiquidationSuccessEvent(tokens: types.Tokens, prefix=''):
#     return '{}Liquidated {} {}'.format(fmt(prefix), *tokens.decompose())


# # done
# def AutomatedTransferEvent(tokens: types.Tokens, prefix=''):
#     return '{}Initiating Automated Conversion of {:.2f} {} for DANGER level'.format(fmt(prefix), *tokens.decompose())


# done
def ParamChangeEvent(param_type, og, new, prefix=""):
    return "{}Parameter *{}* changed from {:.2f} to {:.2f}".format(
        fmt(prefix), param_type, og, new
    )


# # done
# def RedeemSuccessEvent(recipient: types.AgentType, tokens: types.Tokens, prefix=''):
#     redeem_amount, denom = tokens.decompose()
#     return '{}Redeemed {:.2f} {} from {} Pool to {} {}'.format(fmt(prefix), redeem_amount, denom, denom,
#                                                                recipient.get_type(), recipient.get_name())


# done
# def BuyerAttemptBuyEvent(buyer: types.AgentType, tokens: types.Tokens, prefix=''):
#     return '{}Buyer {} Attempting to Buy using {:.2f} {}'.format(fmt(prefix), buyer.get_name(), *tokens.decompose())


# # done
# def BuyerAttemptRedeemEvent(buyer: types.AgentType, vouchers: types.Tokens, prefix=''):
#     return '{}Buyer {} Attempting to Redeem {:.2f} {} Tokens'.format(fmt(prefix), buyer.get_name(),
#                                                                      *vouchers.decompose())

#
# # done
# def TokenBurnedEvent(tokens: types.Tokens, prefix=''):
#     amount, denom = tokens.decompose()
#     return '{}Burned {:.2f} {} Tokens'.format(fmt(prefix), amount, denom)


# # done
# def TokenMintedEvent(tokens: types.Tokens, recipient: types.AgentType, prefix=''):
#     amount, denom = tokens.decompose()
#     return '{}Minted {:.2f} {} Tokens to {} {}'.format(fmt(prefix), amount, denom, recipient.get_type(),
#                                                        recipient.get_name())

#
# # done
# def BuySuccessEvent(buyer: types.AgentType, paid_va: types.Tokens, price_usd: Decimal, prefix=''):
#     return '{}Buyer {} Successfully bought using {} {}, worth ${}'.format(fmt(prefix), buyer.get_name(),
#                                                                           *paid_va.decompose(), price_usd)


# # done
# def BuyerRedeemSuccessEvent(buyer: types.AgentType, redeemed_va: types.Tokens, redeemed_usd: Decimal, prefix=''):
#     return '{}Buyer {} Successfully redeemed {} {}, worth ${}'.format(fmt(prefix), buyer.get_name(),
#                                                                       *redeemed_va.decompose(), redeemed_usd)
#
#
# def NothingToRedeemEvent(vouchers: types.Tokens, prefix=''):
#     return '{}Cannot redeem anything for {} {} Tokens'.format(fmt(prefix), *vouchers.decompose())

# def AssetAnalyzeEvent(assets, principal, threshold):
#     return '^^^VA POOL: ${:.2f}, SA POOL: ${:.2f}, FEE POOL: ${:.2f}...TOTAL ${:.2f} // PRINCIPAL ${:2f} // THRESHOLD ${:.2f}^^^\n'.format(
#         *assets, sum(assets), principal, threshold)
#
#
# def TriggerDangerProtocolEvent(assets, threshold):
#     return 'VA POOL: ${:.2f}, SA POOL: ${:.2f}, FEE POOL: ${:.2f}...TOTAL ${:.2f} < ${:.2f}\n\n ' \
#            'TRIGGERING EMERGENCY LIQUIDATION \n\n'.format(*assets, sum(assets), threshold)
#
#
# def PoolRebalancingEvent(balance, content):
#     return 'SA POOL: ${:.2f}, Filling Up to ---> ${:.2f}'.format(balance, content)
