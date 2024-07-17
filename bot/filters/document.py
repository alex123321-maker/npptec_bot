

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import BaseFilter

from handlers.faqs import AddFaqState,EditFaqState


class NotAddFaqState(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        specified_states = [
            AddFaqState.waiting_for_text.state,
            AddFaqState.waiting_for_short_description.state,
            AddFaqState.waiting_for_document.state,
            EditFaqState.waiting_for_short_description.state,
            EditFaqState.waiting_for_description.state,
            EditFaqState.waiting_for_file.state
        ]
        return current_state not in specified_states