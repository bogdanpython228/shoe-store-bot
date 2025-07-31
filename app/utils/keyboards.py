from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.database.requests import get_categories, get_category_item

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Админ-панель')], 
    [KeyboardButton(text='Каталог')],
    [KeyboardButton(text='Корзина')],
    [KeyboardButton(text='Контакты'), KeyboardButton(text='О нас')]],
                           one_time_keyboard=True,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

admin_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить'), KeyboardButton(text='Удалить')],
    [KeyboardButton(text='Выйти')]],
                                 one_time_keyboard=True,
                                 resize_keyboard=True,
                                 input_field_placeholder='Выберите пункт меню...')


async def build_reply_keyboard(items, placeholder):
    keyboard = ReplyKeyboardBuilder()
    for item in items:
        keyboard.add(KeyboardButton(text=item.name))
    return keyboard.adjust(2).as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=placeholder
    )


async def category():
    '''Создает реплай-клавиатуру со списком всех категорий'''
    return await build_reply_keyboard(
        await get_categories(),
        'Выберите категорию...'
    )


async def del_item(category_id: int):
    '''Создает реплай-клавиатуру со списком всех товаров из выбранной категории'''
    return await build_reply_keyboard(
        await get_category_item(category_id),
        'Выберите товар...'
    )


async def categories():
    '''Создает инлайн-клавиатуру со списком всех категорий.'''
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name,
                                          callback_data=f"category_{category.id}"))
    return keyboard.adjust(2).as_markup()


async def items(category_id: int):
    '''Создает инлайн-клавиатуру со списком всех товаров из выбранной категории.'''
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, 
                                          callback_data=f"item_{item.id}"))
    return keyboard.adjust(2).as_markup()


category_or_item = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Категория'), KeyboardButton(text='Товар')]],
                                       resize_keyboard=True,
                                       one_time_keyboard=True)

def item_kb(item_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить в корзину', callback_data=f"fav_{item_id}")],
    [InlineKeyboardButton(text='В главное меню', callback_data='to_main')]])

cart_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Очистить корзину', callback_data='delete')],
    [InlineKeyboardButton(text='Назад', callback_data='to_main')]])

back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', 
                                                                      callback_data='to_main')]])