import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# .env faylini yuklash
load_dotenv()

# Tokenni Render yoki lokal muhitdan olish
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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

    # Admin xabaridan foydalanuvchini aniqlash uchun matn oxiriga [User_ID: ...] kalitini qo'shamiz
    text = (
        f"📨 YANGI MUROJAAT\n\n"
        f"🆔 {appeal_id}\n\n"
        f"👤 F.I.Sh.: {context.user_data['fio']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"📍 Hudud: {context.user_data['district']}\n\n"
        f"📝 Murojaat:\n"
        f"{context.user_data['text']}\n\n"
        f"👤 Profil: <a href='tg://user?id={user_id}'>Foydalanuvchi sahifasi</a>\n"
        f"🔑 [User_ID: {user_id}]"
    )

    for admin in ADMINS:
        try:
            # Agar foydalanuvchi media yuborgan bo'lsa, bitta xabarda yuboramiz (caption yordamida)
            if attachment:
                if attachment.photo:
                    await context.bot.send_photo(
                        chat_id=admin,
                        photo=attachment.photo[-1].file_id,
                        caption=text,
                        parse_mode="HTML"
                    )
                elif attachment.document:
                    await context.bot.send_document(
                        chat_id=admin,
                        document=attachment.document.file_id,
                        caption=text,
                        parse_mode="HTML"
                    )
                else:
                    await context.bot.send_message(chat_id=admin, text=text, parse_mode="HTML")
            else:
                # Agar fayl bo'lmasa, faqat matn o'zi ketadi
                await context.bot.send_message(chat_id=admin, text=text, parse_mode="HTML")

        except Exception as e:
            print(f"Xatolik (Admin {admin}): {e}")

    await update.message.reply_text(
        f"✅ Murojaatingiz qabul qilindi.\n\n"
        f"🆔 Murojaat raqami: {appeal_id}\n\n"
        f"📌 Murojaatingiz ko'rib chiqiladi va javob beriladi.\n"
        f"Yangi murojaat qoldirish uchun /start bosing."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Murojaat bekor qilindi. Qayta boshlash uchun /start bosing.")
    return ConversationHandler.END


async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    reply_to = update.message.reply_to_message
    if not reply_to:
        return

    user_id = None
    
    # Kelgan xabarning matnidan (text) yoki media ostidagi izohidan (caption) Regex orqali ID raqamini qidiramiz
    target_text = reply_to.text or reply_to.caption
    if target_text:
        match = re.search(r"\[User_ID:\s*(\d+)\]", target_text)
        if match:
            user_id = int(match.group(1))

    if user_id:
        try:
            reply_text = f"🔔 <b>Murojaatingizga javob xati keldi:</b>\n\n{update.message.text}"
            await context.bot.send_message(chat_id=user_id, text=reply_text, parse_mode="HTML")
            await update.message.reply_text("✅ Javobingiz foydalanuvchiga muvaffaqiyatli yetkazildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Javobni yuborishda xatolik: {e}")
    else:
        await update.message.reply_text("⚠️ Xatolik: Foydalanuvchi ID-si aniqlanmadi. Iltimos, faqat bot yuborgan asosiy xabarga 'Reply' qiling.")


def main():
    if not TOKEN:
        print("❌ Xatolik: TELEGRAM_BOT_TOKEN muhit o'zgaruvchisi topilmadi!")
        return

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
                # filters.ALL qildik, har qanday holatda keyingi bosqichga o'tishi uchun
                MessageHandler(filters.ALL & ~filters.COMMAND, get_file),
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply_handler))

    print("✅ Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
