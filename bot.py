import os
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter
import telegram
import datetime
import time
import logging
import bot_config
import morse


class MentionFilter(BaseFilter):
    """
    Filter class that works in both private chat and group chat
    Applying method match() for both private messages and mention messages
    """

    def match(self, message):
        # doing a certain pattern matching
        # it will be applied to both private chat (with no extra checking)
        # and group chat (with checking for the mentioning)
        # should return true or false
        raise NotImplementedError('Must override match()!')

    def filter(self, message):
        if message.text is None:
            logging.warning("Message type is null, trying disabling privacy mode")
            return False
        else:
            # if this is a private chat
            if message.chat.type == telegram.Chat.PRIVATE:
                return self.match(message)
            # if this is a group chat
            elif message.chat.type == telegram.Chat.GROUP:
                mentioned = bot_config.bot_id in message.text
                return mentioned and self.match(message)


class AnyTextFilter(MentionFilter):
    """
    Return true for any private message or mention messages
    """

    def match(self, message):
        return True


def send_morse_code_as_audio(bot, update):
    logging.info("Send morse code request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                 update.effective_user.username))

    # create a filename for this update
    timestamp_string = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S-%f')
    file_name = "{}-{}.mp3".format(timestamp_string, update.effective_user.username)

    # remove the mentioning part from the text
    text = update.message.text.replace("@" + bot_config.bot_id, "")
    morse.text_to_audio(text, file_name, "mp3")

    with open(file_name, "rb") as audio_file:
        bot.send_audio(
            chat_id=update.message.chat_id,
            audio=audio_file,
            caption=text,
            reply_to_message_id=update.message.message_id
        )

    # delete the file
    try:
        os.remove(file_name)
    except OSError:
        pass


def send_morse_code_as_voice(bot, update):
    logging.info("Send morse code request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                 update.effective_user.username))

    # create a filename for this update
    timestamp_string = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S-%f')
    file_name = "{}-{}.ogg".format(timestamp_string, update.effective_user.username)

    # remove the mentioning part from the text
    text = update.message.text.replace("@" + bot_config.bot_id, "")
    morse.text_to_audio(text, file_name, "ogg", "opus")

    with open(file_name, "rb") as audio_file:
        bot.send_voice(
            chat_id=update.message.chat_id,
            voice=audio_file,
            reply_to_message_id=update.message.message_id
        )

    # delete the file
    try:
        os.remove(file_name)
    except OSError:
        pass


def start(bot, update):
    update.message.reply_text("Hi! Text me anything!")


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater = Updater(token=bot_config.token)
    dispatcher = updater.dispatcher

    any_text_filter = AnyTextFilter()

    start_handler = CommandHandler('start', start)

    send_morse_code_handler = MessageHandler(any_text_filter, send_morse_code_as_voice)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(send_morse_code_handler)

    updater.start_polling()
    updater.idle()  # so the bot can gracefully close


if __name__ == "__main__":
    main()
