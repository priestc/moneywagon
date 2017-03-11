import datetime
from moneywagon.crypto_data import crypto_data

class SupplyEstimator(object):
    """
    Returns a function that can be used to calculate the supply of coins for a given
    amount of minutes since genesis date. Only works for standard bitcoin forked
    currencies such as LTC, DOGE, PPC, etc.
    """

    def __init__(self, crypto=None, supply_data=None, genesis_date=None):
        if crypto:
            try:
                cd = crypto_data[crypto.lower()]
            except KeyError:
                raise Exception("Currency not supported")
            try:
                self.genesis_date = cd['genesis_date']
                self.supply_data = cd['supply_data']
            except KeyError:
                raise Exception("Insufficient supply data for %s" % crypto.upper())
        else:
            self.supply_data = supply_data
            self.genesis_date = genesis_date

        self.minutes_per_block = self.supply_data['minutes_per_block']
        self.method = self.supply_data['method']
        self.blocktime_adjustments = self.supply_data.get('blocktime_adjustments', None)

    @property
    def block_adjustment_in_minutes(self):
        minute_adjustments = []
        minutes_since_genesis = 0
        previous_minutes_per_block = self.minutes_per_block
        previous_adjustment_block = 0
        for adjustment_block, new_minutes_per_block in self.blocktime_adjustments:
            minutes_since_last_adjustment = (adjustment_block - previous_adjustment_block) * previous_minutes_per_block
            #minutes_since_genesis += minutes_since_last_adjustment
            minute_adjustments.append([minutes_since_last_adjustment, new_minutes_per_block])

            previous_minutes_per_block = new_minutes_per_block
            previous_adjustment_block = adjustment_block

        return minute_adjustments

    def estimate_height_from_date(self, at_time):
        minutes = (at_time - self.genesis_date).total_seconds() / 60.0
        target_block = int(minutes / self.minutes_per_block)

        if self.blocktime_adjustments:
            new_block = 0
            previous_minutes_per_block = self.minutes_per_block
            minutes_since_genesis = 0

            for minutes_since_last_adjustment, new_minutes_per_block in self.block_adjustment_in_minutes:
                if minutes_since_genesis < minutes:
                    this_blocks = minutes_since_last_adjustment / previous_minutes_per_block
                    new_block += this_blocks
                else:
                    remainder_blocks = (minutes - minutes_since_genesis) / previous_minutes_per_block
                    new_block += remainder_blocks
                    break

                previous_minutes_per_block = new_minutes_per_block
                minutes_since_genesis += minutes_since_last_adjustment
            else:
                remainder_blocks = (minutes - minutes_since_genesis) / new_minutes_per_block
                new_block += remainder_blocks

            target_block = new_block

        return target_block

    def estimate_date_from_height(self, block_height):
        minutes = block_height * self.minutes_per_block
        if self.blocktime_adjustments:
            new_minutes = 0
            previous_adjustment_block = 0
            previous_minutes_per_block = self.minutes_per_block
            for adjustment_block, new_minutes_per_block in self.blocktime_adjustments:
                if block_height > adjustment_block:
                    minutes_this_adjustment = (adjustment_block - previous_adjustment_block) * previous_minutes_per_block
                    new_minutes += minutes_this_adjustment
                else:
                    remaining_minutes = (block_height - previous_adjustment_block) * previous_minutes_per_block
                    new_minutes += remaining_minutes
                    break

                previous_minutes_per_block = new_minutes_per_block
                previous_adjustment_block = adjustment_block
            else:
                remaining_minutes = (block_height - previous_adjustment_block) * previous_minutes_per_block
                new_minutes += remaining_minutes

            minutes = new_minutes

        return self.genesis_date + datetime.timedelta(minutes=minutes)

    def calculate_supply(self, block_height=None, at_time=None):
        if at_time:
            block_height = self.estimate_height_from_date(at_time)

        if self.method == 'standard':
            return self._standard_supply(block_height)
        if self.method == 'per_era':
            return self._per_era_supply(block_height)

    def _per_era_supply(self, block_height):
        """
        Calculate the coin supply based on 'eras' defined in crypto_data. Some
        currencies don't have a simple algorithmically defined halfing schedule
        so coins supply has to be defined explicitly per era.
        """
        coins = 0
        for era in self.supply_data['eras']:
            end_block = era['end']
            start_block = era['start']
            reward = era['reward']

            if not end_block or block_height < end_block:
                blocks_this_era = block_height - start_block
                coins += blocks_this_era * reward
                break

            blocks_per_era = end_block - start_block
            coins += reward * blocks_per_era

        return coins

    def _standard_supply(self, block_height):
        """
        Calculate the supply of coins for a given time (in either datetime, or
        block height) for coins that use the "standard" method of halfing.
        """
        start_coins_per_block = self.supply_data['start_coins_per_block']
        minutes_per_block = self.supply_data['minutes_per_block']
        blocks_per_era = self.supply_data['blocks_per_era']
        full_cap = self.supply_data['full_cap']

        if not full_cap:
            full_cap = 1e100 # nearly infinite

        coins = 0
        for era, start_block in enumerate(range(0, full_cap, blocks_per_era), 1):
            end_block = start_block + blocks_per_era
            reward = start_coins_per_block / float(2 ** (era - 1))
            if block_height < end_block:
                blocks_this_era = block_height - start_block
                coins += blocks_this_era * reward
                break

            coins += reward * blocks_per_era

        return coins
