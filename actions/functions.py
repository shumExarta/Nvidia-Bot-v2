from thefuzz import fuzz, process
import random
import requests
import json

with open('./products_list.json', 'r') as file:
    original_json_file = json.load(file)

# API INTEGRATIONS FOR GETTING PRODUCT DATA
def get_data_from_api():
    url = "http://172.16.15.217:8000/api/product_list"
    response = requests.get(url=url)
    data = response.json()
    product_list = data['product_list']
    
    if (product_list != original_json_file):
        print("Data is changed. Updating JSON file.")
        with open('./products.json', 'w') as file:
            json.dump(product_list, file)
    else:
        print('Data is not changed. No need to update the JSON file')
    
    with open('./products_list.json', 'w') as file:
        json.dump(product_list, file, indent=4)
        
    product_names = [item['name'] for item in product_list]

    return product_list, product_names

# SENDING DATA TO RAG API AND GETTING RESPONSE FROM THERE
def send_data_to_rag(text):
    url = "http://172.16.15.217:8000/api/rag"
    data = {'text': text}
    response = requests.post(url=url, json=data['text'])
        
    return response.json()

# GETTING PRODUCT NAME FROM THE PRODUCT LIST
def get_product(productName, productList):
    for product in productList:
        if product['name'] == productName :
            return product

# GETTING PRODUCTS POSITION FROM THE LIST
def get_product_position(productName, productList):
    for product in productList:
        if product['name'] == productName:
            x = product["itemTransform"]["translation"]["x"]
            y = product["itemTransform"]["translation"]["y"]
            z = product["itemTransform"]["translation"]["z"]

    return x, y, z

# CREATING JSON TO SEND TO UNREAL
def createJson(
    iD=None,
    name=None,
    desc=None,
    price=None,
    rotation=None,
    translation=None,
    scale3D=None,
    action=None,
    additionalInformation=None,
    **kwargs,
):
    dict_json = {
        'iD': iD,
        'name': name,
        'desc': desc,
        'price': price,
        'itemTransform': {
            'rotation': rotation,
            'translation': translation,
            'scale3D': scale3D,
        },
        'action': action,
        'additionalInformation': additionalInformation
    }
    # def format_value(value):
    #     if value is None:
    #         return '"None"'
    #     if isinstance(value, (dict, list)):
    #         return json.dumps(value)
    #     return f'"{value}"'
    
    # dict_str = f'''{{
    #     "product_id": {format_value(product_id)},
    #     "name": {format_value(name)},
    #     "desc": {format_value(desc)},
    #     "price": {format_value(price)},
    #     "itemTransform": 
    #     {{
    #         "rotation": {format_value(rotation)},
    #         "translation": {format_value(translation)},
    #         "scale3D": {format_value(scale3D)}
    #     }},
    #     "action": {format_value(action)},
    #     "additionalInformation": {format_value(additionalInformation)}
    # }}'''

    return dict_json

# FUNCTION FOR MAINTAING THE STATES
def state_maintain(
    iD=None,
    name=None,
    desc=None,
    price=None,
    **kwargs,):
    
    state_dict = {
        'iD': iD,
        'name': name,
        'desc': desc,
        'price': price,
    }
    
    return state_dict