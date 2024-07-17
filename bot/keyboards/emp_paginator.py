from enum import Enum
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PageNavigationCD(CallbackData, prefix="page_nav"):
    page: int
    obj_count: int 


def generate_pagination_kb(current_page, total_pages, obj_count=15):
    builder = InlineKeyboardBuilder()
    btns = 1

    if current_page != 1:
        btns+=1
        builder.button(
            text="1",
            callback_data=PageNavigationCD(page=1,obj_count=obj_count)
        )
    if current_page > 2: 
        btns+=1
        builder.button(
            text=f"{max(current_page-5,2)}",
            callback_data=PageNavigationCD(page=max(current_page-5,2),obj_count=obj_count)
        )
        
    builder.button(
        text=f"[{current_page}]",
        callback_data=PageNavigationCD(page=current_page,obj_count=obj_count)
    )
    if current_page < total_pages-2:
        btns+=1
        builder.button(
            text=f"{min(current_page + 5, total_pages-1)}",
            callback_data=PageNavigationCD(page=min(current_page + 5, total_pages-1),obj_count=obj_count)
        )
    if current_page != total_pages:
        btns+=1
        builder.button(
            text=f"{total_pages}",
            callback_data=PageNavigationCD(page=total_pages,obj_count=obj_count)
        )
    b = 0
    if current_page != 1:
        b+=1
        builder.button(
            text="Предыдущая страница",
            callback_data=PageNavigationCD(page=max(current_page - 1, 1),obj_count=obj_count)
        )
    if current_page != total_pages:
        b+=1
        builder.button(
            text="Следующая страница",
            callback_data=PageNavigationCD(page=min(current_page + 1, total_pages),obj_count=obj_count)
        )
    
    builder.adjust(btns,b)
    

    return builder.as_markup()


