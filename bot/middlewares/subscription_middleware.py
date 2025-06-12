from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from structures.states import RegState, PaymentState
from utils.user_check import check_user_stepwise 


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
            RegState.subscription,
            PaymentState.waiting_for_card_number,
            PaymentState.waiting_for_card_expiration,
            PaymentState.waiting_for_sms_code,
        ]
        if state_name in bypass_states:
            return await handler(event, data)

        if not await check_user_stepwise(event, state):
            return

        return await handler(event, data)