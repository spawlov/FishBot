import datetime
import json

import requests


def save_token_data(url, data):
    response = requests.post(url, data=data)
    response.raise_for_status()
    token_data = response.json()
    with open('.token', 'w') as file:
        json.dump(token_data, file)
    return token_data


def get_shop_token(base_url, client, secret):
    url = f'{base_url}/oauth/access_token'
    data = {
        'client_id': client,
        'client_secret': secret,
        'grant_type': 'client_credentials',
    }
    try:
        with open('.token', 'r') as file:
            token_data = json.load(file)
        if token_data['expires'] <= datetime.datetime.now().timestamp():
            return save_token_data(url, data)['access_token']
        return token_data['access_token']
    except FileNotFoundError:
        return save_token_data(url, data)['access_token']


def get_products(base_url, token):
    url = f'{base_url}/pcm/products'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product(base_url, token, product_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/pcm/products/{product_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_price(base_url, token, product_id):
    headers = {'Authorization': f'Bearer {token}'}
    data = {'include': 'prices'}
    url = f'{base_url}/catalog/products/{product_id}'
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()['data']['attributes']['price']['USD']['amount']


def get_stock(base_url, token, product_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/v2/inventories/{product_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['available']


def get_image(base_url, token, image_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/v2/files/{image_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def add_to_cart(base_url, token, product_id, quantity, customer_id):
    url = f'{base_url}/v2/carts/{customer_id}/items'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity
        }
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.status_code


def get_cart(base_url, token, customer_id):
    url = f'{base_url}/v2/carts/{customer_id}/items'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']

    url = f'{base_url}/v2/carts/{customer_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_sum = response.json()['data']['meta']['display_price']['with_tax']['amount']

    return cart_items, cart_sum


def delete_from_cart(base_url, token, customer_id, product_id):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/v2/carts/{customer_id}/items/{product_id}'
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.status_code


def check_customer(base_url, token, name, email):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/v2/customers'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    customers = response.json()['data']
    for customer in customers:
        if all([name == customer['name'], email == customer['email']]):
            return customer['id']
    return None


def create_customer(base_url, token, name, email):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}/v2/customers'
    data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
            'password': '',
        },
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']

