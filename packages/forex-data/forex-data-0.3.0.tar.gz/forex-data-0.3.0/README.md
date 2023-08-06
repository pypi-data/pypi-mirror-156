# Forex Data Get and Process
A small demo library for getting forex data and process it

### Installation
```
pip install forex-data
```

### Get started
How to pass currency pairs to process it:

```Python
from forex_data import portfolio
from forex_data import get_process
from forex_data import get_process_agg

currency_pairs = [["AUD","USD",[],portfolio("AUD","USD")],
                  ["GBP","EUR",[],portfolio("GBP","EUR")],
                  ["USD","CAD",[],portfolio("USD","CAD")]]

get_process(currency_pairs, "sqlite_hw1/test.db", 86400, 360)   # 86400=24h, 360=6min

# get_process(currency_pairs, db_path, total_run_time, aggregate_time)
# time should be seconds

currency_pairs = [["AUD", "USD"],["GBP","EUR"], ["USD","CAD"]]
for cur in currency_pairs:
    get_process_agg(cur, "sqlite_hw3/aggfive.db", 7200, 36000, 360)
    # don't collect for the first 20 periods(20*6min=20*360s=7200s), run 10h(36000s), aggregate each 6 min
```