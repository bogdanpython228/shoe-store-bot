from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from app.database.models import async_session
from app.database.models import User, Category, Item, Favorite


async def add_user(tg_id: int):
    '''Добавляет пользователя в БД.
    
    Args:
        tg_id: телеграм ID пользователя
        
    Returns:
        True если успешно добавлен, False если такой полльзователь есть в БД
    '''
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if user:
            return False

        session.add(User(tg_id=tg_id))
        await session.commit()
        return True
            
            
async def add_category(name: str):
    '''Добавляет новую категорию.
    
    Args:
        name: название категории
        
    Returns:
        True если успешно добавлена, False если такая категория уже существует
    '''
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.name == name))
        
        if category:
            return False
        
        session.add(Category(name=name))
        await session.commit()
        return True
    
    
async def delete_category(name: str):
    '''Удаляет старую категорию.
    
    Args:
        name: название категории
        
    Returns:
        True если успешно удалена, False если такой категории нет
    '''
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.name == name))
        
        if not category:
            return False

        await session.execute(delete(Item).where(Item.category == category.id))

        await session.delete(category)
        await session.commit()
        return True
        
        
async def add_item(name: str, description: str, price: int, category: int):
    '''Добавляет новый товар.
    
    Args:
        name: название товара
        description: описание товара
        price: цена товара
        category: категория в которой находится товар
        
    Returns:
        True если успешно добавлен, False если товар уже существует
    '''
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.name == name,
                                                       Item.description == description,
                                                       Item.price == price,
                                                       Item.category == category))
        
        if item:
            return False
        
        session.add(Item(name=name, description=description,
                         price=price, category=category))
        await session.commit()
        return True
    
    
async def del_item(name: str, category: int):
    '''Удаляет старый товар.
    
    Args:
        name: название товара
        category: категория в котором он находится
        
    Returns:
        True если успешно удалено, False если такого товара нет
    '''
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.name == name,
                                                       Item.category == category))
        if not item:
            return False
        
        await session.delete(item)
        await session.commit()
        return True
            
            
async def add_to_favorites(user_id: int, item_id: int):
    '''Добваляет товар в корзину пользователя.
    
    Args:
        user_id: ID пользователя
        item_id: ID товара
        
    Returns:
        True если успешно добавлено, False если уже есть в корзине
    '''
    async with async_session() as session:
        favorite = await session.scalar(select(Favorite).where(Favorite.user_id == user_id,
                                                               Favorite.item_id == item_id))
        
        if favorite:
            return False
        
        session.add(Favorite(user_id=user_id, item_id=item_id))
        await session.commit()
        return True
        
        
async def get_favorites(user_id: int):
    '''Показывает что в корзине у пользователя.'''
    async with async_session() as session:
        return await session.scalars(select(Favorite)
                                     .where(Favorite.user_id == user_id)
                                     .options(joinedload(Favorite.item)))
        

async def delete_favorites(user_id: int):
    '''Удаляет все товары из корзины пользователя.'''
    async with async_session() as session:
        await session.execute(delete(Favorite).where(Favorite.user_id == user_id))
        await session.commit()


async def get_categories():
    '''Показывает все категории.'''
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id: int):
    '''Показывает все товары из выбранной категории.'''
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id: int):
    '''Показывает товар.'''
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))