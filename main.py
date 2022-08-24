#!/usr/bin/python

from fileinput import filename
import json
from datetime import datetime, date
import os
import sys
from urllib import request

# File for getting the energi prices for Denmark West Market. 
# It writes the energy prices to a json file in the data folder.
# It also shows the data as a I3 blocks compatible output.

url = "https://nrgi.dk/api/common/pricehistory?region=DK1&date="
COLORS = ["#25AA00", "#72A300", "#BD9A00", "#EA7500", "#FF4400"]

MIN_COLOR = 200 # lower bound for øre price
MAX_COLOR = 800 # upper bound for øre price

def get_energi_prices(date_obj: date = date.today()) -> dict:
    """Get the prices for the given data.

    Args:
        date_obj (date, optional): Get the prices according to the date object. Defaults to date.today().

    Raises:
        ValueError: If the get request fails return the status code as an error.

    Returns:
        dict: dictionary with the loaded prices.
    """
    prices = request.urlopen(url+date_obj.isoformat())
    if prices.status != 200:
        raise ValueError(f"Status code {prices.status_code}: Couldn't get the data for energi prices.")
    return json.loads(prices.read())


def write_prices_file(date_obj: date = date.today()) -> str:
    """Write the prices to a JSON file.

    Args:
        date_obj (date, optional): The date for the prices. Defaults to date.today().

    Returns:
        str: The filename for the newly written file.
    """
    filename = f"prices-{date_obj.isoformat()}.json"
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(path, "w") as file:
        prices = get_energi_prices(date_obj)
        file.write(json.dumps(prices))
    return filename 

def read_prices_file(date_obj: date = date.today()):
    filename = f"prices-{date_obj.isoformat()}.json"
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    if not os.path.exists(path):
        # If there is no data file then write them to it.
        write_prices_file(date_obj)
    with open(path, "r") as file:
        try:
            return json.loads(file.read())
        except json.JSONDecodeError as e:
            print("Failed to parse JSON data.")
            return None

def format_price(price: int) -> str:
    """Format the price from øre to dkk

    Args:
        price (int): The price

    Returns:
        str: String reprensation of the price in dkk.
    """

    return f"{price/100:.2f} DKK"

def output_hour_price(date_obj: date = date.today(), hour: int = datetime.now().hour) -> int:
    """Print the energy price for the given data and hour.

    Args:
        date_obj (date, optional): The date. Defaults to date.today().
        hour (int, optional): Which hour to select. Defaults to datetime.now().hour.

    Returns:
        int: price in øre
    """
    prices = read_prices_file(date_obj)
    current_hour_price = prices["prices"][hour]["priceInclVat"]
    # print(f"kW/h {format_price(current_hour_price)} dkk \n\n{output_hour_price_background()}")
    print(f"<span bgcolor=\"{output_hour_price_background()}\"> kW/h {format_price(current_hour_price)} </span>")

def output_hour_price_background(date_obj: date = date.today(), hour: int = datetime.now().hour) -> str:
    prices = read_prices_file(date_obj)
    current_hour_price = prices["prices"][hour]["priceInclVat"]


    if current_hour_price < MIN_COLOR:
        return(COLORS[0])
    elif current_hour_price > MAX_COLOR:
        return(COLORS[-1])
    else:
        vrange = MAX_COLOR - MIN_COLOR
        colors = COLORS[1:-2]
        vrange_interval = vrange // len(colors)
        index = (current_hour_price - MIN_COLOR) // vrange_interval
        #print(f"index is {index+1} and vrange is {vrange_interval} and value is {MIN_COLOR + ((index+1) * vrange_interval)}")
        return(colors[index])



def output_day_price(date_obj: date = date.today()) -> str:
    """Output the day prices as a str

    Args:
        date_obj (date, optional): Date you want to see. Defaults to date.today().

    Returns:
        str: str ouput of the day.
    """
    prices = read_prices_file(date_obj)
    day = {}
    for  hour, data in enumerate(prices["prices"]):
        # Add one since it 0 indexes
        day[hour+1] = format_price(data["priceInclVat"])
    print(day)


if __name__ == "__main__":
    args = sys.argv[1:]
    menu = """\
        Print the energy price for the current hour.
        commands:
                -h, h: Help menu.
                now: current price for the hour
                background: The color background for the current hour
        """
    if len(args) < 1:
        print(menu)
    elif args[0] == "now":
        output_hour_price()
    elif args[0] == "background":
        output_hour_price_background()
    elif args[0] == '-h' or args[0] == "h":
        print(menu)
    else:
        print("Please use the arg 'now' or 'background'")
    
