from aiogram import Router

from filters.role_filter import RoleFilter

player_router = Router()
player_router.message.filter(RoleFilter("player"))
player_router.callback_query.filter(RoleFilter("player"))
