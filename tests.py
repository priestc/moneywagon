import datetime

from moneywagon.supply_estimator import SupplyEstimator
from moneywagon.crypto_data import crypto_data

def test_blocktime_adjustments():
    sd = {
        'method': 'standard',
        'start_coins_per_block': 80,
        'minutes_per_block': 2,
        'blocktime_adjustments': [
            [4, 1],
            [9, 3]
        ],
        'full_cap': 336000000,
        'blocks_per_era': 2100000,
    }

    genesis = datetime.datetime(2017, 1, 1)

    crypto_data['tst'] = {
        'genesis_date': genesis,
        'supply_data': sd
    }

    for s in [SupplyEstimator('tst'), SupplyEstimator(genesis_date=genesis, supply_data=sd)]:
        assert s.estimate_date_from_height(10) == datetime.datetime(2017, 1, 1, 0, 16)
        assert s.estimate_date_from_height(11) == datetime.datetime(2017, 1, 1, 0, 19)
        assert s.estimate_date_from_height(4) == datetime.datetime(2017, 1, 1, 0, 8)
        assert s.estimate_date_from_height(9) == datetime.datetime(2017, 1, 1, 0, 13)

        assert s.estimate_height_from_date(datetime.datetime(2017, 1, 1, 0, 16)) == 10
        assert s.estimate_height_from_date(datetime.datetime(2017, 1, 1, 0, 19)) == 11
        assert s.estimate_height_from_date(datetime.datetime(2017, 1, 1, 0, 8)) == 4
        assert s.estimate_height_from_date(datetime.datetime(2017, 1, 1, 0, 13)) == 9




if __name__ == '__main__':
    test_blocktime_adjustments()
    print("all tests passed")
