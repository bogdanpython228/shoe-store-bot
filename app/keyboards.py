from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_item

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Каталог')],
                                     [KeyboardButton(text='Корзина')],
                                     [KeyboardButton(text='Контакты'),
                                      KeyboardButton(text='О нас')]],
                           one_time_keyboard=True,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
    return keyboard.adjust(2).as_markup()


def item_kb(item_id):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить в корзину', callback_data=f"fav_{item_id}")],
    [InlineKeyboardButton(text='В главное меню', callback_data='to_main')]])

bebra = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Очистить корзину', callback_data='delete')],
    [InlineKeyboardButton(text='Назад', callback_data='to_main')]])

back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', 
                                                                      callback_data='to_main')]])