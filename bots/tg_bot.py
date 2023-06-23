import logging
import os
import re
import textwrap

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from bots.tg_logger import TelegramLogsHandler
from shop.elasticpath import (
    get_shop_token,
    get_products,
    get_product,
    get_price,
    get_stock,
    get_image,
    add_to_cart,
    get_cart,
    delete_from_cart,
    check_customer,
    create_customer,
)

logger = logging.getLogger(__file__)


def error_handler(_, context):
    logger.error(f'FishBot error: ', exc_info=context.error)


def start(update, context):
    shop_token = get_shop_token(
        context.bot_data['base_url'],
        context.bot_data['client_id'],
        context.bot_data['client_secret']
    )
    products = get_products(context.bot_data['base_url'], shop_token)
    keyboard = [
        [
            InlineKeyboardButton(
                product['attributes']['name'], callback_data=product['id']
            ) for product in products
        ]
    ]
    user = update.effective_user
    firstname = user.first_name if user.first_name else ''
    lastname = user.last_name if user.last_name else ''
    update.message.reply_text(
        text=textwrap.dedent(
            f'''Здравствуйте, {firstname} {lastname}
            Добро пожаловать в рыбный магазин! 
            Выберите, пожалуйста, что Вас интересует:'''
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    update.message.delete()
    return 'HANDLE_DESCRIPTION'


def handler_menu(update, context):
    shop_token = get_shop_token(
        context.bot_data['base_url'],
        context.bot_data['client_id'],
        context.bot_data['client_secret']
    )
    products = get_products(context.bot_data['base_url'], shop_token)
    keyboard = [
        [
            InlineKeyboardButton(
                product['attributes']['name'], callback_data=product['id']
            ) for product in products
        ],
        [InlineKeyboardButton('Корзина', callback_data='SHOP_CART')],
    ]
    query = update.callback_query
    query.answer()
    query.message.reply_text(
        'Выберите, пожалуйста, что Вас интересует:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    query.message.delete()
    return 'HANDLE_DESCRIPTION'


def handler_cart(update, context):
    query = update.callback_query

    shop_token = get_shop_token(
        context.bot_data['base_url'],
        context.bot_data['client_id'],
        context.bot_data['client_secret']
    )

    if query.data == 'BACK_TO_MENU':
        handler_menu(update, context)
        return 'HANDLE_DESCRIPTION'

    if query.data[:6] == 'DELETE':
        _, product_id = query.data.split()
        delete_from_cart(
            context.bot_data['base_url'],
            shop_token,
            query.message.chat_id,
            product_id
        )

    if query.data == 'TO_PAY':
        keyboard = [
            [InlineKeyboardButton('В меню', callback_data='BACK_TO_MENU')]
        ]
        query.message.reply_text(
            text='Для оплаты, пожалуйста, укажите Ваш email',
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        query.message.delete()
        return 'WAITING_EMAIL'

    items, price = get_cart(
        context.bot_data['base_url'],
        shop_token,
        query.message.chat_id,
    )
    text = ''
    keyboard = []
    cart_image = 'cart_.jpg' if items else 'cart.jpeg'
    for item in items:
        text += f'''
        {item["name"]}
        {item["description"]}
        ${item["unit_price"]["amount"] / 100} per kg
        {item["quantity"]}kg in cart for ${item["value"]["amount"] / 100}
        '''
        keyboard.append(
            [
                InlineKeyboardButton(
                    f'Убрать из корзины {item["name"]}',
                    callback_data=f'DELETE {item["id"]}'
                )
            ]
        )
    text += f'Total: ${price / 100}' if items else 'Cart is empty'
    if items:
        keyboard.append(
            [InlineKeyboardButton('Оплатить', callback_data='TO_PAY')]
        )
    keyboard.append(
        [InlineKeyboardButton('В меню', callback_data='BACK_TO_MENU')]
    )
    with open(os.path.normpath(f'{os.getcwd()}/assets/{cart_image}')) as photo:
        query.message.reply_photo(
            photo=photo,
            caption=textwrap.dedent(text),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    query.message.delete()
    return 'HANDLE_CART'


def handler_email(update, context):
    shop_token = get_shop_token(
        context.bot_data['base_url'],
        context.bot_data['client_id'],
        context.bot_data['client_secret']
    )
    query = update.callback_query
    if query:
        if query.data == 'BACK_TO_MENU':
            handler_menu(update, context)
            return 'HANDLE_DESCRIPTION'

        if query.data[:3] == 'YES':
            user = update.effective_user
            firstname = user.first_name if user.first_name else ''
            lastname = user.last_name if user.last_name else ''
            name = f'{firstname} {lastname}'.strip()
            _, user_email = query.data.split()
            if not check_customer(
                    context.bot_data['base_url'], shop_token, name, user_email
            ):
                create_customer(
                    context.bot_data['base_url'], shop_token, name, user_email
                )
            query.message.reply_text(
                f'{name}, спасибо за заказ. '
                f'В ближайшее время с Вами свяжуться '
                f'для завершения его оформления.'
            )
            query.message.delete()
            return 'WAITING_EMAIL'

    chat_id = update.message.chat_id
    state = context.bot_data['db'].get(str(f'Chat::{chat_id}')).decode('utf-8')
    if state != 'WAITING_EMAIL':
        update.message.delete()
        return
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$'
    user_email = update.message.text
    if re.match(email_pattern, user_email):
        user = update.effective_user
        firstname = user.first_name if user.first_name else ''
        lastname = user.last_name if user.last_name else ''
        keyboard = [
            [
                InlineKeyboardButton('Да', callback_data=f'YES {user_email}'),
                InlineKeyboardButton('Нет', callback_data='NO')
            ]
        ]
        update.message.reply_text(
            f'{firstname} {lastname}, {update.message.text} - это Ваш Email?',
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        update.message.delete()
        return 'WAITING_EMAIL'
    update.message.reply_text(f'Email: {user_email} не корректен!')
    update.message.delete()


def handler_description(update, context):
    shop_token = get_shop_token(
        context.bot_data['base_url'],
        context.bot_data['client_id'],
        context.bot_data['client_secret']
    )
    query = update.callback_query
    query.answer()

    if query.data[:4] == 'CART':
        _, quantity, product_id = query.data.split()
        add_to_cart(
            context.bot_data['base_url'],
            shop_token,
            product_id,
            int(quantity),
            query.message.chat_id
        )
        handler_cart(update, context)
        return 'HANDLE_CART'

    if query.data == 'SHOP_CART':
        handler_cart(update, context)
        return 'HANDLE_CART'

    if query.data == 'BACK':
        handler_menu(update, context)
        return 'HANDLE_DESCRIPTION'

    product = get_product(context.bot_data['base_url'], shop_token, query.data)
    price = get_price(context.bot_data['base_url'], shop_token, query.data)
    stock = get_stock(context.bot_data['base_url'], shop_token, query.data)
    image_id = product['relationships']['main_image']['data']['id']
    image_url = get_image(context.bot_data['base_url'], shop_token, image_id)
    text = textwrap.dedent(
        f'''
        {product["attributes"]["name"]}
        
        ${price / 100} per kg.
        {stock}kg on stock
        
        {product["attributes"].get("description")}'''
    )
    keyboard = [
        [InlineKeyboardButton('1кг', callback_data=f'CART 1 {query.data}'),
         InlineKeyboardButton('5кг', callback_data=f'CART 5 {query.data}'),
         InlineKeyboardButton('10кг', callback_data=f'CART 10 {query.data}')],
        [InlineKeyboardButton('Корзина', callback_data='SHOP_CART')],
        [InlineKeyboardButton('Назад', callback_data='BACK')],
    ]
    query.message.reply_photo(
        photo=image_url,
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    query.message.delete()
    return 'HANDLE_DESCRIPTION'


def handler_user_reply(update, context):
    db = context.bot_data['db']
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        query = update.callback_query
        query.answer()
        user_reply = query.data
        chat_id = query.message.chat_id
    else:
        return

    if user_reply == '/start' or not db.get(str(f'Chat::{chat_id}')):
        user_state = 'START'
    else:
        user_state = db.get(str(f'Chat::{chat_id}')).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handler_menu,
        'HANDLE_DESCRIPTION': handler_description,
        'HANDLE_CART': handler_cart,
        'WAITING_EMAIL': handler_email,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(str(f'Chat::{chat_id}'), next_state)


def telegram_bot(token, base_url, client_id, client_secret, db, log_token, dev_chat):
    logger_bot = telegram.Bot(token=log_token)
    logger.setLevel(logging.INFO)
    logger.addHandler(
        TelegramLogsHandler(logger_bot, dev_chat)
    )
    bot = Updater(token)
    dispatcher = bot.dispatcher
    dispatcher.bot_data['base_url'] = base_url
    dispatcher.bot_data['client_id'] = client_id
    dispatcher.bot_data['client_secret'] = client_secret
    dispatcher.bot_data['db'] = db
    dispatcher.add_handler(CallbackQueryHandler(handler_user_reply))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r'/start'), handler_user_reply)
    )
    dispatcher.add_handler(MessageHandler(Filters.text, handler_email))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_error_handler(error_handler)

    bot.start_polling()
    bot.idle()
