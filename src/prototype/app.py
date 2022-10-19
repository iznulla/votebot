import logging

from models import *
from sqlalchemy.orm import sessionmaker

from flask import Flask

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md
import random
import smtplib

# Base.metadata.create_all(engine)

logging.basicConfig(level=logging.INFO)

TOKEN_API = '639642745:AAHd9aIHomuZZH7-pxJPRpWAAdMjF4vHRWc'

bot = Bot(token=TOKEN_API)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

gmail_user = 'iiepe6op@gmail.com'
gmail_password = 'aarkahldsqizguga'
voteData = {}

Session = sessionmaker(bind=engine)
session = Session()

def poll_for_send():
    poll_options = []
    values = voteData.get('option')
    if values is not None:
        for value in values:
            poll_options.append(value)

        poll_opt_dict = dict(poll_options)
        re_poll_opt = []

        for option_p in poll_opt_dict.keys():
            re_poll_opt.append(option_p[1])
        return re_poll_opt

# @dp.message_handler(commands=["city"])
def sendFilter(filter, id):
    city_users = []
    if filter == 'c':
        filter_id = User.city_id
        print(filter_id)
    elif filter == 't':
        filter_id = User.tribe_id
    elif filter == 'w':
        filter_id = User.wave_id
    if id == 'all':
        if filter == 'c':
            city_filter = session.query(City)
        elif filter == 't':
            city_filter = session.query(Tribe)
        elif filter == 'w':
            city_filter = session.query(Wave)
    elif id == '1':
        city_filter = session.query(User)
    else:
        city_filter = session.query(User).filter(filter_id == id)

    for u_id in city_filter:
        print(u_id)
        city_users.append(str(u_id.user_id))
    return city_users

def rndCode():
    return random.randint(1000, 9999)

def sendEmail(gmail_user, username, postfixMail, rndFour):
    sent_from = gmail_user
    to = username + postfixMail
    subject = 'CODE VOTEBOT'
    body = str(rndFour)
    print(gmail_user, rndFour, to)
    email_text = body
    print(email_text)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except:
        print('Something went wrong...')
    return body

buttonStudent = KeyboardButton('/student')
buttonAdmin = KeyboardButton('/adm')

buttonUsername = KeyboardButton('/username')
buttonInfo = KeyboardButton('/info')
buttonPoll = KeyboardButton('/poll')
buttonCancel = KeyboardButton('/cancel')
buttonCreatePoll = KeyboardButton('/create_poll',request_poll=types.KeyboardButtonPollType(type=types.PollType.mode))
keyboardStud = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonInfo, buttonCancel)
keyboardCreatePoll = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonInfo, buttonCreatePoll)

buttonYes = KeyboardButton('Yes')
buttonNo = KeyboardButton('No')
keyboardYesNo = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonYes, buttonNo)

buttonContact = KeyboardButton('Who are you?', request_contact=True)
buttonLocation = KeyboardButton('Where are you?', request_location=True)
keyboardInfo = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonContact, buttonLocation).add(buttonCancel)

buttonCampus1 = KeyboardButton('Kazan')
buttonCampus2 = KeyboardButton('Moscow')
buttonCampus3 = KeyboardButton('Novosibirsk')
keyboardCampus = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonCampus1, buttonCampus2, buttonCampus3).add(buttonCancel)

buttonWave1 = KeyboardButton('w12')
buttonWave2 = KeyboardButton('w13')
buttonWave3 = KeyboardButton('w14')
keyboardWave = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonWave1, buttonWave2, buttonWave3).add(buttonCancel)

buttonTribe1 = KeyboardButton('ignis')
buttonTribe2 = KeyboardButton('aqua')
buttonTribe3 = KeyboardButton('air')
buttonTribe4 = KeyboardButton('terra')
keyboardTribe = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonTribe1, buttonTribe2, buttonTribe3, buttonTribe4).add(buttonCancel)

keyboardRole = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(buttonStudent, buttonAdmin)

buttonSendAll = KeyboardButton('Send all users')
buttonGroupFilter = KeyboardButton('Group filter')
keyboardPoll = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(buttonSendAll).add(buttonGroupFilter).add(buttonCancel)

buttonSendTribe = KeyboardButton('Send TRIBE survey')
buttonSendWave = KeyboardButton('Send WAVE survey')
buttonSendCampus = KeyboardButton('Send CAMPUS survey')
keyboardSend = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(buttonSendTribe, buttonSendWave, buttonSendCampus).add(buttonCancel)

app = Flask(__name__)
db.create_all()

# class StatePoll(StatesGroup):
    # filter = State()
    # detal = State()

class Form(StatesGroup):
    role = State()
    username = State()
    code = State()
    wave = State()
    tribe = State()
    campus = State()
    poll = State()
    sendAll = State()
    filter = State()
    filterTribe = State()
    filterWave = State()
    filterCampus = State()

@dp.poll_answer_handler()
async def just_poll_answer(active_quiz: types.PollAnswer):
    answers = [o[1] for o in active_quiz.get_current('id')]
    vott = answers[2]
    vott = int(vott[0])
    answer = User_answer(user_id=voteData.get('user_id'), question_id=voteData.get('id'), answer_id=str(vott))
    db.session.add(answer)
    db.session.commit()

@dp.message_handler(commands=['help', 'start'])
async def start(message: types.Message):
    await Form.role.set()
    await message.answer("Choose role:", reply_markup=keyboardRole)

@dp.message_handler(commands=['cancel'], state='*')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await Form.role.set()
    await message.reply('Cancelled.', reply_markup=keyboardRole)

@dp.message_handler(lambda message: message.text not in ["/adm", "/student"], state=Form.role)
async def checkRole(message: types.Message):
    return await message.reply("Bad role. Choose your role from the keyboard.")
@dp.message_handler(state=Form.role)
async def saveRole(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['role'] = message.text
        print(data['role'])
    await Form.next()
    curUser = message.from_user.id
    nameUser = message.from_user.username
    user = User.query.filter_by(user_id=curUser).first()
    if user is None:
        await Form.username.set()
        await message.reply("Send me SBER platform username:")
    else:
        admin_status = user.admin_status
        if data['role'] == "/adm":
            if admin_status is True:
                await message.answer(f'Welcome back, ' + str(nameUser), reply_markup=keyboardCreatePoll)
                await Form.poll.set()
            else:
                await Form.role.set()
                await message.answer(f'Sorry, you dont have adm permission ', reply_markup=keyboardRole)
                return
        elif data['role'] == "/student":
            await message.answer(f'Welcome back, ' + str(nameUser), reply_markup=keyboardStud)
            await Form.role.set()

        else:
            await message.answer(f'Sorry, you dont have permission ', reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return

@dp.message_handler(state=Form.username)
async def sendUsername(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    if data['role'] == '/adm':
        postfixMail = '@21-school.ru'
    elif data['role'] == '/student':
        postfixMail = '@student.21-school.ru'
    else:
        return
    rndFour = rndCode()
    await message.reply('Enter code from your email ' + data['username'] + postfixMail + ':')
    sendEmail(gmail_user, data['username'], postfixMail, rndFour)
    await Form.next()
    @dp.message_handler(lambda message: not message.text.isdigit(), state=Form.code)
    async def checkCode(message: types.Message):
        return await message.reply('Code is WRONG.\nTry again:')

    @dp.message_handler(state=Form.code)
    async def processCode(message: types.Message, state: FSMContext):
        if str(rndFour) == message.text:
            await state.update_data(rndFour=int(message.text))
            if data['role'] == "/adm":
                await Form.campus.set()
                await message.answer("All right!\nChoose your campus:", reply_markup=keyboardCampus)

            else:
                await Form.next()
                await message.answer("All right!\nChoose your wave:", reply_markup=keyboardWave)
        else:
            # await state.finish()
            await message.reply('Code is WRONG.\nTry again:')
            # return await message.answer(data['role'], reply_markup=ReplyKeyboardRemove())
            # code = rndCode()

@dp.message_handler(lambda message: message.text not in ["w12", "w13", "w14"], state=Form.wave)
async def checkWave(message: types.Message):
    return await message.reply("Bad wave. Choose your wave from the keyboard.")

@dp.message_handler(state=Form.wave)
async def processWave(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['wave'] = message.text
    await Form.next()
    await message.answer("All right!\nChoose your tribe:", reply_markup=keyboardTribe)

@dp.message_handler(lambda message: message.text not in ["ignis", "aqua", "air", "terra"], state=Form.tribe)
async def checkTribe(message: types.Message):
    return await message.reply("Bad tribe. Choose your tribe from the keyboard.")

@dp.message_handler(state=Form.tribe)
async def processTribe(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tribe'] = message.text
    await Form.next()
    await message.answer("All right!\nChoose your campus:", reply_markup=keyboardCampus)

@dp.message_handler(lambda message: message.text not in ["Kazan", "Moscow", "Novosibirsk"], state=Form.campus)
async def checkCampus(message: types.Message):
    return await message.reply("Bad campus. Choose your campus from the keyboard.")

@dp.message_handler(state=Form.campus)
async def processCampus(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['campus'] = message.text
        curUser = message.from_user
        markup = types.ReplyKeyboardRemove()
        if data['role'] == '/student':
            newUser = User(user_id=curUser.id, telegram_username=curUser.username, platform_username=data['username'],
                           city_id=data['campus'], admin_status=False, tribe_id=data['tribe'], wave_id=data['wave'])
            db.session.add(newUser)
            db.session.commit()
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text('Hello ', md.bold(data['username'])),
                    md.text('Role: ', md.bold(data['role'])),
                    md.text('Campus: ', md.bold(data['campus'])),
                    md.text('Wave: ', md.bold(data['wave'])),
                    md.text('Tribe: ', md.bold(data['tribe'])),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )
            await Form.role.set()
            await message.answer('You have Student permissions. Now you can create and reply poll',
                                 reply_markup=keyboardRole)
        else:
            newUser = User(user_id=curUser.id, telegram_username=curUser.username, platform_username=data['username'],
                           city_id=data['campus'], admin_status=True, tribe_id=0, wave_id=0)
            db.session.add(newUser)
            db.session.commit()

            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text('Hello ', md.bold(data['username'])),
                    md.text('Role: ', md.bold(data['role'])),
                    md.text('Campus: ', md.bold(data['campus'])),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )
            await Form.role.set()
            await message.answer('You have Admin permissions. Now you can create and reply poll',
                                 reply_markup=keyboardCreatePoll)
    # print(data['username'], data['role'], data['wave'], data['tribe'], data['campus'], User.user_id)
    await Form.role.set()

# poll = State()

@dp.message_handler(commands=["create_poll"])
async def cmd_start(message: types.Message):
    # await Form.poll.set()
    await message.answer("Create new poll", reply_markup=keyboardPoll)

@dp.message_handler(commands=["/poll"])
async def cmd_start(message: types.Message):
    # await Form.poll.set()
    await message.answer("Subscribed to the newsletter", reply_markup=keyboardPoll)

@dp.message_handler(content_types=["poll"], state='*')
async def msg_with_poll(message: types.Message):
    voteData['id'] = str(message.poll.id)
    voteData['user_id'] = str(message.from_user.id)
    voteData['question'] = message.poll.question
    voteData['option'] = message.poll.options
    print(voteData['id'])
    question = Question(message.poll.id, message.poll.question, True, True)
    sd = poll_for_send()
    answers = [o[1] for o in sd]
    # vott = answers[1]
    # vott = int(vott[0])
    for o in range(len(sd)):
        answer = Answer(voteData.get('id'), str(sd[o]))
        db.session.add(answer)
    db.session.add(question)
    db.session.commit()
    await message.answer("Poll saved", reply_markup=keyboardPoll)
    return
@dp.message_handler(lambda message: message.text not in ['Send all users', 'Group filter', 'Send TRIBE survey', 'Send WAVE survey', 'ignis', 'air', 'terra', 'aqua', 'Send CAMPUS survey', 'Novosibirsk', 'Kazan', 'Moscow', 'w12', 'w13', 'w14', '/info'], state=Form.poll)
async def checkPoll(message: types.Message):
    return await message.reply("Bad option. Choose option from keyboard.")

@dp.message_handler(lambda message: message.text == 'Send all users', state=Form.poll)
async def stateAllUsers(message: types.Message):
    await Form.sendAll.set()
    await message.answer("Send poll to all users?", reply_markup=keyboardYesNo)

@dp.message_handler(state=Form.sendAll)
async def sendAllStudents(message: types.Message):
    if message.text == 'Yes':
        # await Form.poll.set()
        re_poll_opt = poll_for_send()
        print(User.city_id)
        id = '1'
        city_user = sendFilter('0', id)
        print(city_user)
        for i in range(len(city_user)):
            try:
                await bot.send_poll(chat_id=city_user[i], question=voteData.get('question'), is_anonymous=False, options=re_poll_opt)
            except:
                continue
        await message.answer("Poll sent all users", reply_markup=keyboardPoll)
        await Form.poll.set()
    elif message.text == 'No':
        await Form.poll.set()
        await message.answer(reply_markup=keyboardPoll)
    else:
        await message.answer("Bad option. Choose option from keyboard.")

@dp.message_handler(lambda message: message.text == 'Group filter', state=Form.poll)
async def groupFilter(message: types.Message):
    await Form.filter.set()
    await message.answer("Choose filter", reply_markup=keyboardSend)

@dp.message_handler(lambda message: message.text == 'Send TRIBE survey', state=Form.filter)
async def chooseTribe(message: types.Message):
    await Form.filterTribe.set()
    await message.answer("Choose tribe", reply_markup=keyboardTribe)

@dp.message_handler(lambda message: message.text == 'Send CAMPUS survey', state=Form.filter)
async def chooseCampus(message: types.Message):
    await Form.filterCampus.set()
    await message.answer("Choose campus", reply_markup=keyboardCampus)

@dp.message_handler(lambda message: message.text == 'Send WAVE survey', state=Form.filter)
async def chooseWave(message: types.Message):
    await Form.filterWave.set()
    await message.answer("Choose wave", reply_markup=keyboardWave)

@dp.message_handler(state=Form.filterTribe)
async def sendTribe(message: types.Message):
    re_poll_opt = poll_for_send()
    tribePoll = message.text
    print(tribePoll)
    filter = 't'
    city_user1 = sendFilter(filter, tribePoll)
    for i in range(len(city_user1)):
        try:
            await bot.send_poll(chat_id=city_user1[i], question=voteData.get('question'), is_anonymous=False, options=re_poll_opt)
        except:
            continue
    await Form.poll.set()
    await message.answer("Poll sent to " + tribePoll, reply_markup=keyboardPoll)
@dp.message_handler(state=Form.filterCampus)
async def sendCampus(message: types.Message):
    re_poll_opt = poll_for_send()
    campusPoll = message.text
    print(campusPoll)
    filter = 'c'
    city_user = sendFilter(filter, campusPoll)
    for i in range(len(city_user)):
        try:
            await bot.send_poll(chat_id=city_user[i], question=voteData.get('question'), is_anonymous=False, options=re_poll_opt)
        except:
            continue
    await Form.poll.set()
    await message.answer("Poll sent to " + campusPoll, reply_markup=keyboardPoll)

@dp.message_handler(state=Form.filterWave)
async def sendCampus(message: types.Message):
    re_poll_opt = poll_for_send()
    wavePoll = message.text
    print(wavePoll)
    filter = 'w'
    city_user = sendFilter(filter, wavePoll)
    for i in range(len(city_user)):
        try:
            await bot.send_poll(chat_id=city_user[i], question=voteData.get('question'), is_anonymous=False, options=re_poll_opt)
        except:
            continue
    await Form.poll.set()
    await message.answer("Poll sent to " + wavePoll, reply_markup=keyboardPoll)

# @dp.message_handler(commands=['cancel'])
# async def cancelPoll(message: types.Message):
#     await message.answer('Cancel', reply_markup=keyboardRole)
@dp.message_handler(commands=['info'], state=Form.poll)
async def info(message: types.Message):
    # await Form.role.set()
    await message.reply('Contact and location', reply_markup=keyboardInfo)

if __name__ == '__main__':
    executor.start_polling(dp)
