from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator

import requests
from django.utils import timezone
from datetime import datetime, timedelta, time
import os
import json
import re
from itertools import groupby
from operator import itemgetter

API_KEY = "0vgoHqEhtTZk/b0cE+I1JWgeP4aAEmpfCDsJEhz61Ic="
API_ROOT = "https://marsapi.ams.usda.gov/services/v1.2/reports/2314"
MAX_RANGE = 365 # one year of days

def prev_date(date = None, reverse=False):
    """
    Return the previous weekday to an inputted date
    """
    if date is None:
        date = datetime.now()
    sign = -1 if reverse else 1
    date -= timedelta(days=sign * 1)
    if ((not reverse and date.weekday() == 5) or
        (reverse and date.weekday() == 6)):
        return date - timedelta(days=sign * 1)
    elif ((not reverse and date.weekday() == 6) or
          (reverse and date.weekday() == 5)):
        return date - timedelta(days=sign * 2)
    return date

def get_report(end_date=None, commodity=None, duration=None):
    if end_date is None:
        end_date = prev_date()
    date_str = end_date.strftime('%m/%d/%Y')
    if duration is not None:
        start_date = end_date - duration
        date_str = start_date.strftime('%m/%d/%Y') + ':' + date_str

    filter_str = date_str
    if commodity:
        filter_str += f';commodity={commodity}'
    url = f'{API_ROOT}?q=report_begin_date={filter_str}&allSections=true'

    # check cache
    #commodity_path = f'{slugify(commodity)}/' if commodity else ''
    # TODO
    commodity_path = ''
    path = f'cache/{commodity_path}{filter_str.replace("/", "_")}.json'
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    # cache miss, get response
    response = requests.get(url, auth=(API_KEY, ""))
    if not response.ok:
        return [{"error": "error"}]
    data = response.json()
    # and save to cache
    if not os.path.isdir("cache"):
        os.makedirs("cache")
    with open(path, 'w') as f:
        json.dump(data, f)

    return data

# given a report, return the weather
def get_weather(report):
    if not report:
        report = [{}]
    results = report[0].get('results', [{}])
    if not results:
        results = [{}]
    return results[0].get("report_narrative", "couldn't find weather :(")

# given a report, return the fruits in that report
def get_fruits(report):
    if not report:
        report = [{}, {}]
    entries = report[1].get('results', [])
    fruits = {}
    for entry in entries:
        fruit = entry.get("commodity")
        if not fruit:
            continue
        fruit_arr = fruits.get(fruit, [])
        fruit_arr.append(entry)
        fruits[fruit] = fruit_arr
    return dict(sorted(fruits.items()))


def isfloat(value):
    """
    Returns true if a value is a float or can be casted into one
    """
    if type(value) is float or type(value) is int:
        return True
    elif type(value) is str:
        return value.replace('.', '', 1).isdigit()
    return False

def get_fruit_price(fruit_arr, dir="low"):
    """
    Gets the mean price for a fruit
    TODO: make this unit price?
    """
    prices = [float(fruit[f'{dir}_price']) for fruit in fruit_arr if isfloat(fruit.get(f'{dir}_price'))]
    return sum(prices) / len(prices) if len(prices) else 0

def get_market_tone(fruit_arr):
    market_tone = None
    offerings_comments = None
    has_offerings = False
    for fruit in fruit_arr:
        if fruit.get('market_tone_comments'):
            market_tone = fruit['market_tone_comments']
        if fruit.get('offerings_comments'):
            offerings_comments = fruit['offerings_comments']
    if ((market_tone and re.search(r'\blow', market_tone, re.IGNORECASE)) or
        (offerings_comments)):
        has_offerings = True
    response = offerings_comments if offerings_comments else market_tone
    return response, has_offerings

def get_marquee(date):
    fruits = get_fruits(get_report(end_date=date))
    prev_fruits = get_fruits(get_report(end_date=prev_date(date)))

    marquee = {}
    for fruit, entries in fruits.items():
        avg_price = get_fruit_price(entries)
        prev_avg_price = get_fruit_price(prev_fruits.get(fruit, []))
        is_up = avg_price > prev_avg_price
        is_down = avg_price < prev_avg_price
        market_tone, has_offerings = get_market_tone(entries)
        marquee[fruit] = {
            "dir": "up" if is_up else "down" if is_down else "neutral",
            "dir_symbol": "▲" if is_up else "▼" if is_down else "•︎",
            "price": avg_price,
            "market_tone": market_tone,
            "has_offerings": has_offerings,
            "table": entries,
        }
    return marquee

def daily_report(request, date=None):
    today = datetime.combine(datetime.now().date(), time.min)
    next_date = None
    if date is not None:
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        date = prev_date()
    if date + timedelta(days=1) < today:
        next_date = prev_date(date, reverse=True)
    report = get_report(end_date=date)

    context = {
        "date": date,
        "prev_date": prev_date(date),
        "next_date": next_date,
        "weather": get_weather(report),
        "fruits": get_marquee(date),
        "report_view": True,
    }
    return render(request, 'fruit/report.html', context)


def consolidate_fruits(fruit_arr, date):
    """
    Take in a list of fruits and then return a single
    dictionary where the values are comma separated values of
    all values present
    """

    def minmax(value, fn):
        arr = [float(x) for x in value if x and isfloat(x)]
        #if not arr:
        #    return "N/A"
        if not arr:
            return None
        return fn(arr)

    combined_dict = {}
    for d in fruit_arr:
        for key, value in d.items():
            if key not in combined_dict:
                combined_dict[key] = set()
            combined_dict[key].add(value)

    #for key in combined_dict.keys():
    #    str_list = sorted([str(i) for i in list(combined_dict[key])])
    #    combined_dict[key] = ', '.join(str_list)
    combined_dict["low_price"] = minmax(combined_dict.get('low_price', None), min)
    combined_dict["high_price"] = minmax(combined_dict.get('high_price', None), max)
    lo = combined_dict.get("low_price")
    hi = combined_dict.get("high_price")
    combined_dict['mean_price'] = (float(hi) + float(lo)) / 2.0 if isfloat(hi) and isfloat(lo) else 0

    date_obj = datetime.strptime(date, '%m/%d/%Y')
    combined_dict['date'] = date_obj
    combined_dict['date_str'] = datetime.strftime(date_obj, '%Y-%m-%d')
    return combined_dict

def get_chart_data(table_grouped):
    data = []
    """table = list(reversed(table_grouped))
    for i in range(len(table)):
        prev_entry = table[i - 1] if i >= 1 else {}
        entry = table[i]
        if entry.get("low_price") and entry.get("high_price"):
            open_price = prev_entry.get("mean_price", entry['mean_price'])
            data.append({
                "time": entry['date_str'],
                "open": open_price,
                "high": entry['high_price'],
                "low": entry['low_price'],
                "close": entry['mean_price'],
            })"""
    table = {entry['date_str']: entry for entry in table_grouped}
    date = table_grouped[-1]['date']
    end_date = table_grouped[0]['date']
    i = 0
    loop_count = 0
    prev_entry = {}
    while not (i >= len(table) or date == end_date or loop_count >= MAX_RANGE):
        date_str = datetime.strftime(date, '%Y-%m-%d')
        entry = table.get(date_str)
        if not (entry and entry.get("low_price") and entry.get("high_price")):
            data.append({"time": date_str})
        else:
            open_price = prev_entry.get("mean_price", entry['mean_price'])
            data.append({
                "time": entry['date_str'],
                "open": open_price,
                "high": entry['high_price'],
                "low": entry['low_price'],
                "close": entry['mean_price'],
            })
            i += 1
            prev_entry = entry
        date = date + timedelta(days=1)
        loop_count += 1
    return json.dumps(data)

def commodity(request, fruit_slug=None):
    date = prev_date()
    fruits = get_marquee(date)
    fruit = None
    if fruit_slug:
        for f in fruits.keys():
            if slugify(f) == fruit_slug:
                fruit =  f
                break
    if fruit_slug is not None and fruit is None:
        messages.error(request, 'not a valid fruit :(')
        return HttpResponseRedirect(reverse('fruit:list_commodities'))

    entry = None
    if fruit:
        report = get_report(commodity=fruit, duration=timedelta(days=MAX_RANGE), end_date=date)
        table = get_fruits(report).get(fruit, [])

        #table_paged = Paginator(table, 20)
        #page = request.GET.get('page')
        table_grouped = groupby(table, key = itemgetter('report_begin_date'))
        table_grouped = [consolidate_fruits(entry, date) for date, entry in table_grouped]
        table_grouped_paged = Paginator(table_grouped, 20)
        page = request.GET.get('page')
        entry = {
            "year_table": table,
            "table_grouped": table_grouped,
            "table_grouped_paged": table_grouped_paged.get_page(page),
            "varieties": sorted(list(set([e.get('variety') for e in table]))),
            "chart": get_chart_data(table_grouped),
        }
        entry.update(fruits[fruit]) # add other info from marquee

    context = {
        "commodity_view": True,
        "fruits": fruits,
        "fruit": fruit,
        "entry": entry,
        "date": date,
    }
    return render(request, 'fruit/commodity.html', context)

