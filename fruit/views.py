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

API_KEY = "0vgoHqEhtTZk/b0cE+I1JV+Xrw6x7lXm"
API_ROOT = "https://marsapi.ams.usda.gov/services/v1.2/reports/2314"

def get_report(end_date=None, commodity=None, duration=None):
    if end_date is None:
        end_date = timezone.now() - timedelta(days=1)
    date_str = end_date.strftime('%m/%d/%Y')
    if duration is not None:
        start_date = end_date - duration
        date_str = start_date.strftime('%m/%d/%Y') + ':' + date_str

    filter_str = date_str
    if commodity:
        filter_str += f';commodity={commodity}'
    url = f'{API_ROOT}?q=report_begin_date={filter_str}&allSections=true'

    # check cache
    path = f'cache/{filter_str.replace("/", "_")}.json'
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    # cache miss, get response
    response = requests.post(url, auth=(API_KEY, API_KEY))
    if not response.ok:
        return {"error": "error"}
    data = response.json()
    # and save to cache
    if not os.path.isdir("cache"):
        os.makedirs("cache")
    with open(path, 'w') as f:
        json.dump(data, f)

    return data

def get_weather(report):
    if not report:
        report = [{}]
    results = report[0].get('results', [{}])
    if not results:
        results = [{}]
    return results[0].get("report_narrative", "couldn't find weather :(")

def get_fruits(report):
    if not report:
        report = [{}]
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

def get_fruit_price(fruit_arr):
    """
    Gets the average price for a fruit
    TODO: make this unit price?
    """
    prices = [float(fruit['low_price']) for fruit in fruit_arr if fruit.get('low_price')]
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
    prev_fruits = get_fruits(get_report(end_date=date-timedelta(days=1)))

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
        date = datetime.now() - timedelta(days=1)
    if date + timedelta(days=1) < today:
        next_date = date + timedelta(days=1)
    report = get_report(end_date=date)

    context = {
        "date": date,
        "prev_date": date - timedelta(days=1),
        "next_date": next_date,
        "weather": get_weather(report),
        "fruits": get_marquee(date),
        "report_view": True,
    }
    return render(request, 'fruit/report.html', context)


def consolidate_fruits(fruit_arr):
    """
    Take in a list of fruits and then return a single
    dictionary where the values are comma separated values of
    all values present
    """
    combined_dict = {}
    for d in fruit_arr:
        for key, value in d.items():
            if key not in combined_dict:
                combined_dict[key] = set()
            combined_dict[key].add(value)

    #for key in combined_dict.keys():
    #    str_list = sorted([str(i) for i in list(combined_dict[key])])
    #    combined_dict[key] = ', '.join(str_list)
    return combined_dict

def commodity(request, fruit_slug=None):
    date = datetime.now() - timedelta(days=1)
    fruits = get_marquee(date)
    fruit = None
    if fruit_slug:
        for f in fruits.keys():
            if slugify(f) == fruit_slug:
                fruit =  f
                break
    if fruit_slug is not None and fruit is None:
        messages.error(request, 'not a valid fruit :(')
        return HttpResponseRedirect(reverse('fruit:index'))

    entry = None
    if fruit:
        report = get_report(commodity=fruit, duration=timedelta(days=365), end_date=date)
        table = get_fruits(report).get(fruit, [])

        #table_paged = Paginator(table, 20)
        #page = request.GET.get('page')
        table_grouped = groupby(table, key = itemgetter('report_begin_date'))
        table_grouped = [consolidate_fruits(entry) for date, entry in table_grouped]
        table_grouped_paged = Paginator(table_grouped, 20)
        page = request.GET.get('page')
        entry = {
            "year_table": table,
            "table_grouped": table_grouped,
            "table_grouped_paged": table_grouped_paged.get_page(page),
            "varieties": sorted(list(set([e.get('variety') for e in table]))),
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

