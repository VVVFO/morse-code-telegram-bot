# Morse Code Telegram Bot

## Dependencies

First install the Python packages required with (use `--user` or `sudo` as appropriate):

```bash
pip3 install -r requirements.txt
```

Then install the dependencies of `pydub` by following its official instructions here: [https://github.com/jiaaro/pydub](https://github.com/jiaaro/pydub). Note that `ffmpeg` might not work (due to `opus` codec support), therefore `libav` is recommended.

## Running

Create a configuration file with:

```bash
mv bot_config.example.py bot_config.py
```

Edit `bot_config.py` then fill in `bot_id` and `token`.

Then simply run:

```bash
python3 bot.py
```

