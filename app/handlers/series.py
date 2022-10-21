from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

available_categories = ["топ", "по жанрам", "адаптивное"]
reduced_categories = ["топ", "адаптивное"]
available_genres = ["боевики", "драма", "комедия", "триллер", "ужасы", "приключения"]


class ChooseSeriesState(StatesGroup):
    waiting_for_categories = State()
    waiting_for_subcategory = State()
    exploring_state = State()


async def series_start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_categories:
        keyboard.add(name)
    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(ChooseSeriesState.waiting_for_categories.state)


async def category_series_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_categories:
        await message.answer("Пожалуйста, выберите категорию, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_category=message.text.lower())

    if message.text.lower() in reduced_categories:
        await state.set_state(ChooseSeriesState.exploring_state.state)
        await message.answer(f"Вы выбрали категорию сериалов: {message.text.lower()}.\n"
                             f"Теперь приступим к просмотру вариантов :-)",
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for genre in available_genres:
            keyboard.add(genre)
        await state.set_state(ChooseSeriesState.waiting_for_subcategory.state)
        await message.answer("Теперь приступим к выбору подкатегории", reply_markup=keyboard)


async def subcategory_series_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_genres:
        await message.answer("Пожалуйста, выберите подкатегорию, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await state.set_state(ChooseSeriesState.exploring_state.state)
    await message.answer(f"Вы выбрали категорию сериалов: {user_data['chosen_category']}  {message.text.lower()}.\n"
                         f"Теперь приступим к просмотру вариантов :-)",
                         reply_markup=types.ReplyKeyboardRemove())


async def exploring_series_state(message: types.Message, state: FSMContext):
    # здесь откручивается показ сериалов с инлайн кнопками: лайк, некст
    await echo_message(message)


async def echo_message(message: types.Message):
    await message.answer(message.from_user.id, message.text)


def register_handlers_series(dp: Dispatcher):
    dp.register_message_handler(series_start, commands="series", state="*")
    dp.register_message_handler(category_series_chosen, state=ChooseSeriesState.waiting_for_categories)
    dp.register_message_handler(subcategory_series_chosen, state=ChooseSeriesState.waiting_for_subcategory)
    dp.register_message_handler(exploring_series_state, state=ChooseSeriesState.exploring_state)




