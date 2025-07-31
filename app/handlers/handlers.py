from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.utils.keyboards as kb
import app.database.requests as rq
from app.core.config import ADMIN

class States(StatesGroup):
    add_category_or_item = State()
    del_category_or_item = State()
    add_category = State()
    del_category = State()
    add_name_item = State()
    add_description_item = State()
    add_price_item = State()
    add_category_item = State()
    del_cat_item = State()
    del_item = State()

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.add_user(message.from_user.id)
    await message.answer('Добро пожаловать в магазин кроссовок!', reply_markup=kb.main)


@router.message(F.text == 'Админ-панель')
async def admin(message: Message):
    if message.from_user.id == ADMIN:
        await message.answer('Добро пожаловать в админ-панель!', reply_markup=kb.admin_main)
    else:
        await message.answer('Вход в админ-панель для вас недоступен', reply_markup=kb.back)
        
        
@router.message(F.text == 'Добавить')
async def add(message: Message, state: FSMContext):
    await state.set_state(States.add_category_or_item)
    await message.answer('Выберите что вы хотите добавить', reply_markup=kb.category_or_item)
    
    
@router.message(States.add_category_or_item)
async def add_category_or_item(message: Message, state: FSMContext):
    if message.text == 'Категория':
        await state.set_state(States.add_category)
        await message.answer('Напишите название категории')
    elif message.text == 'Товар':
        await state.set_state(States.add_category_item)
        await message.answer('Выберите в какой категории будет ваш товар')
        
        categories = await rq.get_categories()
        
        response = ''
        
        for i, category in enumerate(categories, 1):
            response += f'{i} - {category.name}\n'
            
        await message.answer(response)
    else:
        message.answer('Выберите, категория или товар:')
        
    
@router.message(States.add_category)
async def add_category(message: Message, state: FSMContext):
    category_name = message.text
    success = await rq.add_category(category_name)
    await state.clear()
    
    if success:
        await message.answer('Создана новая категория!', reply_markup=kb.admin_main)
    else:
        await message.answer('Такая категория уже существует...\nПопробуйте другое название!', 
                             reply_markup=kb.admin_main)
    
    
@router.message(States.add_category_item)
async def add_category_item(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(States.add_name_item)
    await message.answer('Введите название для товара')
    
    
@router.message(States.add_name_item)
async def add_name_item(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(States.add_description_item)
    await message.answer('Введите описание')
    
    
@router.message(States.add_description_item)
async def add_description_item(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(States.add_price_item)
    await message.answer('Введите цену в долларах\n(Только цифры)')
    
    
@router.message(States.add_price_item)
async def add_price_item(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    data = await state.get_data()
    await rq.add_item(data['name'], data['description'], data['price'],  data['category'])
    await message.answer('Вот карточка вашего товара!')
    await message.answer(f'Название: {data['name']}\nОписание: {data['description']}\n'
                         f'Цена: {data['price']}$', reply_markup=kb.admin_main)
    await state.clear()
    
    
@router.message(F.text == 'Удалить')
async def delete(message: Message, state: FSMContext):
    await state.set_state(States.del_category_or_item)
    await message.answer('Выберите что вы хотите удалить', reply_markup=kb.category_or_item)
    
    
@router.message(States.del_category_or_item)
async def delete_category(message: Message, state: FSMContext):
    if message.text == 'Категория':
        await state.set_state(States.del_category)
        await message.answer('Выберите категорию которую вы хотите удалить', 
                             reply_markup=await kb.category())
    elif message.text == 'Товар':
        await state.set_state(States.del_cat_item)
        await message.answer('Выберите из какой категории нужно удалить товар')
        
        categories = await rq.get_categories()
        
        response = ''
        
        for i, category in enumerate(categories, 1):
            response += f'{i} - {category.name}\n'
            
        await message.answer(response)
    else:
        await message.answer('Выберите, категория или товар:')
    
    
@router.message(States.del_category)
async def del_category(message: Message, state: FSMContext):
    category_name = message.text
    success = await rq.delete_category(category_name)
    await state.clear()
    
    if success:
        await message.answer('Категория удалена!', reply_markup=kb.admin_main)
    else:
        await message.answer('Категория не была удалена.', reply_markup=kb.admin_main)
        
        
@router.message(States.del_cat_item)
async def del_cat_item(message: Message, state: FSMContext):
    category_id = message.text
    await state.update_data(category=message.text)
    await state.set_state(States.del_item)
    await message.answer('Выберите какой нужно удалить товар', 
                         reply_markup=await kb.del_item(category_id))
    
    
@router.message(States.del_item)
async def del_item(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    success = await rq.del_item(data['name'], data['category'])
    await state.clear()
    
    if success:
        await message.answer('Товар удален!', reply_markup=kb.admin_main)
    else:
        await message.answer('Товар не был удален.', reply_markup=kb.admin_main)
    

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
        
    await message.answer(response, reply_markup=kb.cart_actions)


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
    category_id = callback.data.split('_')[1]
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


@router.message(F.text == 'Выйти')
async def to_main(message: Message):
    await message.answer('Вы вышли из админ-панели!')
    await message.answer('Главное меню', reply_markup=kb.main)


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Главное меню', reply_markup=kb.main)
    await state.clear()