import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import json,bcrypt

ASK_EMAIL = 1

async def forgotpass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ('Baik, bisa tolong sebutkan emailnya?')
    await update.message.reply_text(message)
    return ASK_EMAIL
    
# ask email for forgot password
async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    await update.message.reply_text(f"Password baru sudah dikirim ke email {email}")
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ok, terima kasih.')
    return ConversationHandler.END

forgotpass_convhandler = ConversationHandler(
    entry_points=[CommandHandler("forgotpass", forgotpass_command)],
    states={
        ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
    },
    fallbacks=[CommandHandler("cancel", cancel_command)]
)
