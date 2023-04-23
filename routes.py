from email.mime.text import MIMEText

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import db

from loader import dp, bot, _

b1 = KeyboardButton("O'zbekcha")
b2 = KeyboardButton('Русский')
b3 = KeyboardButton("Ўзбекча")

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).add(b3)


class Regist(StatesGroup):
    name = State()
    phone = State()
    viloyat = State()
    tuman = State()
    years = State()
    ad = State()
    user_id = State()
    lang = State()
    change_name = State()
    change_phone = State()
    change_viloyat = State()
    change_tuman = State()


@dp.message_handler(commands=['start', 'help'])
async def commands_start(message: types.Message):
    user_id = message.from_user.id

    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    text = await db.session.execute(select(db.Text.greeting).filter_by(lang=user.lang if user else 'uz_kir'))
    text = text.scalar()

    if user:
        print('User')
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))

        return user
    else:
        print(user_id)
        print('No user')
        text = await db.session.execute(select(db.Text.greeting).filter_by(lang='uz_kir'))
        text_ru = await db.session.execute(select(db.Text.greeting).filter_by(lang='ru'))
        text_kir = await db.session.execute(select(db.Text.greeting).filter_by(lang='uz_kir'))

        text = text.scalar()
        text_ru = text_ru.scalar()
        text_kir = text_kir.scalar()

        multitext = text + '\n' + text_ru + '\n' + text_kir

        lang_ru = 'Уважаемый заявитель, выберите язык интерфейса!'
        lang_uz = "Xurmatli murojaatchi, iltimos intefeys tilini tanlang!"
        lang_kir = 'Хурматли мурожаатчи, илттимос интерфейс тилини танланг!'

        multilang = lang_uz + '\n' + lang_ru + '\n' + lang_kir
        await bot.send_message(user_id, multitext, reply_markup=kb_client)
        await bot.send_message(user_id, multilang)


async def take_text(lang, step, user_id, message=None, ls=None):
    text = await db.session.execute(select(db.Text).filter_by(lang=lang))
    text = text.scalar()
    #
    if step == 0:
        await bot.send_message(user_id, text.greeting)

    if step == 1:
        return text.step1
    if step == 2:
        return text.step2
    if step == 3:
        return text.step3
    if step == 4:
        return text.step4
    if step == 5:
        return text.step5
    if step == 6:
        return text.step6
    if step == 7:
        return text.step7


@dp.message_handler(Text(equals="Murojaatingizni qoldiring"))
@dp.message_handler(Text(equals="O'zbekcha"))
async def murojat_handlers_uz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    global status_lang

    status_lang = 'uz'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman
            text = await take_text(user.lang, 6, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('uz', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Bekor qilish')))
        await Regist.name.set()


@dp.message_handler(Text(equals="Оставьте обращение"))
@dp.message_handler(Text(equals="Русский"))
async def murojat_handlers_ru(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    global status_lang

    status_lang = 'ru'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman
            text = await take_text(user.lang, 6, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('ru', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Отмена')))
        await Regist.name.set()


@dp.message_handler(Text(equals="Мурожаатингизни қолдиринг"))
@dp.message_handler(Text(equals="Ўзбекча"))
async def murojat_handlers_uz_kir(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    global status_lang

    status_lang = 'uz_kir'

    step = 1

    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()
    if user:
        await Regist.ad.set()
        async with state.proxy() as data:
            data['name'] = user.fio
            data['phone'] = user.phone
            data['phone'] = user.year
            data['lang'] = user.lang
            data['viloyat'] = user.viloyati.name_uz
            data['tuman'] = user.tuman
            text = await take_text(user.lang, 6, message.from_user.id, message)
            await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Bekor qilish'))))

    else:
        text = await take_text('uz_kir', step, message.from_user.id, message)
        await bot.send_message(user_id, text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Бекор қилиш')))
        await Regist.name.set()


@dp.message_handler(state=Regist.name)
async def load_name(message: types.Message, state: FSMContext):
    step = 2

    async with state.proxy() as data:
        data['name'] = message.text
        object = tuple(data.values())

    if object[0] == 'Bekor qilish':
        await state.finish()
        await bot.send_message(message.from_user.id, 'Bekor qilish', reply_markup=kb_client)
        return
    elif object[0] == 'Отмена':
        await state.finish()
        await bot.send_message(message.from_user.id, 'Отмена', reply_markup=kb_client)
        return
    elif object[0] == 'Бекор қилиш':
        await state.finish()
        await bot.send_message(message.from_user.id, 'Бекор қилиш', reply_markup=kb_client)
        return

    text = await take_text(status_lang, step, message.from_user.id, message)

    if status_lang == 'ru':
        await bot.send_message(message.from_user.id, text,
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                                   KeyboardButton('Отправить номер телефона', request_contact=True)))
    elif status_lang == 'uz':
        await bot.send_message(message.from_user.id, text,
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                                   KeyboardButton("Telefon raqamni jo'natish", request_contact=True)))
    else:
        await bot.send_message(message.from_user.id, text,
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                                   KeyboardButton('Телефон рақамни жўнатиш', request_contact=True)))
    await Regist.next()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Regist.phone)
async def load_phone(message: types.Message, state: FSMContext, editMessageReplyMarkup=None):
    step = 3

    async with state.proxy() as data:
        data['phone'] = message.contact.phone_number
        await Regist.next()
        kb = await get_viloyats(status_lang)
        text = await take_text(status_lang, step, message.from_user.id, message)
        await bot.send_message(message.from_user.id, text, reply_markup=kb)


async def get_viloyats(lang: str) -> db.Viloyat:
    viloyats = await db.session.execute(select(db.Viloyat))

    viloyats = viloyats.scalars()

    if lang == 'ru':
        kb_generator = [x.name_ru for x in viloyats]
    elif lang == 'uz_kir':
        kb_generator = [x.name_uz_kir for x in viloyats]
    else:
        kb_generator = [x.name_uz for x in viloyats]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(*kb_generator)

    return kb


@dp.message_handler(state=Regist.viloyat)
async def load_viloyat(message: types.Message, state: FSMContext):
    step = 4

    async with state.proxy() as data:
        data['viloyat'] = message.text
        await Regist.next()

    text = await take_text(status_lang, step, message.from_user.id, message)
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(state=Regist.tuman)
async def load_tuman(message: types.Message, state: FSMContext):
    step = 5

    async with state.proxy() as data:
        data['tuman'] = message.text
        await Regist.next()

    text = await take_text(status_lang, step, message.from_user.id, message)
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(regexp=r"^(\d+)$", state=Regist.years)
async def load_years(message: types.Message, state: FSMContext):
    step = 6

    async with state.proxy() as data:
        data['years'] = int(message.text)
        await Regist.next()

    text = await take_text(status_lang, step, message.from_user.id, message)
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(state=Regist.ad)
async def load_ad(message: types.Message, state: FSMContext):
    step = 7

    async with state.proxy() as data:
        data['ad'] = message.text
        data['user_id'] = message.from_user.id
        data['lang'] = status_lang

    await createUser(state, message.from_user.id)
    await state.finish()

    object = tuple(data.values())

    if object[5] == _('Bekor qilish') or object[0] == _('Bekor qilish'):
        return

    await sql_read2(message, status_lang, step)
    if status_lang == 'uz':
        await bot.send_message(message.from_user.id, 'Asosiy menyu',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton('Mening murojaatlarim')
                               ).add(KeyboardButton('Murojaatingizni qoldiring')
                                     ).add(KeyboardButton("Tilni o'zgartirish")).add(
                                   KeyboardButton('Sozlamalar')))
    elif status_lang == 'ru':
        await bot.send_message(message.from_user.id, 'Главное меню',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton('Мои обращения')
                                   ).add(KeyboardButton('Оставьте обращение')
                                         ).add(KeyboardButton("Поменять язык")).add(
                                   KeyboardButton('Настройки')))
    else:
        await bot.send_message(message.from_user.id, 'Асосий меню',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton('Менинг мурожаатларим')
                                   ).add(KeyboardButton('Мурожаатингизни қолдиринг')
                                         ).add(KeyboardButton("Тилни ўзгартириш")).add(
                                   KeyboardButton('Созламалар')))


async def sql_read2(message, lang, step):
    app = await db.session.execute(select(db.Application.id).join(db.User, db.User.id == db.Application.user_id).filter(
        db.User.tg_user_id == message.from_user.id))
    app = app.scalars()
    ls = []

    for i in app:
        ls.append(i)
    text = await take_text(lang, step, message.from_user.id, message, str(ls[-1]))
    await bot.send_message(message.from_user.id, text)


async def createUser(state, user_id):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    async with state.proxy() as data:
        object = tuple(data.values())
        print(object)

        if object[5] == 'Бекор қилиш' or object[0] == 'Бекор қилиш':
            await bot.send_message(user_id, 'Бекор қилиш', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
                  ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
                KeyboardButton(_('Sozlamalar'))))
            return ''

        if object[5] == 'Отмена' or object[0] == 'Отмена':
            await bot.send_message(user_id, 'Отмена', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
                  ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
                KeyboardButton(_('Sozlamalar'))))
            return ''

        if object[5] == 'Bekor qilish' or object[0] == 'Bekor qilish':
            await bot.send_message(user_id, 'Bekor qilish', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton(_('Mening murojaatlarim'))
            ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
                  ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
                KeyboardButton(_('Sozlamalar'))))
            return ''

        else:

            if user:

                app = db.Application(application=object[5], user_id=user.id, lang=object[3])

                db.session.add(app)
                await db.session.commit()

                # message = f'''№{app.id}
                # Username: {user.fio}
                # User_phone: {user.phone}
                # {'Murojat kategoriyasi'}: {cat.name_uz}
                # {'sizning murojaatingiz'}: {app.application}
                # {'Murojat holati'}: {app.status}
                # {'murojatga javob'}: {app.answer if app.answer != None else ''}
                #             '''
                #
                # await send_mail2(message)

            else:

                if object[7] == 'uz':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz=object[2]))
                if object[7] == 'ru':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_ru=object[2]))
                if object[7] == 'uz_kir':
                    cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=object[2]))
                cat = cat.scalar()

                user = db.User(fio=object[0], phone=object[1], viloyat_id=cat.id, year=object[4], tuman=object[3],
                               tg_user_id=object[6], lang=object[7])
                db.session.add(user)
                await db.session.flush()

                app = db.Application(application=object[5], user_id=user.id, lang=object[7])

                db.session.add_all([user, app])
                await db.session.commit()


@dp.message_handler(Text(equals='Bekor qilish'))
@dp.message_handler(Text(equals='Отмена'))
@dp.message_handler(Text(equals='Бекор қилиш'))
async def cancel_purchase(message: types.Message):
    await bot.send_message(message.from_user.id, _('Bekor qilish'),
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                               KeyboardButton(_('Mening murojaatlarim'))
                           ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
                                 ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
                               KeyboardButton(_('Sozlamalar'))))
    return


import aiosmtplib


async def send_mail2(message: str) -> str:
    sender = "sarvarchikkamilov@gmail.com"
    # your password = "your password"
    password = 'aaywgssiujzhsirr'

    server = aiosmtplib.SMTP("smtp.gmail.com", 587)
    await server.connect()
    # await server.starttls()

    try:
        await server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "FROM TG BOT"
        await server.sendmail(sender, 'sarvar_kamilov2@mail.ru', msg.as_string())
        await server.quit()

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


@dp.message_handler(Text(equals='Mening murojaatlarim'))
@dp.message_handler(Text(equals='Мои обращения'))
@dp.message_handler(Text(equals='Менинг мурожаатларим'))
async def my_applications(message: types.Message):
    user_id = message.from_user.id

    apps = await db.session.execute(select(db.Application).join(db.User, db.User.id == db.Application.user_id).filter(
        db.User.tg_user_id == user_id).order_by(db.Application.id))

    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    apps = apps.scalars()

    for i in apps:
        if user.lang == 'uz':

            message = f'''№{i.id}
{'sizning murojaatingiz'}: {i.application} 
{'Murojat holati'}: {i.status}
{'murojatga javob'}: {i.answer if i.answer != None else ''}
            '''
        elif user.lang == 'ru':

            message = f'''№{i.id}
{'Ваше обращение'}: {i.application} 
{'Cтатус обращения'}: {i.status}
{'Ответ на обращение'}: {i.answer if i.answer != None else ''}
            '''
        else:

            message = f'''№{i.id}
{'Сизнинг мурожатингиз'}: {i.application} 
{'Мурожат холати'}: {i.status}
{'Мурожатга жавоб'}: {i.answer if i.answer != None else ''}
                    '''
        await bot.send_message(user_id, message)


def lang_change_handler():
    langs = ["O'zbekchaga", 'На русский', "Ўзбекчага"]
    for i in langs:
        dp.register_message_handler(change_lang, Text(equals=i))


@dp.message_handler(Text(equals="Tilni o'zgartirish"))
@dp.message_handler(Text(equals="Поменять язык"))
@dp.message_handler(Text(equals="Тилни ўзгартириш"))
async def select_lang(message: types.Message):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    c1 = KeyboardButton("O'zbekchaga")
    c2 = KeyboardButton('На русский')
    c3 = KeyboardButton("Ўзбекчага")
    kb_client_change = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(c1).add(c2).add(c3)

    if user.lang == 'uz':
        await bot.send_message(message.from_user.id, 'Xurmatli murojaatchi, iltimos intefeys tilini tanlang!',
                               reply_markup=kb_client_change)
    if user.lang == 'ru':
        await bot.send_message(message.from_user.id, 'Уважаемый заявитель, выберите язык интерфейса!',
                               reply_markup=kb_client_change)
    if user.lang == 'uz_kir':
        await bot.send_message(message.from_user.id, 'Хурматли мурожаатчи, илттимос интерфейс тилини танланг!',
                               reply_markup=kb_client_change)


async def change_lang(message: types.Message):
    if message.text == "O'zbekchaga":
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'uz'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Mening murojaatlarim')
                                                                ).add(KeyboardButton('Murojaatingizni qoldiring')
                                                                      ).add(KeyboardButton("Tilni o'zgartirish")).add(
            KeyboardButton('Sozlamalar'))
        await bot.send_message(message.from_user.id, "Til o'zgartirildi", reply_markup=user_kb)

    if message.text == 'На русский':
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'ru'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Мои обращения')
                                                                ).add(KeyboardButton('Оставьте обращение')
                                                                      ).add(KeyboardButton("Поменять язык")).add(
            KeyboardButton('Настройки'))

        await bot.send_message(message.from_user.id, 'Язык изменен', reply_markup=user_kb)
    if message.text == "Ўзбекчага":
        user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
        user = user.scalar()
        user.lang = 'uz_kir'
        await db.session.commit()
        user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Менинг мурожаатларим')
                                                                ).add(KeyboardButton('Мурожаатингизни қолдиринг')
                                                                      ).add(KeyboardButton("Тилни ўзгартириш")).add(
            KeyboardButton('Созламалар'))
        await bot.send_message(message.from_user.id, 'Тил ўзгартирилди', reply_markup=user_kb)


@dp.message_handler(Text(equals='Sozlamalar'))
@dp.message_handler(Text(equals='Настройки'))
@dp.message_handler(Text(equals='Созламалар'))
async def settings(message: types.Message):
    uz_sets = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(_("Ma'lumotlarni ko'rish")))

    await bot.send_message(message.from_user.id, _('Sozlamalar'), reply_markup=uz_sets)


def handlers_settings_changes():
    ls = ["Ism sharifini o'zgartirish", "Telefonni o'zgartirish", "Изменить имя", "Изменить телефон",
          'Исм шарифини ўзгартириш', "Телефонни ўзгартириш"]
    for x in ls:
        dp.register_message_handler(change_settings, Text(equals=x))


async def change_settings(message: types.Message, state: FSMContext):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    if message.text == _('Ism sharifini o`zgartirish'):
        await changes(message.from_user.id, state, message, Regist, user.lang, 'change_name')
    if message.text == _('Telefonni o`zgartirish'):
        await changes(message.from_user.id, state, message, Regist, user.lang, 'change_phone')


async def changes(user_id, state, message, Regist, lang, step):
    if step == 'change_name':
        await Regist.change_name.set()

        text = await take_text(lang, 1, user_id, message)
        await bot.send_message(user_id, text)

        await bot.send_message(user_id, _('Bekor qilish'),
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Bekor qilish'))))
    if step == 'change_phone':
        await Regist.change_phone.set()
        await bot.send_message(user_id, _('Kontaktni yuboring'),
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Kontaktni yuboring'), request_contact=True)))


@dp.message_handler(state=Regist.change_name)
async def changeName(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    await state.finish()

    if new_name == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))
        return

    else:
        user.fio = new_name
        await db.session.commit()

        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Regist.change_phone)
async def changePhone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.contact.phone_number
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()
    await state.finish()
    if new_name == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))
        return

    else:
        user.phone = new_name
        await db.session.commit()

        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))


@dp.message_handler(Text(equals="Ma'lumotlarni ko'rish"))
@dp.message_handler(Text(equals="Посмотреть данные"))
@dp.message_handler(Text(equals="Малумотларини кўриш"))
async def sendMyName(message: types.Message):
    user_id = message.from_user.id
    user = await db.session.execute(
        select(db.User).filter_by(tg_user_id=user_id).options(selectinload(db.User.viloyati)))
    user = user.scalar()

    sets_change = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton(_("Ism sharifini o'zgartirish"))).add(KeyboardButton(_("Telefonni o'zgartirish"))).add(
        _("Hududi o'zgartirish")).add(
        _('Bekor qilish'))

    if user.lang == 'uz':
        await bot.send_message(user_id,
                               f'Sizning FISh {user.fio}, sizning telefon raqamingiz: {user.phone}, {user.viloyati.name_uz}, {user.tuman}',
                               reply_markup=sets_change)
    elif user.lang == 'ru':
        await bot.send_message(user_id,
                               f'Ваше ФИО  {user.fio}, ваш номер телефона: {user.phone}, {user.viloyati.name_ru}, {user.tuman}',
                               reply_markup=sets_change)
    else:
        await bot.send_message(user_id,
                               f'Сизнинг ФИШ {user.fio}, сизнинг телефон рақамингиз: {user.phone}, {user.viloyati.name_uz_kir}, {user.tuman}',
                               reply_markup=sets_change)


@dp.message_handler(Text(equals="Hududi o'zgartirish"))
@dp.message_handler(Text(equals="Худуди ўзгартириш"))
@dp.message_handler(Text(equals="Поменять область"))
async def change_viloyat_button(message: types.Message):
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=message.from_user.id))
    user = user.scalar()
    kb = await get_viloyats(user.lang)
    await Regist.change_viloyat.set()
    await bot.send_message(message.from_user.id, "Tugmasini bosing", reply_markup=kb)


async def handlers_uz():
    cats = await db.session.execute(select(db.Viloyat))
    cats = cats.scalars()
    for x in cats:
        dp.register_message_handler(change_viloyat, Text(equals=x.name_uz), state=None)


@dp.message_handler(state=Regist.change_viloyat)
async def change_viloyat(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if new_name == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'),
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   KeyboardButton(_('Mening murojaatlarim'))
                               ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
                                     ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
                                   KeyboardButton(_('Sozlamalar'))))
        return

    else:
        async with state.proxy() as data:
            data['change_viloyat'] = message.text
            await Regist.next()

            text = await take_text(user.lang, 4, message.from_user.id, message)
            await bot.send_message(message.from_user.id, text)


@dp.message_handler(state=Regist.change_tuman)
async def change_tuman(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_tuman = message.text
    user = await db.session.execute(select(db.User).filter_by(tg_user_id=user_id))
    user = user.scalar()

    if new_tuman == _('Bekor qilish'):
        await bot.send_message(user_id, _('Bekor qilish'), reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))
        return

    else:
        async with state.proxy() as data:
            object = tuple(data.values())
            print(object)

        if user.lang == 'uz':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz=object[0]))
        if user.lang == 'ru':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_ru=object[0]))
        if user.lang == 'uz_kir':
            cat = await db.session.execute(select(db.Viloyat).filter_by(name_uz_kir=object[0]))
        cat = cat.scalar()

        user.viloyat_id = cat.id
        user.tuman = new_tuman
        await db.session.commit()
        await state.finish()
        await bot.send_message(message.from_user.id, 'ok', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton(_('Mening murojaatlarim'))
        ).add(KeyboardButton(_('Murojaatingizni qoldiring'))
              ).add(KeyboardButton(_("Tilni o'zgartirish"))).add(
            KeyboardButton(_('Sozlamalar'))))
