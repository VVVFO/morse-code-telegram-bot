import math
import pyaudio
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


def interval_to_wave_data_segment(interval, frame_rate, frequency, unit_length_seconds):
    is_on, unit = interval
    num_frames = frame_rate * unit * unit_length_seconds
    result = ''
    for x in range(int(num_frames)):
        if is_on:
            result += chr(int(math.sin(x / ((frame_rate / frequency) / math.pi)) * 127 + 128))
        else:
            result += chr(int(128))
    return result


def intervals_to_sound(intervals, frame_rate, frequency, unit_length_seconds):
    wave_data = ''
    total_length = 0
    for interval in intervals:
        wave_data += interval_to_wave_data_segment(
            interval,
            frame_rate,
            frequency,
            unit_length_seconds
        )
        total_length += interval[1]
    # handling the ending part
    print(total_length)
    for x in range(int(total_length * frame_rate) % frame_rate):
        wave_data += chr(int(128))
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(1),
                    channels=1,
                    rate=frame_rate,
                    output=True)
    stream.write(wave_data)
    stream.stop_stream()
    stream.close()


if __name__ == "__main__":
    # e = encode_sentence("PARIS PARIS")
    # print(e)
    # sum = 0
    # for char in e:
    #     _, length = CODE_TO_INTERVAL_TABLE[char]
    #     sum += length
    # print(sum)
    intervals_to_sound(sentence_to_intervals("PARIS PARIS"), FRAME_RATE, FREQUENCY, UNIT_LENGTH_SECONDS)
