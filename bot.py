# lbraries for create bot
from telegram.ext import Updater,CommandHandler,MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.filters import Filters
import kenlm
from lm import *
import Levenshtein
import logging

# load and prepare model to correct words
model = kenlm.LanguageModel("language_model/airi.bin")
model.vocab = prepare_unigram_set("language_model/airi.arpa", model)

def start(update,context):
    update.message.reply_text(
        f'Assalomu alaykum, botdan foydalanish uchun biror gap jo\'nating!!!'
        )

def buyruq(update, context):
    chat_id = update.message.chat.id
    text_user = update.message.text
    result = recycle_sentence(model, text_user)
    context.bot.send_message(
        chat_id=chat_id,
        text=result
    )



updater = Updater(token="6112868019:AAHwGOfVnclWVim7vVO6Ys-uBP95mlyV9i4")
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('restart', start))
dispatcher.add_handler(MessageHandler(Filters.text, buyruq))

updater.start_polling()
updater.idle()
