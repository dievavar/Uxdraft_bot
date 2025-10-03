from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.prototype_generator import PROMPT_TEMPLATES, generate_prototype
from bot.states import UXForm
import asyncio
from aiogram.types import FSInputFile
from config import SERVER_URL, OUTPUT_DIR
import os


router = Router()
# Типы проекта
PROJECTS_MAP = {
    "proj_website": "Сайт",
    "proj_shop": "Интернет-магазин",
    "proj_mobile": "Мобильное приложение",
    "proj_saas": "SaaS / Онлайн-сервис",
    "proj_crm": "CRM / ERP",
    "proj_edu": "Образовательная платформа"
}

# Аудитория
AUDIENCE_MAP = {
    "aud_teens": "Подростки (12–18)",
    "aud_youth": "Молодёжь (18–25)",
    "aud_families": "Молодые семьи (25–40)",
    "aud_business": "Бизнес",
    "aud_seniors": "Старшее поколение (50+)"
}

# Функции
FUNCTIONS_MAP = {
    "func_auth": "Авторизация",
    "func_catalog": "Каталог",
    "func_cart": "Корзина",
    "func_form": "Обратная связь",
    "func_search": "Поиск",
    "func_payment": "Онлайн-оплата"
}

# Стиль
STYLE_MAP = {
    "style_minimal": "Минимализм",
    "style_business": "Бизнес",
    "style_bright": "Яркий",
    "style_dark": "Тёмная тема",
    "style_modern": "Современный UI"
}


# ---------- Старт ----------
@router.message(F.text == "/start")
async def start_form(message: Message, state: FSMContext):
    photo = FSInputFile("assets/4.png")
    text = (
        "Привет!\n"
        "Я помогу тебе создать **UX-прототип** — быстрый и наглядный макет будущего сайта или приложения.\n\n"
        "Что это даёт:\n"
        "— Проверишь идею без долгой разработки\n"
        "— Поймёшь, как продуктом будут пользоваться реальные люди\n"
        "— Сможешь показать дизайн коллегам или инвесторам\n\n"
        "Просто опиши проект, выбери аудиторию, функции и стиль — и получишь кликабельный прототип!\n\n"
        "Доступные команды:\n"
        "/start — начать новый проект\n"
        "/help — подсказка по функциям\n"
        "/brief — показать текущий бриф\n"
        "/cancel — отменить и начать заново\n"
        "/about — подробнее о боте\n\n"
        "Выбери тип проекта или напиши свой вариант:"
    )

    await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")

    await message.answer(
        "Сейчас я задам несколько вопросов, которые помогут составить бриф.\n"
        "По нему мы сгенерируем кликабельный прототип."
    )

    photo2 = FSInputFile("assets/2.png")
    await message.answer_photo(
        photo2,
        caption="Вот пример, как можно отвечать 👆\n\n"
                "Можно выбрать кнопку или написать свой вариант вручную."
    )

    await state.set_state(UXForm.business_type)
    await ask_projects(message, state)

# ---------- Вопрос 1: Тип проекта ----------
async def ask_projects(target, state: FSMContext):
    # Динамически строим кнопки из prompts.yaml
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=key, callback_data=f"proj_{i}")]
        for i, key in enumerate(PROMPT_TEMPLATES.keys())
    ])

    await target.answer(
        "Выбери *тип проекта* или напиши свой вариант:",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await state.set_state(UXForm.business_type)


@router.callback_query(UXForm.business_type, F.data.startswith("proj_"))
async def process_business_type_cb(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("proj_", ""))
    project_type = list(PROMPT_TEMPLATES.keys())[index]  # берём название из YAML
    await state.update_data(business_type=project_type)
    await ask_audience(callback.message, state)


@router.message(UXForm.business_type)
async def process_business_type_msg(message: Message, state: FSMContext):
    # Если написал вручную — сохраняем как есть
    await state.update_data(business_type=message.text)
    await ask_audience(message, state)
# ---------- Вопрос 2: Аудитория ----------
async def ask_audience(target, state: FSMContext):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подростки (12–18)", callback_data="aud_teens")],
        [InlineKeyboardButton(text="Молодёжь (18–25)", callback_data="aud_youth")],
        [InlineKeyboardButton(text="Молодые семьи (25–40)", callback_data="aud_families")],
        [InlineKeyboardButton(text="Старшее поколение (50+)", callback_data="aud_seniors")],
        [InlineKeyboardButton(text="Бизнес", callback_data="aud_business")]
    ])
    await target.answer("Кто *основная аудитория*?\n\nМожешь выбрать или написать свой вариант:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(UXForm.audience)



@router.callback_query(UXForm.audience, F.data.startswith("aud_"))
async def process_audience_cb(callback: CallbackQuery, state: FSMContext):
    value = AUDIENCE_MAP.get(callback.data, callback.data)
    await state.update_data(audience=value)
    await ask_functions(callback.message, state)

@router.message(UXForm.audience)
async def process_audience_msg(message: Message, state: FSMContext):
    await state.update_data(audience=message.text)
    await ask_functions(message, state)

# ---------- Вопрос 3: Функции ----------
async def ask_functions(target, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Авторизация", callback_data="func_auth")],
        [InlineKeyboardButton(text="Каталог", callback_data="func_catalog")],
        [InlineKeyboardButton(text="Корзина", callback_data="func_cart")],
        [InlineKeyboardButton(text="Обратная связь", callback_data="func_form")],
        [InlineKeyboardButton(text="Поиск", callback_data="func_search")],
        [InlineKeyboardButton(text="Онлайн-оплата", callback_data="func_payment")]
    ])

    await target.answer(
        "Какие *функции* нужны?\n\n"
        "Можешь выбрать из списка или написать свой вариант текстом:",
        reply_markup=kb, parse_mode="Markdown"
    )
    await state.set_state(UXForm.functions)


# ---------- Обработка кнопки ----------
@router.callback_query(UXForm.functions, F.data.startswith("func_"))
async def process_functions_cb(callback: CallbackQuery, state: FSMContext):
    value = FUNCTIONS_MAP.get(callback.data, callback.data)
    await state.update_data(functions=value)
    await ask_style(callback.message, state)



# ---------- Обработка текстового ввода ----------
@router.message(UXForm.functions)
async def process_functions_msg(message: Message, state: FSMContext):
    await state.update_data(functions=message.text)
    await ask_style(message, state)


# ---------- Вопрос 4: Стиль ----------
async def ask_style(target, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Минимализм", callback_data="style_minimal")],
        [InlineKeyboardButton(text="Бизнес", callback_data="style_business")],
        [InlineKeyboardButton(text="Яркий", callback_data="style_bright")],
        [InlineKeyboardButton(text="Тёмная тема", callback_data="style_dark")],
        [InlineKeyboardButton(text="Современный UI", callback_data="style_modern")]
    ])
    await target.answer("Какой *стиль* предпочитаешь?\n\nМожешь выбрать или написать свой вариант:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(UXForm.style)

@router.callback_query(UXForm.style, F.data.startswith("style_"))
async def process_style_cb(callback: CallbackQuery, state: FSMContext):
    value = STYLE_MAP.get(callback.data, callback.data)
    await state.update_data(style=value)
    await show_summary(callback.message, state)


@router.message(UXForm.style)
async def process_style_msg(message: Message, state: FSMContext):
    await state.update_data(style=message.text)
    await show_summary(message, state)

# ---------- Финальный обзор ----------
async def show_summary(target, state: FSMContext):
    data = await state.get_data()

    def normalize(value) -> str:
        """Приводим данные к строке для вывода"""
        if not value:
            return "—"
        if isinstance(value, list):
            return ", ".join(map(str, value))
        return str(value)

    projects = normalize(data.get("business_type"))
    audience = normalize(data.get("audience"))
    functions = normalize(data.get("functions"))
    styles = normalize(data.get("style"))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить тип проекта", callback_data="edit_business")],
        [InlineKeyboardButton(text="Изменить аудиторию", callback_data="edit_audience")],
        [InlineKeyboardButton(text="Изменить функции", callback_data="edit_functions")],
        [InlineKeyboardButton(text="Изменить стиль", callback_data="edit_style")],
        [InlineKeyboardButton(text="Подтвердить!", callback_data="confirm")]
    ])

    await target.answer(
        "Отлично! Вот что я понял из твоих ответов:\n\n"
        f"*Тип проекта*: {projects}\n"
        f"*Аудитория*: {audience}\n"
        f"*Функции*: {functions}\n"
        f"*Стиль*: {styles}\n\n"
        "Хочешь что-то изменить или подтвердить?",
        reply_markup=kb, parse_mode="Markdown"
    )
    await state.set_state(UXForm.confirm)

async def get_brief(state: FSMContext) -> dict:
    data = await state.get_data()
    return {
        "project": data.get("business_type", "—"),
        "audience": data.get("audience", "—"),
        "functions": data.get("functions", []),
        "style": data.get("style", "—")
    }

from deep_translator import GoogleTranslator

def translate_text(text: str) -> str:
    """Переводит текст на английский, если это не пустая строка"""
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        return text  # если ошибка перевода — оставляем как есть


@router.message(F.text == "/help")
async def help_command(message: Message):
    photo = FSInputFile("assets/3.png")
    caption = (
         "Я помогу тебе создать UX-прототип.\n\n"
        "Доступные команды:\n"
        "/start — начать новый проект\n"
        "/brief — показать текущий бриф\n"
        "/cancel — отменить и начать заново\n"
        "/about — подробнее о боте"
    )
    await message.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")



# ---------- About ----------
@router.message(F.text == "/about")
async def about_command(message: Message):
    photo = FSInputFile("assets/5.png")
    text = (
        "*О боте*\n\n"
        "Этот бот создан для быстрой генерации UX-прототипов — "
        "упрощённых макетов интерфейсов сайтов и приложений.\n\n"
        "*Зачем это нужно?*\n"
        "— протестировать идеи до начала разработки\n"
        "— показать концепцию коллегам или инвесторам\n"
        "— понять, как будет выглядеть продукт и какие функции нужны\n\n"
        "Бот помогает собрать бриф (тип проекта, аудитория, функции, стиль), "
        "а затем создаёт интерактивный прототип, доступный по ссылке.\n\n"
        "    Используй команды `/start` или `/brief`, чтобы попробовать прямо сейчас!"
    )
    await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")

# ---------- Brief ----------
@router.message(F.text == "/brief")
async def brief_command(message: Message, state: FSMContext):
    photo = FSInputFile("assets/1.png")
    data = await state.get_data()

    def normalize(value):
        if not value:
            return "—"
        if isinstance(value, list):
            return ", ".join(map(str, value))
        return str(value)

    text = (
        "*Текущий бриф*\n\n"
        f"Тип проекта: {normalize(data.get('business_type'))}\n"
        f"Аудитория: {normalize(data.get('audience'))}\n"
        f"Функции: {normalize(data.get('functions'))}\n"
        f"Стиль: {normalize(data.get('style'))}\n"
    )

    await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")


@router.message(F.text == "/cancel")
async def cancel_command(message: Message, state: FSMContext):
    # очищаем состояние
    await state.clear()

    photo = FSInputFile("assets/1.png")
    # отправляем помощь
    text = (
        "Ввод данных отменён.\n\n"
        "Используй /help, чтобы узнать доступные команды."
    )
    await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")

# ---------- Обработка изменения ----------

@router.callback_query(UXForm.confirm)
async def edit_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "edit_business":
        await callback.message.answer("Окей, давай уточним тип проекта:")
        await ask_projects(callback.message, state)
        await state.set_state(UXForm.business_type)
        return

    if callback.data == "edit_audience":
        await callback.message.answer("Хорошо, давай уточним аудиторию:")
        await ask_audience(callback.message, state)
        await state.set_state(UXForm.audience)
        return

    if callback.data == "edit_functions":
        await callback.message.answer("Хорошо, давай уточним функции:")
        await ask_functions(callback.message, state)
        await state.set_state(UXForm.functions)
        return

    if callback.data == "edit_style":
        await callback.message.answer("Хорошо, давай уточним стиль:")
        await ask_style(callback.message, state)
        await state.set_state(UXForm.style)
        return

    elif callback.data == "confirm":
        data = await state.get_data()

        # Сообщаем пользователю, что началась генерация
        await callback.message.answer(
            "Генерация прототипа началась!\n\n"
            "Пожалуйста, подождите немного..."
        )

        brief = {
            "project": data.get("business_type"),
            "audience": data.get("audience"),
            "functions": data.get("functions", []),
            "style": data.get("style")
        }

        try:
            # Генерация в отдельном потоке
            from bot.prototype_generator import generate_prototype
            result = await asyncio.to_thread(generate_prototype, brief)

            # Проверяем, есть ли скриншот
            from aiogram.types import FSInputFile
            caption = (
                "Прототип создан! Можешь открыть его с компьютера.\n\n"
                f"[Открыть HTML онлайн]({result['html_link']})\n\n"
                "Также прикреплён сам HTML-файл для локального открытия."
            )

            if result.get("png_path") and os.path.exists(result["png_path"]):
                screenshot = FSInputFile(result["png_path"])
                await callback.message.answer_photo(
                    screenshot,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                # если скриншота нет
                await callback.message.answer(
                    "Прототип создан, но скриншот не удалось сгенерировать.\n\n" + caption,
                    parse_mode="Markdown"
                )

            # Отправляем сам HTML-файл
            html_file = FSInputFile(result["html_path"])
            await callback.message.answer_document(html_file)

        except Exception as e:
            await callback.message.answer(f"Ошибка генерации: {e}")

        finally:
            await state.clear()
