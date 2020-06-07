'''1. Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев для конкретного пользователя,
 сохранить JSON-вывод в файле *.json.'''

import requests

user_name = 'alikin-alexey'
link = f'https://api.github.com/users/{user_name}/repos'

result = requests.get(link)
with open('repos.json', 'w') as f:
    f.write(result.text.strip('[]'))




