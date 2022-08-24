# I3 blocks kW/h price for energi

Provides a script for showing how much energy costs right now. This is done using the [Enrgi West API](https://nrgi.dk/api/common/pricehistory?region=DK1&date=2022-8-24). It returns the price for the current hour and stores it in a JSON object. Maybe changing it later to be a SQLite database.


# Using
Clone the repo into your I3blocks folder (typically `~/.config/i3blocks/`). Then add the I3 block below into your `config` file:

```
[Energy]
markup=pango
command=~/.config/i3blocks/i3-energi-tracker/main.py now
background=#000000
interval=600
```


# Todo:

Some todo items:
- [ ] Pick some better colors for the block
- [ ] Add configuration for selecting ranges
  - [ ] Add cli configuration for cutoffs (setting COLOR_MIN and COLOR_MAX via cli)
  - [ ] Add a setting for selecting coloring based on percentage of highest and lowest price for the day
- [ ] Add a on click event that shows a table of prices for the whole day