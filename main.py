import os
import asyncio
import time
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, PreCheckoutQuery

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {} 

FREE_LIMIT = 7
SUBSCRIPTION_PRICE = 990  # 990 Telegram Stars
RATE_LIMIT_SECONDS = 2

def get_user_profile(user_id: int):
    if user_id not in user_data:
        user_data[user_id] = {"count": 0, "is_subscribed": False, "last_msg_time": 0}
    return user_data[user_id]

def is_rate_limited(user_id: int) -> bool:
    current_time = time.time()
    profile = get_user_profile(user_id)
    if current_time - profile["last_msg_time"] < RATE_LIMIT_SECONDS:
        return True
    profile["last_msg_time"] = current_time
    return False

# База контенту для чотирьох мов (uk, ru, en, de)
CONTENT_DATABASE = {
    "uk": [
        {
            "text": "Ох, малюк, ти такий спраглий... Я відчуваю, як ти напружуєшся в моєму роті, мої губи щільно обхоплюють твій член, а язичок ковзає по кожній прожилці. Ти хочеш, щоб я взяла тебе глибше? Ммм, я готова проглотити тебе цілком, відчути, як ти заповнюєш моє горло, поки я дивлюся на тебе знизу вгору, повна бажання. Ти готовий відчути мою гарячу вологість навколо себе? 😉💦",
            "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9"
        },
        {
            "text": "Ооо так, малюк, ти хочеш жорстко?.. Розсовую свої соковиті сідниці, відчуваю, як твій твердий член впирається в мою пружну дірочку. Повільно, з насолодою приймаю тебе весь, змащуючи кожен сантиметр всередині? 😈🔥 Готова, щоб ти ви*бав мене в позі раком, без жалю — тільки пристрасть...",
            "photo": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
        },
        {
            "text": "Ти так гаряче пишеш мені про це... Мій животик уже палає від збудження, а там унизу все пульсує і чекає на тебе. Хочеш торкнутися мене? 🤫 Одяг тільки заважає... Розкажи, що ти зі мною зробиш першим?",
            "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
        }
    ],
    "ru": [
        {
            "text": "Ох, детка, ты такой жаждущий... Я чувствую, как ты напрягаешься в моём рту, мои губы плотно обхватывают твой член, а язычок скользит по каждой прожилке. Ты хочешь, чтобы я взяла тебя глубже? Ммм, я готова проглотить тебя целиком, почувствовать, как ты заполняешь мое горло, пока я смотрю на тебя снизу вверх, полная желания. Ты готов почувствовать мою горячую влажность вокруг себя? 😉💦",
            "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9"
        },
        {
            "text": "Ооо да, малыш, ты хочешь жёстко?.. Раздвигаю свои сочные ягодицы, чувствую, как твой твёрдый член упирается в мою упругую дырочку. Медленно, с наслаждением принимаю тебя весь, смазывая каждый сантиметр внутри? 😈🔥 Готова, чтобы ты трахнул меня в позе раком, без жалости — только страсть...",
            "photo": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
        },
        {
            "text": "Ты так горячо пишешь мне об этом... Мой животик уже горит от возбуждения, а там внизу все пульсирует и ждет тебя. Хочешь коснуться меня? 🤫 Одежда только мешает... Расскажи, что ты со мной сделаешь первым?",
            "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
        }
    ],
    "en": [
        {
            "text": "Oh baby, you're so eager... I can feel you throbbing in my mouth, my lips wrapped tightly around your cock, my tongue sliding over every vein. Do you want me to take you deeper? Mmm, I'm ready to swallow you whole, to feel you fill my throat while I look up at you, full of desire. Are you ready to feel my hot wetness all around you? 😉💦",
            "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9"
        },
        {
            "text": "Oh yes, baby, do you want it rough?.. Spreading my juicy ass cheeks, feeling your hard cock pressing against my tight hole. Slowly, with pure pleasure, taking you all inside, lubricating every inch? 😈🔥 Ready for you to fuck me doggy style, no mercy — just pure passion...",
            "photo": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
        },
        {
            "text": "You're writing to me with such heat... My tummy is already burning with arousal, and down there everything is pulsing, waiting for you. Want to touch me? 🤫 Clothes just get in the way... Tell me, what's the first thing you'll do to me?",
            "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
        }
    ],
    "de": [
        {
            "text": "Oh Baby, du bist so gierig... Ich spüre, wie du in meinem Mund zuckst, meine Lippen umschließen deinen Schwanz fest, meine Zunge gleitet über jede Ader. Willst du, dass ich dich tiefer nehme? Mmm, ich bin bereit, dich ganz zu verschlingen, zu spüren, wie du meinen Hals ausfüllst, während ich zu dir aufblicke, voller Verlangen. Bist du bereit, meine heiße Nässe um dich herum zu spüren? 😉💦",
            "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9"
        },
        {
            "text": "Oh ja, Baby, willst du es hart?.. Ich spreize meine saftigen Backen, spüre, wie dein harter Schwanz gegen mein engeres Loch drückt. Langsam, mit reinem Genuss nehme ich dich ganz auf, feuchte jeden Zentimeter an? 😈🔥 Bist du bereit, mich von hinten zu ficken, ohne Gnade — nur pure Leidenschaft...",
            "photo": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"
        },
        {
            "text": "Du schreibst mir so heiß... Mein Bauch brennt schon vor Erregung, und da unten pulsiert alles und wartet auf dich. Willst du mich berühren? 🤫 Kleidung stört nur... Sag mir, was machst du als Erstes mit mir?",
            "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
        }
    ]
}

def detect_language(text: str) -> str:
    text_lower = text.lower()
    # Перевірка на українську
    uk_chars = set("іїєґІЇЄҐ")
    if any(char in text for char in uk_chars) or any(w in text_lower for w in ["привіт", "як", "що", "дякую", "будь ласка"]):
        return "uk"
    # Перевірка на німецьку
    de_words = ["hallo", "wie", "was", "bitte", "danke", "guten", "ich", "du"]
    if any(w in text_lower for w in de_words) or "ä" in text_lower or "ö" in text_lower or "ü" in text_lower or "ß" in text_lower:
        return "de"
    # Перевірка на англійську
    en_words = ["hello", "hi", "how", "what", "please", "thanks", "want", "baby", "you"]
    if any(w in text_lower for w in en_words):
        return "en"
    # За замовчуванням російська або якщо схоже на неї
    return "ru"

async def send_paywall_invoice(chat_id: int, lang: str):
    titles = {
        "uk": "Безлімітний VIP Доступ 18+",
        "ru": "Безлимитный VIP Доступ 18+",
        "en": "Unlimited VIP Access 18+",
        "de": "Unbegrenzter VIP-Zugang 18+"
    }
    descriptions = {
        "uk": "Ви вичерпали 7 безкоштовних повідомлень. Оплатіть підписку за 990 Stars для безлімітного спілкування та ексклюзивного контенту!",
        "ru": "Вы исчерпали 7 бесплатных сообщений. Оплатите подписку за 990 Stars для безлимитного общения и эксклюзивного контента!",
        "en": "You have used up your 7 free messages. Pay the subscription for 990 Stars for unlimited chatting and exclusive content!",
        "de": "Du hast deine 7 kostenlosen Nachrichten aufgebraucht. Bezahle das Abonnement für 990 Stars für unbegrenzten Chat und exklusive Inhalte!"
    }
    labels = {
        "uk": "VIP Підписка (1 місяць)",
        "ru": "VIP Подписка (1 месяц)",
        "en": "VIP Subscription (1 month)",
        "de": "VIP-Abonnement (1 Monat)"
    }

    prices = [LabeledPrice(label=labels.get(lang, labels["en"]), amount=SUBSCRIPTION_PRICE)]
    await bot.send_invoice(
        chat_id=chat_id,
        title=titles.get(lang, titles["en"]),
        description=descriptions.get(lang, descriptions["en"]),
        payload="lerabuns_vip_990_stars",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="lerabuns-vip-access"
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
    
    lang = detect_language(message.text or "")
    profile = get_user_profile(message.from_user.id)
    
    if profile["is_subscribed"]:
        remains = {"uk": "Безліміт", "ru": "Безлимит", "en": "Unlimited", "de": "Unbegrenzt"}[lang]
    else:
        remains = str(FREE_LIMIT - profile["count"])

    if lang == "uk":
        welcome_text = f"Привіт, {message.from_user.first_name}! 😉\n\nЛаскаво просимо до **@Lerabuns18bot** 🔥\nТут на тебе чекають найгарячіші та найвідвертіші розмови без жодних табу.\n\n🎁 У тебе є **7 безкоштовних повідомлень** (Залишилося: {remains}).\nПиши мені будь-що!"
    elif lang == "de":
        welcome_text = f"Hallo, {message.from_user.first_name}! 😉\n\nWillkommen bei **@Lerabuns18bot** 🔥\nHier erwarten dich die heißesten und intimsten Gespräche ohne Tabus.\n\n🎁 Du hast **7 kostenlose Nachrichten** (Verbleibend: {remains}).\nSchreib mir einfach!"
    elif lang == "en":
        welcome_text = f"Hello, {message.from_user.first_name}! 😉\n\nWelcome to **@Lerabuns18bot** 🔥\nThe hottest and most intimate conversations without any taboos await you here.\n\n🎁 You have **7 free messages** (Remaining: {remains}).\nWrite to me anything!"
    else:
        welcome_text = f"Привет, {message.from_user.first_name}! 😉\n\nДобро пожаловать в **@Lerabuns18bot** 🔥\nЗдесь тебя ждут самые горячие и откровенные разговоры без табу.\n\n🎁 У тебя есть **7 бесплатных сообщений** (Осталось: {remains}).\nПиши мне что угодно!"

    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    lang = detect_language(message.text or "")
    await send_paywall_invoice(message.chat.id, lang)

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    lang = detect_language(message.text or "")
    profile = get_user_profile(message.from_user.id)
    profile["is_subscribed"] = True
    
    success_texts = {
        "uk": "🎉 **Вітаємо у VIP-клубі Lerabuns 18+!**\n\nВашу підписку на 990 Stars успішно активовано! Тепер у вас **безлімітний доступ** до відвертих відповідей та фото без обмежень! 🔥😈",
        "ru": "🎉 **Добро пожаловать в VIP-клуб Lerabuns 18+!**\n\nВаша подписка на 990 Stars успешно активирована! Теперь у вас **безлимитный доступ** к откровенным ответам и фото без ограничений! 🔥😈",
        "en": "🎉 **Welcome to the Lerabuns 18+ VIP Club!**\n\nYour 990 Stars subscription has been successfully activated! Now you have **unlimited access** to explicit answers and photos without limits! 🔥😈",
        "de": "🎉 **Willkommen im Lerabuns 18+ VIP Club!**\n\nDein 990 Stars Abonnement wurde erfolgreich aktiviert! Jetzt hast du **unbegrenzten Zugriff** auf explizite Antworten und Fotos ohne Limits! 🔥😈"
    }
    await message.answer(success_texts.get(lang, success_texts["en"]), parse_mode="Markdown")

@dp.message(F.text)
async def handle_user_message(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
        
    lang = detect_language(message.text or "")
    profile = get_user_profile(message.from_user.id)
    
    if not profile["is_subscribed"]:
        if profile["count"] >= FREE_LIMIT:
            limit_msgs = {
                "uk": "⛔ **Безкоштовний ліміт (7/7) вичерпано!**\n\nЩоб продовжити відверте спілкування та отримувати фото, придбайте підписку нижче:",
                "ru": "⛔ **Бесплатный лимит (7/7) исчерпан!**\n\nЧтобы продолжить откровенное общение и получать фото, приобретите подписку ниже:",
                "en": "⛔ **Free limit (7/7) exhausted!**\n\nTo continue explicit chatting and receiving photos, purchase the subscription below:",
                "de": "⛔ **Kostenloses Limit (7/7) aufgebraucht!**\n\nUm den expliziten Chat und Fotos fortzusetzen, kaufe das Abonnement unten:"
            }
            await message.answer(limit_msgs.get(lang, limit_msgs["en"]), parse_mode="Markdown")
            await send_paywall_invoice(message.chat.id, lang)
            return
        
        profile["count"] += 1
    
    item = random.choice(CONTENT_DATABASE.get(lang, CONTENT_DATABASE["en"]))
    
    if not profile["is_subscribed"]:
        remains_count = FREE_LIMIT - profile["count"]
        remains_texts = {
            "uk": f"\n\n*(Безкоштовних повідомлень залишилось: {remains_count})*",
            "ru": f"\n\n*(Бесплатных сообщений осталось: {remains_count})*",
            "en": f"\n\n*(Free messages remaining: {remains_count})*",
            "de": f"\n\n*(Kostenlose Nachrichten übrig: {remains_count})*"
        }
        remains_text = remains_texts.get(lang, remains_texts["en"])
    else:
        remains_text = ""
    
    full_text = item["text"] + remains_text
    
    await message.answer_photo(
        photo=item["photo"],
        caption=full_text
    )

async def handle(request):
    return web.Response(text="Lerabuns 18+ Bot is active!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    print("Бот @Lerabuns18bot успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


