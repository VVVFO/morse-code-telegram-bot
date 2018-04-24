from pydub.generators import Sine

# the default (libav) doesn't work somehow due to the mystic parameter "write_xing"
# this dirty hack makes the issue go away
# I have opened an issue for pydub at https://github.com/jiaaro/pydub/issues/269
import sys

sys.platform = "something else"
# or change the converter to ffmpeg like that, but it doesn't support opus well :(
# from pydub import AudioSegment
# AudioSegment.converter = "ffmpeg"

# (State, Length in units)
CODE_TO_INTERVAL_TABLE = {
    '.': (True, 1),
    '-': (True, 3),
    ' ': (False, 1)
}

CHAR_TO_CODE_TABLE = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                      'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                      'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                      'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                      '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ',': '--..--',
                      '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}


def encode_word(word):
    char_codes = []
    for character in word:
        # to add an one-unit-pause between each . and -
        # ignore if the character is not found in the table
        char_codes.append(" ".join(list(CHAR_TO_CODE_TABLE.get(character.upper(), ""))))
    return "   ".join(char_codes)  # three units between letters


def encode_sentence(sentence):
    return "       ".join(encode_word(word) for word in sentence.split(' '))  # seven units between words


def sentence_to_intervals(sentence):
    return [CODE_TO_INTERVAL_TABLE[character] for character in encode_sentence(sentence)]


def interval_to_wave_data_segment(interval, frequency, unit_length_seconds):
    is_on, length = interval
    if is_on:
        return Sine(frequency).to_audio_segment(length * unit_length_seconds * 1000)
    else:
        return Sine(0).to_audio_segment(length * unit_length_seconds * 1000)


def wpm_to_unit_length_seconds(wpm):
    return 60 / (wpm * 50)


def text_to_audio(text,
                  file_name,
                  format,
                  codec=None,  # None for default
                  frequency=700,
                  wpm=10,
                  cross_fade=2):
    unit_length_seconds = wpm_to_unit_length_seconds(wpm)
    intervals = sentence_to_intervals(text)
    segment = Sine(0).to_audio_segment(cross_fade)  # silence at the beginning for cross-fade
    for interval in intervals:
        segment = segment.append(interval_to_wave_data_segment(interval, frequency, unit_length_seconds),
                                 crossfade=cross_fade)
    segment.export(file_name,
                   format=format,
                   codec=codec)


if __name__ == "__main__":
    text_to_audio("hello world", "test.ogg", "ogg")
