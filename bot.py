from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8849386246:AAEKJWj9uKJMI3PdkOTookVGZrcLGudClkw"

ADMINS = [
    1628119985,
    6506671718,
    1810163607
]

FIO, PHONE, DISTRICT, TEXT, FILE = range(5)

counter = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Assalomu alaykum!\n\n"
        "Respublika Tez Tibbiy Yordam Markazi Toshkent viloyati filiali "
        "murojaatlar botiga xush kelibsiz.\n\n"
        "✍️ F.I.Sh. kiriting:"
    )
    return FIO


async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📍 Tuman/Shahar nomini kiriting:")
    return DISTRICT


async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["district"] = update.message.text
    await update.message.reply_text("📝 Murojaat matnini kiriting:")
    return TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text

    await update.message.reply_text(
        "📎 Foto yoki fayl yuboring.\n\n"
        "Agar ilova qilmoqchi bo‘lmasangiz /skip yuboring."
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
    
    user_id = update.effective_user.id

    # Admin xabaridan user_id ni topib olish uchun uni matn ichiga HTML havola ko'rinishida berkitamiz
    text = (
        f"📨 YANGI MUROJAAT\n\n"
        f"🆔 {appeal_id}\n\n"
        f"👤 F.I.Sh.: {context.user_data['fio']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"📍 Hudud: {context.user_data['district']}\n\n"
        f"📝 Murojaat:\n\n"
        f"{context.user_data['text']}\n"
        f"<a href='tg://user?id={user_id}'>&#8203;</a>"  # Ko'rinmas havola (User ID ni saqlaydi)
    )

    for admin in ADMINS:
        try:
            await context.bot.send_message(admin, text, parse_mode="HTML")

            if attachment:
                if attachment.photo:
                    await context.bot.send_photo(
                        admin,
                        attachment.photo[-1].file_id
                    )

                elif attachment.document:
                    await context.bot.send_document(
                        admin,
                        attachment.document.file_id
                    )

        except Exception as e:
            print(f"Xatolik: {e}")

    await update.message.reply_text(
        f"✅ Murojaatingiz qabul qilindi.\n\n"
        f"🆔 Murojaat raqami: {appeal_id}\n\n"
        f"📌 Murojaatingiz 15 kungacha bo'lgan muddat davomida "
        f"ko'rib chiqiladi va javob beriladi."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Murojaat bekor qilindi.")
    return ConversationHandler.END


# Admin javobini foydalanuvchiga yuboruvchi yangi funksiya
async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat belgilangan adminlar guruhidan yoki chatidan kelgan xabarlarni tekshiramiz
    if update.effective_user.id not in ADMINS:
        return

    # Reply qilingan xabarni tekshiramiz
    reply_to = update.message.reply_to_message
    if not reply_to:
        return

    # Xabarning entities qismidan yashirin tg://user?id=... havolasini qidiramiz
    user_id = None
    if reply_to.entities:
        for entity in reply_to.entities:
            if entity.type == "text_link" and entity.url.startswith("tg://user?id="):
                user_id = int(entity.url.split("id=")[1])
                break

    if not user_id:
        # Agar rasm yoki fayl ostidagi matnga reply qilingan bo'lsa, caption entities tekshiriladi
        if reply_to.caption_entities:
            for entity in reply_to.caption_entities:
                if entity.type == "text_link" and entity.url.startswith("tg://user?id="):
                    user_id = int(entity.url.split("id=")[1])
                    break

    if user_id:
        try:
            # Admindan kelgan xabarni foydalanuvchiga yuboramiz
            reply_text = f"🔔 <b>Murojaatingizga javob xati keldi:</b>\n\n{update.message.text}"
            await context.bot.send_message(chat_id=user_id, text=reply_text, parse_mode="HTML")
            await update.message.reply_text("✅ Javobingiz foydalanuvchiga muvaffaqiyatli yetkazildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Javobni yuborishda xatolik (Foydalanuvchi botni bloklagan bo'lishi mumkin): {e}")
    else:
        await update.message.reply_text("⚠️ Xatolik: Foydalanuvchi ID-si aniqlanmadi. Faqat matnli murojaat xabarining o'ziga 'Reply' qilib javob yozing.")


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio),
                CommandHandler("start", start),
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CommandHandler("start", start),
            ],
            DISTRICT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_district),
                CommandHandler("start", start),
            ],
            TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_text),
                CommandHandler("start", start),
            ],
            FILE: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, get_file),
                CommandHandler("skip", skip_file),
                CommandHandler("start", start),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    
    # Admin javoblarini tutib oluvchi yangi handler (ConversationHandler'dan tashqarida bo'lishi kerak)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply_handler))

    print("✅ Bot ishga tushdi...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
