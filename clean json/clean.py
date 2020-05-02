import json

with open('city.list.json', encoding='utf_8') as data_file:
    data = json.load(data_file)

for element in data:
    del element['coord']

with open('cleaned_city.list.json', 'w') as data_file:
    data = json.dump(data, data_file)
    
 
