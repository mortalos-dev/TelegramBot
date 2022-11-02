from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from ..dbworker import get_movie_data, DBEntry
import aiogram.utils.markdown as fmt


available_categories = ["топ", "по жанрам", "адаптивное"]
reduced_categories = ["топ", "адаптивное"]
available_genres = ["боевики", "драма", "комедия", "триллер", "ужасы", "приключения"]


class ChooseMovieState(StatesGroup):
    waiting_for_categories = State()
    waiting_for_subcategory = State()
    exploring_state = State()


async def movies_start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_categories:
        keyboard.add(name)
    await message.answer("Выберите категорию", reply_markup=keyboard)
    await state.set_state(ChooseMovieState.waiting_for_categories.state)


async def category_movies_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_categories:
        await message.answer("Пожалуйста, выберите категорию, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_category=message.text.lower())

    if message.text.lower() in reduced_categories:
        await message.answer(f"Вы выбрали категорию фильмов: {message.text.lower()}.\n"
                             f"Теперь приступим к просмотру вариантов :-)",
                             reply_markup=types.ReplyKeyboardRemove())
        data = await get_movie_data(message.text.lower())
        keyboard, text = create_msg(data)
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

        await state.set_state(ChooseMovieState.exploring_state.state)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for genre in available_genres:
            keyboard.add(genre)
        await message.answer("Теперь выборем подкатегорию", reply_markup=keyboard)
        await state.set_state(ChooseMovieState.waiting_for_subcategory.state)


async def subcategory_movies_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_genres:
        await message.answer("Пожалуйста, выберите подкатегорию, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы выбрали категорию фильмов: {user_data['chosen_category']}  {message.text.lower()}.\n"
                         f"Теперь приступим к просмотру вариантов :-)",
                         reply_markup=types.ReplyKeyboardRemove())

    data = await get_movie_data(user_data['chosen_category'], message.text.lower())
    keyboard, text = create_msg(data)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    await state.update_data(chosen_subcategory=message.text.lower(), chosen_category=user_data['chosen_category'])
    await state.set_state(ChooseMovieState.exploring_state.state)


def create_msg(data: DBEntry):
    buttons = [[types.InlineKeyboardButton(text="LINK TO TRAILER", url=data.trailerLink)],
               [types.InlineKeyboardButton(text="❤", callback_data="like"),
                types.InlineKeyboardButton(text="👎", callback_data="dislike")
                ]
               ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    text = fmt.text(
        fmt.text(fmt.hide_link(data.picLink),
                 fmt.hbold(data.primaryTitle), " (", data.startYear, ") Рейтинг IMDB - ", data.imdbRating),
        fmt.text(fmt.hitalic(data.originalTitle)),
        fmt.text(fmt.hitalic(data.runtimeMinutes), ' минут'),
        fmt.text(' '),
        fmt.text(data.description),
        fmt.text(' '),
        fmt.text(fmt.hbold('Жанр: '), data.genres),
        fmt.text(fmt.hbold('В ролях: '), data.actors),
        fmt.text(fmt.hbold('Режиссер: '), data.directors),
        sep="\n"
    )
    return keyboard, text


async def call_answer(call: types.CallbackQuery, state: FSMContext):

    await call.answer()
    user_data = await state.get_data()
    subcategory_data = user_data['chosen_subcategory'] if 'chosen_subcategory' in user_data.keys() else None
    data = await get_movie_data(user_data['chosen_category'], subcategory_data)
    keyboard, text = create_msg(data)
    await call.bot.send_message(call.from_user.id, text, parse_mode="HTML", reply_markup=keyboard)


async def echo_message(message: types.Message):
    await message.answer(message.text)


def register_handlers_movies(dp: Dispatcher):
    dp.register_message_handler(movies_start, commands="movies", state="*")
    dp.register_message_handler(category_movies_chosen, state=ChooseMovieState.waiting_for_categories)
    dp.register_message_handler(subcategory_movies_chosen, state=ChooseMovieState.waiting_for_subcategory)
    dp.register_callback_query_handler(call_answer, text='like', state=ChooseMovieState.exploring_state)
    dp.register_callback_query_handler(call_answer, text='dislike', state=ChooseMovieState.exploring_state)
