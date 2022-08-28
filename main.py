#!/usr/bin/python

from fileinput import filename
import json
from datetime import datetime, date
import os
import sys
from urllib import request
from typing import Union


# File for getting the energi prices for Denmark West Market. 
# It writes the energy prices to a json file in the data folder.
# It also shows the data as a I3 blocks compatible output.


url = "https://nrgi.dk/api/common/pricehistory?region=DK1&date=" # This is for Denmark West data
# url = "https://nrgi.dk/api/common/pricehistory?region=DK2&date=" # This is for Denmark East data

COLORS = [
            '#00FF00', '#11FF00', '#22FF00', '#33FF00', '#44FF00', '#55FF00', 
            '#66FF00', '#77FF00', '#88FF00', '#99FF00', '#AAFF00', '#BBFF00',
            '#CCFF00', '#DDFF00', '#EEFF00', '#FFFF00', '#FFEE00', '#FFDD00',
            '#FFCC00', '#FFBB00', '#FFAA00', '#FF9900', '#FF8800', '#FF7700',
            '#FF6600', '#FF5500', '#FF4400', '#FF3300', '#FF2200', '#FF1100',
            '#FF0000'
        ]

class NoDataException(Exception):
    """No data available. API might be down?"""


MIN_COLOR = 250 # lower bound for øre price
MAX_COLOR = 700 # upper bound for øre price

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
        raise NoDataException(f"Status code {prices.status_code}: Couldn't get the data for energi prices.")
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
        try:
            prices = get_energi_prices(date_obj)
            file.write(json.dumps(prices))
        except NoDataException as e:
            raise NoDataException(e)
    return filename 

def read_prices_file(date_obj: date = date.today()) -> Union[dict, None]:
    """Read the json file for the given date.

    Args:
        date_obj (date, optional): The data object. Defaults to date.today().

    Returns:
        Union[dict, None]: return the date if it is there.
    """
    filename = f"prices-{date_obj.isoformat()}.json"
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    if not os.path.exists(path):
        # If there is no data file then write them to it.
        try:
            write_prices_file(date_obj)
        except NoDataException as e:
            return None
    # TODO: Handle the download of correct data better if the data file is corrupt
    with open(path, "r") as file:
        try:
            return json.loads(file.read())
        except json.JSONDecodeError as e:
            write_prices_file(date_obj)
            return None

def format_price(price: int) -> str:
    """Format the price from øre to dkk

    Args:
        price (int): The price

    Returns:
        str: String representation of the price in dkk.
    """

    return f"{price/100:.2f} DKK"

def output_hour_price(date_obj: date = date.today(), hour: int = datetime.now().hour) -> str:
    """Print the energy price for the given date and hour as a pango markup element.

    Args:
        date_obj (date, optional): The date. Defaults to date.today().
        hour (int, optional): Which hour to select. Defaults to datetime.now().hour.

    Returns:
        str: The pango markup element
    """
    prices = read_prices_file(date_obj)
    if prices == None:
        print("<span bgcolor=\"#FF0000\" fgcolor=\"#000000\"> Error loading data ...</span>")
    current_hour_price = prices["prices"][hour]["priceInclVat"]
    print(f"<span fgcolor=\"black\" bgcolor=\"{output_background(current_hour_price)}\"> kW/h {format_price(current_hour_price)} </span>")

def output_background(price: int) -> str:
    """Take an integer value and return a HEX color. Uses the MIN_COLOR and MAX_COLOR values to decide range of colors.

    Args:
        current_hour_price (int): the price

    Returns:
        str: _description_
    """
    if price <= MIN_COLOR:
        return(COLORS[0])
    elif price >= MAX_COLOR:
        return(COLORS[-1])
    else:
        # Split the colors into a range and select a color based on which interval they hit.
        colors = COLORS[1:-2] # remove the first and second color
        vrange = MAX_COLOR - MIN_COLOR # create the range
        vrange_interval = vrange // len(colors)
        index = (price - MIN_COLOR) // vrange_interval - 1
        return(colors[index])



def output_day_price(date_obj: date = date.today()) -> str:
    """
    Output the day prices as a html table. Needs to be change later.

    :param date_obj (date, optional): Date you want to see. Defaults to date.today().
    :return str: str ouput of the day.
    """
    prices = read_prices_file(date_obj)
    if prices == None:
        print("<span bgcolor=\"#FF0000\" fgcolor=\"#000000\"> Error loading data ...</span>")
    day = []
    day.append(f"The prices for {date_obj.isoformat()} are: \n")
    for hour, data in enumerate(prices["prices"]):

        # day.append(f"<tr><td>{hour}</td><td style=\"background-color: {output_background(data['priceInclVat'])}\"> {data['priceInclVat']} </td></tr>\n")
        day.append(f"<span color=\"{output_background(data['priceInclVat'])}\">Hour: {hour:02d} :  {format_price(data['priceInclVat'])}</span>\n")
    # print(''.join(day))
    sys.stdout.write(''.join(day))

if __name__ == "__main__":
    args = sys.argv[1:]
    menu = """\
        Print the energy price for the current hour.
        commands:
                -h, h: Help menu.
                now: Current price for the hour as a pango element
                day: Print the day as a html table rows
        """
    if len(args) < 1:
        print(menu)
    elif args[0] == "now":
        output_hour_price()
    elif args[0] == "day":
        output_day_price()
    elif args[0] == '-h' or args[0] == "h":
        print(menu)
    else:
        print("Please use the arg 'now' or 'day'")
    
