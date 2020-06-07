''' Изучить список открытых API. Найти среди них любое, требующее авторизацию
 (любого типа). Выполнить запросы к нему, пройдя авторизацию.
 Ответ сервера записать в файл.'''


import requests

link = 'https://onlinesim.ru/api/getBalance.php?apikey=c5111a022df9aad1eb2f38904f88704f'
api_key = 'c5111a022df9aad1eb2f38904f88704f'
params = {'apikey':api_key}

res = requests.get(link, params=params)


with open('balance.json', 'w') as f:
    f.write(res.text)
