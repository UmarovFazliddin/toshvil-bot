from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8610344867:AAF2iE9avasPQvupLyVaBnFG2FaRg7PTRII"

ADMINS = [
    1628119985,
    6506671718,
    1810163607
]

FIO, PHONE, DISTRICT, TEXT, FILE = range(5)

counter = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum!\n\n"
        "Respublika Tez Tibbiy Yordam Markazi Toshkent viloyati filiali murojaatlar botiga xush kelibsiz.\n\n"
        "F.I.Sh. kiriting:"
    )
    return FIO


async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Tuman/Shahar nomini kiriting:")
    return DISTRICT


async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["district"] = update.message.text
    await update.message.reply_text("Murojaat matnini kiriting:")
    return TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text
    await update.message.reply_text(
        "Foto yoki fayl yuboring.\n"
        "Agar ilova qilmoqchi bo'lmasangiz /skip buyrug'ini yuboring."
    )
    return FILE


async def skip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_to_admins(update, context, None)
    return ConversationHandler.END


async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_to_admins(update, context, update.message)
    return ConversationHandler.END


async def send_to_admins(update, context, attachment):
    global counter

    appeal_id = f"2026-{counter:04d}"
    counter += 1

    text = f"""
📨 YANGI MUROJAAT

🆔 {appeal_id}

👤 F.I.Sh.: {context.user_data['fio']}
📞 Telefon: {context.user_data['phone']}
📍 Hudud: {context.user_data['district']}

📝 Murojaat:

{context.user_data['text']}
"""

    for admin in ADMINS:
        try:
            await context.bot.send_message(admin, text)

            if attachment:
                if attachment.photo:
                    photo = attachment.photo[-1].file_id
                    await context.bot.send_photo(admin, photo)

                elif attachment.document:
                    await context.bot.send_document(
                        admin,
                        attachment.document.file_id
                    )

        except Exception as e:
            print(e)

    await update.message.reply_text(
        f"Sizning murojaatingiz qabul qilindi.\n"
        f"Murojaat raqami: {appeal_id}"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
            FILE: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, get_file),
                CommandHandler("skip", skip_file),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
