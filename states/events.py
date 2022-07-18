from utils import types


class Events:
    class Pool:
        class WithdrawSuccess(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, tokens: types.Tokens):
                return 'Withdrew {:.2f} {} from {} Pool'.format(*tokens.decompose(), pool.type)

        class DepositSuccess(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, tokens: types.Tokens):
                return 'Deposited {:.2f} {} to {} Pool'.format(*tokens.decompose(), pool.type)

        class Dry(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, required: types.Tokens):
                return 'Remaining: {:.2f} {}, Need: {:.2f} {}'.format(pool.balance, pool.denom, *required.decompose())

        class AttemptingLiquidation(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, required: types.Tokens):
                return 'Attempting to Liquidate {:.2f} {}'.format(*required.decompose())

        class SuccessLiquidation(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, liquidated: types.Tokens):
                return 'Liquidated {:.2f} {} from {} Pool'.format(*liquidated.decompose(), pool.type)

        class SuccessRedeem(types.EventBus):
            @staticmethod
            def fmt(pool: types.PoolType, recipient: types.AgentType, redeemed: types.Tokens):
                return 'Redeemed {:.2f} {} from {} Pool to {} {}'.format(*redeemed.decompose(), pool.type,
                                                                         *recipient.identity)

    class Params:
        class Change(types.EventBus):
            @staticmethod
            def fmt(param_type: str, og_val: float, cur_val: float):
                return 'Parameter *{}* changed from {:.2f} to {:.2f}'.format(param_type, og_val, cur_val)

    class Test:
        class ChangePrice(types.EventBus):
            @staticmethod
            def fmt(denom: str, og_val: float, cur_val: float):
                return '{} Price Changed from ${:.2f} to ${:.2f}'.format(denom, og_val, cur_val)

    class Buyer:
        class AttemptingBuy(types.EventBus):
            @staticmethod
            def fmt(buyer: types.AgentType, tokens: types.Tokens):
                return 'Buyer {} Attempting to Buy using {:.2f} {}'.format(buyer.name, *tokens.decompose())

        class AttemptingRedeem(types.EventBus):
            @staticmethod
            def fmt(buyer: types.AgentType, vouchers: types.Tokens):
                return 'Buyer {} Attempting to Redeem {:.2f} {} Tokens'.format(buyer.name, *vouchers.decompose())

        class SuccessBuy(types.EventBus):
            @staticmethod
            def fmt(buyer: types.AgentType, paid_va: types.Tokens, price_usd: float):
                return 'Buyer {} Successfully Bought Using {:.2f} {}, worth ${:.2f}'.format(buyer.name,
                                                                                            *paid_va.decompose(),
                                                                                            price_usd)

        class SuccessRedeem(types.EventBus):
            @staticmethod
            def fmt(buyer: types.AgentType, redeemed_va: types.Tokens, redeemed_usd: float):
                return 'Buyer {} Successfully redeemed {} {}, worth ${}'.format(buyer.name,
                                                                                *redeemed_va.decompose(),
                                                                                redeemed_usd)

    class TokenContract:
        class Burned(types.EventBus):
            @staticmethod
            def fmt(tokens: types.Tokens):
                return 'Burned {:.2f} {} Tokens'.format(*tokens.decompose())

        class Minted(types.EventBus):
            @staticmethod
            def fmt(tokens: types.Tokens, recipient: types.AgentType):
                return 'Minted {:.2f} {} Tokens to {} {}'.format(*tokens.decompose(), *recipient.identity)

    class Router:
        class FailRedeem(types.EventBus):
            @staticmethod
            def fmt(vouchers: types.Tokens, cause: str):
                return '{}: Cannot Redeem anything for {:.2f} {} Tokens'.format(cause, *vouchers.decompose())

        class AttemptingAutomatedConversion(types.EventBus):
            @staticmethod
            def fmt(tokens: types.Tokens):
                return 'Initiating Automated Conversion of {:.2f} {} for DANGER level'.format(*tokens.decompose())


def fmt(prefix):
    return prefix and prefix + ': '


# done
def TestChangePrice(denom, og, now, prefix=''):
    return '{}{} Price Changed from ${:.2f} to ${:.2f}'.format(fmt(prefix), denom, og, now)


# done
def WithdrawSuccessEvent(amount, denom, prefix=''):
    return '{}Withdrew {:.2f} {} from {} Pool'.format(fmt(prefix), amount, denom, denom)


# done
def DepositSuccessEvent(amount, denom, pool_type=None, prefix=''):
    return '{}Deposited {:.2f} {} to {} Pool'.format(fmt(prefix), amount, denom, pool_type or denom)


# done
def PoolDryEvent(balance, required, denom, prefix=''):
    return '{}Remaining: {:.2f} {}, Need: {:.2f} {}'.format(fmt(prefix), balance, denom, required, denom)


# done
def AttemptingLiquidationEvent(required_tokens: types.Tokens, prefix=''):
    return '{}Attempting to Liquidate {:.2f} {}'.format(fmt(prefix), *required_tokens.decompose())


# done
def LiquidationSuccessEvent(tokens: types.Tokens, prefix=''):
    return '{}Liquidated {} {}'.format(fmt(prefix), *tokens.decompose())


# done
def AutomatedTransferEvent(tokens: types.Tokens, prefix=''):
    return '{}Initiating Automated Conversion of {:.2f} {} for DANGER level'.format(fmt(prefix), *tokens.decompose())


# done
def ParamChangeEvent(param_type, og, new, prefix=''):
    return '{}Parameter *{}* changed from {:.2f} to {:.2f}'.format(fmt(prefix), param_type, og, new)


# done
def RedeemSuccessEvent(recipient: types.AgentType, tokens: types.Tokens, prefix=''):
    redeem_amount, denom = tokens.decompose()
    return '{}Redeemed {:.2f} {} from {} Pool to {} {}'.format(fmt(prefix), redeem_amount, denom, denom,
                                                               recipient.get_type(), recipient.get_name())


# done
def BuyerAttemptBuyEvent(buyer: types.AgentType, tokens: types.Tokens, prefix=''):
    return '{}Buyer {} Attempting to Buy using {:.2f} {}'.format(fmt(prefix), buyer.get_name(), *tokens.decompose())


# done
def BuyerAttemptRedeemEvent(buyer: types.AgentType, vouchers: types.Tokens, prefix=''):
    return '{}Buyer {} Attempting to Redeem {:.2f} {} Tokens'.format(fmt(prefix), buyer.get_name(),
                                                                     *vouchers.decompose())


# done
def TokenBurnedEvent(tokens: types.Tokens, prefix=''):
    amount, denom = tokens.decompose()
    return '{}Burned {:.2f} {} Tokens'.format(fmt(prefix), amount, denom)


# done
def TokenMintedEvent(tokens: types.Tokens, recipient: types.AgentType, prefix=''):
    amount, denom = tokens.decompose()
    return '{}Minted {:.2f} {} Tokens to {} {}'.format(fmt(prefix), amount, denom, recipient.get_type(),
                                                       recipient.get_name())


# done
def BuySuccessEvent(buyer: types.AgentType, paid_va: types.Tokens, price_usd: float, prefix=''):
    return '{}Buyer {} Successfully bought using {} {}, worth ${}'.format(fmt(prefix), buyer.get_name(),
                                                                          *paid_va.decompose(), price_usd)


# done
def BuyerRedeemSuccessEvent(buyer: types.AgentType, redeemed_va: types.Tokens, redeemed_usd: float, prefix=''):
    return '{}Buyer {} Successfully redeemed {} {}, worth ${}'.format(fmt(prefix), buyer.get_name(),
                                                                      *redeemed_va.decompose(), redeemed_usd)


def NothingToRedeemEvent(vouchers: types.Tokens, prefix=''):
    return '{}Cannot redeem anything for {} {} Tokens'.format(fmt(prefix), *vouchers.decompose())


def TriggerDangerProtocolEvent(assets, threshold):
    return 'VA POOL: ${:.2f}, SA POOL: ${:.2f}, FEE POOL: ${:.2f}...TOTAL ${:.2f} < ${:.2f}\n\n ' \
           'TRIGGERING EMERGENCY LIQUIDATION \n\n'.format(*assets, sum(assets), threshold)
