from pydub.generators import Sine
from pydub import AudioSegment
import morse_config

# the default (libav) doesn't work somehow, dirty hack time :(
AudioSegment.converter = "ffmpeg"

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
                      '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--',
                      '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}


def encode_word(word):
    char_codes = []
    for character in word:
        # to add an one-unit-pause between each . and -
        # ignore if the character is not found in the table
        char_codes.append(" ".join(list(CHAR_TO_CODE_TABLE.get(character.upper(), ""))))
    return "   ".join(char_codes)  # three units between words


def encode_sentence(sentence):
    return "       ".join(encode_word(word) for word in sentence.split(' '))  # seven units between sentences


def sentence_to_intervals(sentence):
    return [CODE_TO_INTERVAL_TABLE[character] for character in encode_sentence(sentence)]


def interval_to_wave_data_segment(interval, frequency, unit_length_seconds):
    is_on, length = interval
    if is_on:
        return Sine(frequency).to_audio_segment(length * unit_length_seconds * 1000)
    else:
        return Sine(0).to_audio_segment(length * unit_length_seconds * 1000)


def intervals_to_ogg(intervals, frequency, unit_length_seconds, file_name):
    segment = Sine(0).to_audio_segment(morse_config.CROSS_FADE_MS)  # silence at the beginning for cross-fade
    for interval in intervals:
        segment = segment.append(interval_to_wave_data_segment(interval, frequency, unit_length_seconds),
                                 crossfade=morse_config.CROSS_FADE_MS)
    segment.export(file_name, format="ogg")


if __name__ == "__main__":
    intervals_to_ogg(sentence_to_intervals("hello world"),
                     morse_config.FREQUENCY,
                     morse_config.UNIT_LENGTH_SECONDS,
                     "test.ogg")
