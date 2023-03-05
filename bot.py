import os
import sys
import time
import logging, datetime, pytz
from revChatGPT.V1 import Chatbot
from telegram import BotCommand, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, filters
from config import MODE, NICK, config

chatbot = Chatbot(config)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

botNick = NICK.lower() if NICK is not None else None
botNicKLength = len(botNick) if botNick is not None else 0
print("nick:", botNick)

# In all other places characters
# _ * [ ] ( ) ~ ` > # + - = | { } . ! 
# must be escaped with the preceding character '\'.
def start(update, context): # Return text when user enters /start
    user = update.effective_user
    update.message.reply_html(
        rf"Hi {user.mention_html()} ! I am an Assistant, a large language model trained by OpenAI. I will do my best to help answer your questions.",
    )

def reset(update, context):
    chatbot.reset_chat()

def process_message(update, context):
    print(update.effective_user.username, update.effective_user.id, update.message.text)
    if NICK is None:
        chat_content = update.message.text
    else:
        if update.message.text[:botNicKLength].lower() != botNick: return
        chat_content = update.message.text[botNicKLength:].strip()

    chat_id = update.effective_chat.id
    response = ''
    LastMessage_id = ''
    try:
        for data in chatbot.ask(chat_content):
            try:
                response = data["message"]
            #     if LastMessage_id == '':
            #         message = context.bot.send_message(
            #             chat_id=chat_id,
            #             text=response,
            #         )
            #         LastMessage_id = message.message_id
            #         print("LastMessage_id", LastMessage_id)
            #         continue
            #     context.bot.edit_message_text(chat_id=chat_id, message_id=LastMessage_id, text=response)
            except:
                # print("response", data)
                if "reloading the conversation" in data:
                    chatbot.reset_chat()
                    message = context.bot.send_message(
                        chat_id=chat_id,
                        text="Conversation has exceeded the limit, chat has been reset, please try again！",
                    )
                    return
                if "conversation_id" in data:
                    continue
                message = context.bot.send_message(
                    chat_id=chat_id,
                    text="Unknown error：" + str(data),
                )
                return
        context.bot.send_message(
            chat_id=chat_id,
            text=response,
            reply_to_message_id=update.message.message_id,
        )
        print("getresult", response)
    except Exception as e:
        print("response_msg", response)
        print("Exception", e)
        print("Exception str", str(e))
        context.bot.send_message(
            chat_id=chat_id,
            text="Error! :(",
            parse_mode=ParseMode.MARKDOWN,
        )

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if ("can't" in str(context.error)):
        message = (
            f"There's an error! Please try again.\n\n"
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')

def unknown(update: Update, context: CallbackContext): # Return text when the user enters an unknown command
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def setup(token):
    if MODE == "dev": # Local debugging, need to hang proxy, here use surge
        updater = Updater(token, use_context=True, request_kwargs={
            'proxy_url': 'http://127.0.0.1:6152' # Proxy required to use telegram
        })
    elif MODE == "prod": # Production servers in the US, no proxy required
        updater = Updater(token, use_context=True)
    else:
        logger.error("Need to set MODE!")
        sys.exit(1)

    # set commands
    updater.bot.set_my_commands([
        BotCommand('start', 'Start the bot'),
        BotCommand('reset', 'reset the chat'),
        BotCommand('help', 'Help'),
    ])

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reset", reset))
    dispatcher.add_handler(MessageHandler(Filters.text, process_message))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.add_error_handler(error)

    return updater, dispatcher
