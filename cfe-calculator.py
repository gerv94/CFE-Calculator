from datetime import datetime
import json

###############################################################################
# Test code
# TODO: get rates from CFE website
import requests
from bs4 import BeautifulSoup

base = 'https://app.cfe.mx/Aplicaciones/CCFE/Tarifas'
url = '{}/TarifasCRECasa/Casa.aspx'.format(base)
page = requests.get(url)

page = BeautifulSoup(page.content, "html.parser")
main = page.find("div", class_="postcontent")
results = main.find_all("a", attrs={"data-toggle": "tooltip"})

rates = {}
for result in results:
    rates[result.text] = result.get("href").replace('..', base)

###############################################################################
# Main code

def get_rates(date):
    year  = date.strftime('%Y')
    month = date.strftime("%m")
    
    with open('cfe-rates.json') as json_file:
        data = json.load(json_file)
    
    if year in data and month in data[year]:
        return data[year][month]
    else:
        print('No rates found for {}'.format(date))
        return None

def calculate_cost(kwh, rates):
    min  = 25
    cost = 0
    sub  = 0
    rest = kwh if kwh > min else min

    for rate in rates:
        if 'max' not in rate or kwh <= rate['max']:
            sub = rest * rate['cost']
        else:
            sub = rate['max'] * rate['cost']
            rest -= rate['max']
        cost += sub
        print('{}:\t\t${}'.format(rate['name'], round(sub, 2)))

    return cost


prev_date = datetime(2022, 4, 27)
curr_date = datetime(2022, 6, 28)

prev_lecture = 5266
curr_lecture = 5697

if __name__ == '__main__':
    rates         = get_rates(curr_date)
    delta         = curr_date - prev_date
    kwh_per_day   = (curr_lecture - prev_lecture) / delta.days
    kwh_per_month = kwh_per_day * 30
    print('From:\t{}'.format(prev_date.strftime('%Y-%m-%d')))
    print('To:\t{}'.format(curr_date.strftime('%Y-%m-%d')))
    print('')
    print('Days:\t\t{}'.format(delta.days))
    print('Kwh:\t\t{}'.format(curr_lecture - prev_lecture))
    print('')
    print('--Metrics--')
    print('Kwh per day:\t{}'.format(round(kwh_per_day, 2)))
    print('Kwh per month:\t{}'.format(round(kwh_per_month, 2)))
    print('')

    kwh   = curr_lecture - prev_lecture
    cost  = calculate_cost(kwh, rates)
    iva   = cost * 0.16
    total = cost + iva

    print('-----------------------')
    print('Subtotal:\t${}'.format(round(cost, 2)))
    print('IVA:\t\t${}'.format(round(iva, 2)))
    print('Total:\t\t${}'.format(round(total, 2)))
