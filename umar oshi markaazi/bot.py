import logging
import os
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue

# Replace these values after you get your bot token and target chat ID.
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8951671390:AAGHyK2lt6LgYiNjYmpecjRI37wmYb_bJW0')
TARGET_CHAT_ID = int(os.environ.get('TELEGRAM_TARGET_CHAT_ID', '0'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MENU_ITEMS = [
    {'id': 'o1', 'name': 'Toshkent oshi', 'price': 28000},
    {'id': 'o2', 'name': 'To‘y oshi', 'price': 34000},
    {'id': 'o3', 'name': 'Norin qo‘shilgan osh', 'price': 36000},
    {'id': 'o4', 'name': 'Qovurma osh', 'price': 30000},
    {'id': 'sa1', 'name': 'Achichuq', 'price': 12000},
    {'id': 'sa2', 'name': 'Vinegret', 'price': 14000},
    {'id': 'sa3', 'name': 'Koreys salati', 'price': 15000},
    {'id': 'i1', 'name': 'Manti', 'price': 24000},
    {'id': 'i2', 'name': 'Lag‘mon', 'price': 26000},
    {'id': 'i3', 'name': 'Shashlik', 'price': 18000},
    {'id': 'i4', 'name': 'Somsa', 'price': 8000},
    {'id': 'sh1', 'name': 'Sho‘rva', 'price': 19000},
    {'id': 'sh2', 'name': 'Mastava', 'price': 17000},
    {'id': 'n1', 'name': 'Patir non', 'price': 9000},
    {'id': 'n2', 'name': 'Oddiy tandir non', 'price': 6000},
    {'id': 'd1', 'name': 'Choy (choynak)', 'price': 6000},
    {'id': 'd2', 'name': 'Ayron', 'price': 8000},
    {'id': 'd3', 'name': 'Kompot', 'price': 9000},
    {'id': 'q1', 'name': 'Achchiq sous', 'price': 4000},
    {'id': 'q2', 'name': 'Ketchup', 'price': 3000},
]

sold_items = {}
chat_id_storage: Optional[int] = None


def format_menu() -> str:
    lines = ['📋 *Bugungi menyu va narxlar:*']
    for item in MENU_ITEMS:
        lines.append(f"{item['name']} — {item['price']:,} so'm")
    lines.append('\nTaom sotib olish uchun: /buy <taom nomi>')
    return '\n'.join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id_storage
    chat_id_storage = update.effective_chat.id
    text = (
        'Assalomu alaykum! \n'
        'Men ovqatlar narxini har 5 daqiqada yuboraman. '\n'
        'Agar taom olmoqchi bo\'lsangiz, /buy <taom nomi> buyrug\'ini yuboring.\n\n'
        'Menyu uchun: /menu\n'
        'Chat ID olish uchun: /chatid'
    )
    await update.message.reply_text(text)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown_v2(format_menu())


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Bu chat ID: {update.effective_chat.id}')


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.first_name or 'Foydalanuvchi'
    item_name = ' '.join(context.args).strip()
    if not item_name:
        await update.message.reply_text('Iltimos, /buy <taom nomi> shaklida yozing.')
        return

    matched_item = None
    for item in MENU_ITEMS:
        if item_name.lower() in item['name'].lower():
            matched_item = item
            break

    if not matched_item:
        await update.message.reply_text('Kechirasiz, bu taom menyuda yo‘q. Iltimos, aniq nom yozing.')
        return

    if sold_items.get(matched_item['id']):
        await update.message.reply_text(f"{matched_item['name']} allaqachon sotib olinib bo'lingan.")
        return

    sold_items[matched_item['id']] = user
    await update.message.reply_text(f"✅ {matched_item['name']} ni {user} oldi!")

    dest_chat_id = TARGET_CHAT_ID or chat_id_storage
    if dest_chat_id:
        await context.bot.send_message(
            chat_id=dest_chat_id,
            text=f"📣 *Sotildi:* {matched_item['name']} — {matched_item['price']:,} so'm\n👤 {user} oldi.",
            parse_mode='MarkdownV2',
        )


async def send_menu_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    dest_chat_id = TARGET_CHAT_ID or chat_id_storage
    if not dest_chat_id:
        logger.warning('Chat ID hali o‘rnatilmadi. /start tugmasini bosib qayta urin.')
        return

    await context.bot.send_message(chat_id=dest_chat_id, text=format_menu(), parse_mode='MarkdownV2')


async def send_menu_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dest_chat_id = TARGET_CHAT_ID or chat_id_storage
    if not dest_chat_id:
        await update.message.reply_text('Chat ID hali o‘rnatilmadi. /start tugmasini bosib qayta urin yoki TELEGRAM_TARGET_CHAT_ID ni sozlang.')
        return

    await context.bot.send_message(chat_id=dest_chat_id, text=format_menu(), parse_mode='MarkdownV2')
    await update.message.reply_text('Menu hozir kanalga yuborildi.')


def main() -> None:
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        raise RuntimeError('Iltimos, BOT_TOKEN ni bot.py ichiga yoki TELEGRAM_BOT_TOKEN atrof muhit o‘zgaruvchisiga qoʻying.')

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(CommandHandler('buy', buy))
    application.add_handler(CommandHandler('chatid', chatid))
    application.add_handler(CommandHandler('sendmenu', send_menu_now))

    job_queue: JobQueue = application.job_queue
    job_queue.run_repeating(send_menu_job, interval=300, first=10)

    logger.info('Bot ishga tushdi. Har 5 daqiqada menyu yuboriladi.')
    application.run_polling()


if __name__ == '__main__':
    main()
