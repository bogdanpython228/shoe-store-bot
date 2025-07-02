from app.database.models import async_session
from app.database.models import User, Category, Item, Favorite
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload


async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            
            
async def add_to_favorites(user_id, item_id):
    async with async_session() as session:
        favorite = await session.scalar(select(Favorite).where(Favorite.user_id == user_id,
                                                               Favorite.item_id == item_id))
        
        if favorite:
            return False
        
        session.add(Favorite(user_id=user_id, item_id=item_id))
        await session.commit()
        return True
        
        
async def get_favorites(user_id):
    async with async_session() as session:
        return await session.scalars(select(Favorite).where(Favorite.user_id == user_id).options(joinedload(Favorite.item)))
        

async def delete_favorites(user_id):
    async with async_session() as session:
        stmt = delete(Favorite).where(Favorite.user_id == user_id)
        await session.execute(stmt)
        await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))