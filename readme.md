# Morse Code Telegram Bot

A Telegram bot that lets you:

1. send Telegram messages in morse code (with customizable WPM, frequency etc.)
2. train receiving morse code (by receiving random words or fortune texts)

## Dependencies

First install the Python packages required with (use `--user` or `sudo` as appropriate):

```bash
pip3 install -r requirements.txt
```

Then install the dependencies of `pydub` by following its official instructions here: [https://github.com/jiaaro/pydub](https://github.com/jiaaro/pydub). Note that `ffmpeg` might not work (due to `opus` codec support), therefore `libav` is recommended.

## Running

Then simply run:

```bash
python3 bot.py <bot_id> <bot_token>
```

- replace `<bot_id>` with the Bot ID without `@`
- replace `<bot_token>` with the token

