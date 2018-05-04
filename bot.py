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
import argparse


class MentionFilter(BaseFilter):
    """
    Filter class that works in both private chat and group chat
    Applying method match() for both private messages and mention messages
    """

    def __init__(self, bot_id):
        # super(self.__class__, self).__init__(**kwargs)
        self.bot_id = bot_id

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
                mentioned = self.bot_id in message.text
                return mentioned and self.match(message)


class AnyTextFilter(MentionFilter):
    """
    Return true for any private message or mention messages
    """

    def match(self, message):
        return True


class MorseBot:
    def __init__(self, bot_id, bot_token):
        # instantiate and initialize database manager
        self.db = user_states.UserStateManager(bot_config.DATABASE_NAME,
                                               bot_config.TABLE_NAME)

        # set up frequent word list
        with open(bot_config.WORD_LIST_FILE_NAME, "r") as f:
            word_list = [line.strip() for line in f.readlines()]

        self.word_list = word_list
        self.bot_id = bot_id
        self.bot_token = bot_token

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
            if new_frequency <= 100 or new_frequency > 2000:
                raise ValueError()
        except ValueError:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please input an integer between 100 and 2000 after \\setfrequency"
            )
            return
        logging.info("Setting {}'s frequency to {}".format(
            update.message.from_user.id,
            new_frequency
        ))
        self.db.set_frequency(update.message.from_user.id,
                              new_frequency)

        update.message.reply_text("Frequency for {} set to {}!".format(update.message.from_user.username,
                                                                       new_frequency))

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

        update.message.reply_text("WPM for {} set to {}!".format(update.message.from_user.username,
                                                                 new_wpm))

    def reply_morse_code_to_text(self, bot, update):
        logging.info("Send morse code request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                     update.effective_user.username))

        text = update.message.text.replace("@" + self.bot_id, "")
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
        # to not go over than the 64 byte limit
        keyboard = [[InlineKeyboardButton("Show Text",
                                          callback_data=fortune_text[:bot_config.MAXIMUM_FORTUNE_LENGTH])]]
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
        logging.info("Random word request received, id: {}, username: {}".format(update.effective_user.id,
                                                                                 update.effective_user.username))
        random_word = random.choice(self.word_list)
        # to not go over the 64 byte limit
        keyboard = [[InlineKeyboardButton("Show Text",
                                          callback_data=random_word[:bot_config.MAXIMUM_FORTUNE_LENGTH])]]
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
    bot.answer_callback_query(update.callback_query.id,
                              text="\"{}\"".format(update.callback_query.data.strip()),
                              show_alert=True)


def start(bot, update):
    update.message.reply_text("Hi! Text me anything!")


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("bot_id", help="Bot ID without '@'")
    parser.add_argument("token", help="Bot token")
    args = parser.parse_args()

    return args.bot_id, args.token


def run_bot(bot_id, bot_token):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher

    morse_bot = MorseBot(bot_id, bot_token)

    any_text_filter = AnyTextFilter(bot_id)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('fortune', morse_bot.random_fortune))
    dispatcher.add_handler(CommandHandler('word', morse_bot.random_word))
    dispatcher.add_handler(CommandHandler('setfrequency', morse_bot.set_frequency, pass_args=True))
    dispatcher.add_handler(CommandHandler('setwpm', morse_bot.set_wpm, pass_args=True))
    dispatcher.add_handler(MessageHandler(any_text_filter, morse_bot.reply_morse_code_to_text))
    dispatcher.add_handler(CallbackQueryHandler(show_text_callback))

    updater.start_polling()
    updater.idle()  # so the bot can gracefully close


if __name__ == "__main__":
    bot_id, bot_token = parse_command_line_arguments()
    run_bot(bot_id, bot_token)
