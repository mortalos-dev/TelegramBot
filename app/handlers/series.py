from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from ..dbworker import get_series_data, DBEntry
import aiogram.utils.markdown as fmt


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
        await message.answer(f"Вы выбрали категорию сериалов: {message.text.lower()}.\n"
                             f"Теперь приступим к просмотру вариантов :-)",
                             reply_markup=types.ReplyKeyboardRemove())
        data = await get_series_data(message.text.lower())
        keyboard, text = create_msg(data)
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

        await state.set_state(ChooseSeriesState.exploring_state.state)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for genre in available_genres:
            keyboard.add(genre)
        await message.answer("Теперь выборем подкатегорию", reply_markup=keyboard)
        await state.set_state(ChooseSeriesState.waiting_for_subcategory.state)


async def subcategory_series_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_genres:
        await message.answer("Пожалуйста, выберите подкатегорию, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы выбрали категорию сериалов: {user_data['chosen_category']}  {message.text.lower()}.\n"
                         f"Теперь приступим к просмотру вариантов :-)",
                         reply_markup=types.ReplyKeyboardRemove())

    data = await get_series_data(user_data['chosen_category'], message.text.lower())
    keyboard, text = create_msg(data)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    await state.update_data(chosen_subcategory=message.text.lower(), chosen_category=user_data['chosen_category'])
    await state.set_state(ChooseSeriesState.exploring_state.state)


def create_msg(data: DBEntry):
    buttons = [[types.InlineKeyboardButton(text="LINK TO TRAILER", url="https://www.imdb.com/title/tt2431438/")],
               [types.InlineKeyboardButton(text="❤", callback_data="like"),
                types.InlineKeyboardButton(text="👎", callback_data="dislike")
                ]
               ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    text = fmt.text(
        fmt.text(fmt.hunderline(data.primaryTitle), " (", data.startYear, " - ", data.endYear, ")"),
        fmt.text(fmt.code(data.description)),
        fmt.text(f"{'Для взрослых' if data.isAdult == True else 'Для всей семьи'}"),
        sep="\n"
    )
    return keyboard, text


async def call_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    user_data = await state.get_data()
    subcategory_data = user_data['chosen_subcategory'] if 'chosen_subcategory' in user_data.keys() else None
    data = await get_series_data(user_data['chosen_category'], subcategory_data)
    keyboard, text = create_msg(data)
    await call.bot.send_message(call.from_user.id, text, parse_mode="HTML", reply_markup=keyboard)


async def echo_message(message: types.Message):
    await message.answer(message.text)


def register_handlers_series(dp: Dispatcher):
    dp.register_message_handler(series_start, commands="series", state="*")
    dp.register_message_handler(category_series_chosen, state=ChooseSeriesState.waiting_for_categories)
    dp.register_message_handler(subcategory_series_chosen, state=ChooseSeriesState.waiting_for_subcategory)
    dp.register_callback_query_handler(call_answer, text='like', state=ChooseSeriesState.exploring_state)
    dp.register_callback_query_handler(call_answer, text='dislike', state=ChooseSeriesState.exploring_state)
