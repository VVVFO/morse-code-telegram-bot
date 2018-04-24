import os
import random
import subprocess
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, BaseFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import datetime
import time
import logging
import bot_config
import morse
import user_states


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


class MorseBot:
    def __init__(self):
        # instantiate and initialize database manager
        self.db = user_states.UserStateManager(bot_config.DATABASE_NAME,
                                               bot_config.TABLE_NAME)

    def send_morse_code_voice_to(self,
                                 bot,
                                 username,
                                 text,
                                 chat_id,
                                 reply_to_message_id=None,
                                 frequency=None,
                                 wpm=None,
                                 reply_markup=None):
        # create a filename for this update
        timestamp_string = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S-%f')
        file_name = "{}-{}.ogg".format(timestamp_string, username)

        morse.text_to_audio(text,
                            file_name,
                            "ogg",
                            codec="opus",
                            frequency=frequency,
                            wpm=wpm)

        with open(file_name, "rb") as audio_file:
            bot.send_voice(
                chat_id=chat_id,
                voice=audio_file,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup
            )

        # delete the file
        try:
            os.remove(file_name)
        except OSError:
            pass

    def set_frequency(self, bot, update, args):
        # parsing argument as int
        try:
            new_frequency = int(args[0])
            if new_frequency <= 0 or new_frequency > 2000:
                raise ValueError()
        except ValueError:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please input an integer between 0 and 2000 after \\setfrequency"
            )
            return
        logging.info("Setting {}'s frequency to {}".format(
            update.message.from_user.id,
            new_frequency
        ))
        self.db.set_frequency(update.message.from_user.id,
                              new_frequency)

    def set_wpm(self, bot, update, args):
        # parsing argument as int
        try:
            new_wpm = int(args[0])
            if new_wpm <= 5 or new_wpm > 50:
                raise ValueError()
        except ValueError:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please input an integer between 5 and 50 after \\setwpm"
            )
            return
        logging.info("Setting {}'s wpm to {}".format(
            update.message.from_user.id,
            new_wpm
        ))
        self.db.set_wpm(update.message.from_user.id,
                        new_wpm)

    def reply_morse_code_to_text(self, bot, update):
        logging.info("Send morse code request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                     update.effective_user.username))

        text = update.message.text.replace("@" + bot_config.bot_id, "")
        self.send_morse_code_voice_to(bot,
                                      update.message.from_user.username,
                                      text,
                                      update.message.chat_id,
                                      reply_to_message_id=update.message.message_id,
                                      frequency=self.db.get_frequency(update.message.from_user.id),
                                      wpm=self.db.get_wpm(update.message.from_user.id))

    def random_fortune(self, bot, update):
        logging.info("Random fortune request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                    update.effective_user.username))
        fortune_text = subprocess.run(["fortune", "-s", "-n", "{}".format(bot_config.MAXIMUM_FORTUNE_LENGTH)],
                                      stdout=subprocess.PIPE).stdout.decode("ascii")
        keyboard = [[InlineKeyboardButton("Show Text",
                                          callback_data=fortune_text[:bot_config.MAXIMUM_FORTUNE_LENGTH])]]
        # to not go greater than the 64 byte limit
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.send_morse_code_voice_to(bot,
                                      update.effective_user.username,
                                      fortune_text,
                                      update.message.chat_id,
                                      reply_to_message_id=update.message.message_id,
                                      frequency=self.db.get_frequency(update.message.from_user.id),
                                      wpm=self.db.get_wpm(update.message.from_user.id),
                                      reply_markup=reply_markup)

    def random_word(self, bot, update):
        logging.info("Random fortune request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                    update.effective_user.username))
        fortune_text = subprocess.run(["fortune"], stdout=subprocess.PIPE).stdout.decode("ascii")
        random_word = random.choice(fortune_text.split(' '))
        keyboard = [[InlineKeyboardButton("Show Text",
                                          callback_data=random_word[:bot_config.MAXIMUM_FORTUNE_LENGTH])]]
        # to not go over the 64 byte limit
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.send_morse_code_voice_to(bot,
                                      update.effective_user.username,
                                      random_word,
                                      update.message.chat_id,
                                      reply_to_message_id=update.message.message_id,
                                      frequency=self.db.get_frequency(update.message.from_user.id),
                                      wpm=self.db.get_wpm(update.message.from_user.id),
                                      reply_markup=reply_markup)


def show_text_callback(bot, update):
    """
    Being the callback of fortune text and word texts
    The callback query data contains the question and answer text
    """
    # bot.send_message(chat_id=update.callback_query.from_user.id,
    #                  text=update.callback_query.data)
    bot.answer_callback_query(update.callback_query.id,
                              text="\"{}\"".format(update.callback_query.data.strip()),
                              show_alert=True)


def start(bot, update):
    update.message.reply_text("Hi! Text me anything!")


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater = Updater(token=bot_config.token)
    dispatcher = updater.dispatcher

    morse_bot = MorseBot()

    any_text_filter = AnyTextFilter()

    start_handler = CommandHandler('start', start)
    fortune_handler = CommandHandler('fortune', morse_bot.random_fortune)
    random_word_handler = CommandHandler('random_word', morse_bot.random_word)
    set_frequency_handler = CommandHandler('setfrequency', morse_bot.set_frequency, pass_args=True)
    set_wpm = CommandHandler('setwpm', morse_bot.set_wpm, pass_args=True)

    send_morse_code_handler = MessageHandler(any_text_filter, morse_bot.reply_morse_code_to_text)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(fortune_handler)
    dispatcher.add_handler(random_word_handler)
    dispatcher.add_handler(set_frequency_handler)
    dispatcher.add_handler(set_wpm)
    dispatcher.add_handler(send_morse_code_handler)
    dispatcher.add_handler(CallbackQueryHandler(show_text_callback))

    updater.start_polling()
    updater.idle()  # so the bot can gracefully close


if __name__ == "__main__":
    main()
