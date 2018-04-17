from pydub.generators import Sine
from pydub.playback import play
from config import FRAME_RATE, FREQUENCY, UNIT_LENGTH_SECONDS

CODE_TO_INTERVAL_TABLE = {
    '.': (True, 1),
    '-': (True, 3),
    ' ': (False, 1)
}

CHAR_TO_CODE_TABLE = {'A': '.-', 'B': '-...',
                      'C': '-.-.', 'D': '-..', 'E': '.',
                      'F': '..-.', 'G': '--.', 'H': '....',
                      'I': '..', 'J': '.---', 'K': '-.-',
                      'L': '.-..', 'M': '--', 'N': '-.',
                      'O': '---', 'P': '.--.', 'Q': '--.-',
                      'R': '.-.', 'S': '...', 'T': '-',
                      'U': '..-', 'V': '...-', 'W': '.--',
                      'X': '-..-', 'Y': '-.--', 'Z': '--..',
                      '1': '.----', '2': '..---', '3': '...--',
                      '4': '....-', '5': '.....', '6': '-....',
                      '7': '--...', '8': '---..', '9': '----.',
                      '0': '-----', ', ': '--..--', '.': '.-.-.-',
                      '?': '..--..', '/': '-..-.', '-': '-....-',
                      '(': '-.--.', ')': '-.--.-'
                      }


def encode_word(word):
    char_codes = []
    for character in word:
        # to add an one-unit-pause between each . and -
        char_codes.append(" ".join(list(CHAR_TO_CODE_TABLE.get(character.upper(), ""))))
    return "   ".join(char_codes)


def encode_sentence(sentence):
    return "       ".join(encode_word(word) for word in sentence.split(' '))


def sentence_to_intervals(sentence):
    return [CODE_TO_INTERVAL_TABLE[character] for character in encode_sentence(sentence)]


def interval_to_wave_data_segment(interval, frequency, unit_length_seconds):
    is_on, length = interval
    if is_on:
        return Sine(frequency).to_audio_segment(length * unit_length_seconds * 1000)
    else:
        return Sine(0).to_audio_segment(length * unit_length_seconds * 1000)


def intervals_to_sound(intervals, frequency, unit_length_seconds):
    segment = Sine(0).to_audio_segment(0)
    for interval in intervals:
        segment = segment.append(interval_to_wave_data_segment(interval, frequency, unit_length_seconds), crossfade=0)
    # handling the ending part
    play(segment)


if __name__ == "__main__":
    # e = encode_sentence("PARIS PARIS")
    # print(e)
    # sum = 0
    # for char in e:
    #     _, length = CODE_TO_INTERVAL_TABLE[char]
    #     sum += length
    # print(sum)
    intervals_to_sound(sentence_to_intervals("paris paris"), FREQUENCY, UNIT_LENGTH_SECONDS)
