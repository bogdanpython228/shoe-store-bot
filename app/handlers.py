from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import app.keyboards as kb
import app.database.requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.add_user(message.from_user.id)
    await message.answer('Добро пожаловать в магазин кроссовок!', reply_markup=kb.main)


@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())


@router.message(F.text == 'Корзина')
async def favorites(message: Message):
    items = await rq.get_favorites(message.from_user.id)
    
    if not items:
        await message.answer('Ваша корзина пустая.')
        return
    
    response = 'Ваша корзина:\n\n'
    total_price = 0
    total_count = 0
    for i, fav in enumerate(items, 1):
        response += f'{i}. {fav.item.name}\n'
        response += f'Цена: {fav.item.price}$\n'
        response += '\n'
        total_price += fav.item.price
        total_count += 1
        
    response += f'Всего товаров: {total_count}\n'
    response += f'Итого: {total_price}$'
        
    await message.answer(response, reply_markup=kb.bebra)


@router.message(F.text == 'Контакты')
async def contacts(message: Message):
    await message.answer('Адрес: Сзади тебя\n'
                         'Телефон: +7 (800) 555-35-35\n'
                         'Email: bebra443@gmail.com',
                         reply_markup=kb.back)


@router.message(F.text == 'О нас')
async def about_us(message: Message):
    await message.answer('Добро пожаловать в магазин кроссовок – ваш надежный источник стильных и '
                         'качественных кроссовок! Мы предлагаем только оригинальные модели от '
                         'ведущих мировых брендов, таких как Nike, Adidas и New Balance. Наша '
                         'миссия – помогать вам выглядеть модно и чувствовать себя комфортно в '
                         'любой ситуации. Мы тщательно отбираем ассортимент, чтобы вы могли найти '
                         'идеальную пару для спорта, повседневной носки или особых случаев.',
                         reply_markup=kb.back)


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    category_id = (callback.data.split('_')[1])
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите товар по категории',
                                  reply_markup=await kb.items(category_id))


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_id = callback.data.split('_')[1]
    item = await rq.get_item(item_id)
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(f'Название: {item.name}\nОписание: {item.description}\n'
                                  f'Цена: {item.price}$',
                                  reply_markup=kb.item_kb(item_id))
    
    
@router.callback_query(F.data.startswith('fav_'))
async def add_favorite(callback: CallbackQuery):
    item_id = callback.data.split('_')[1]
    item = await rq.get_item(item_id)

    if not item:
        await callback.message.answer('Произошла ошибка.')
        return

    success = await rq.add_to_favorites(callback.from_user.id, item_id)
    
    if success:
        await callback.answer(f"{item.name} добавлены в корзину!")
    else:
        await callback.answer(f"{item.name} уже в корзине.")


@router.callback_query(F.data == 'delete')
async def delete_favorites(callback: CallbackQuery):
    await rq.delete_favorites(callback.from_user.id)
    await callback.answer('Корзина пустая!')
    await callback.message.answer('Корзина теперь пустая.')


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Главное меню', reply_markup=kb.main)