
from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import decode_payload
from aiogram.utils.i18n import gettext as _

from keyboards.common_kb import main_menu_kb, remove_kb
from utils.user_check import check_user_stepwise
