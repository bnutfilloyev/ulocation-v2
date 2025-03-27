from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from structures.states import RegState
from utils.user_check import \
    check_user_stepwise  # Yangi funksiyani import qilish


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        
        state: FSMContext = data["state"]
        state_name = await state.get_state()

        bypass_states = [
            RegState.fullname, 
            RegState.phone_number, 
            RegState.subscription
        ]
        if state_name in bypass_states:
            return await handler(event, data)

        if not await check_user_stepwise(event, state):
            return

        return await handler(event, data)