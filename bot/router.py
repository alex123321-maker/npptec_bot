from aiogram import Router
from handlers import start,employee,admin,faqs

def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(start.router)
    main_router.include_router(employee.router)
    main_router.include_router(admin.router)
    main_router.include_router(faqs.router)



    return main_router
