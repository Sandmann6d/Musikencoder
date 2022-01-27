# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 12:57:56 2020

@author: User
"""
import sounddevice as sd
import librosa
import librosa.display
import numpy as np
import random
from scipy.io import wavfile


sr = 44100 # Samples per second, should be reasonably high.
dur = 0.5 # Duration (in seconds) of sound per letter. sr*dur/2 should be an integer.
ampl = 0.15 # Amplitude of sine waves. Higher number leads to louder sound.

'''Listen to the sounds, or don't'''
play_while_encoding = True
play_while_decoding = False

'''Plot a chromagram or not'''
show_chromagram_while_encoding = False
show_chromagram_while_decoding = True

''' Choose lowest (can be negative) and highest octave. Octave 2 starts with middle C.'''
lowest_octave = 1
highest_octave = 3

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
            'ä', 'ö', 'ü', 'ß', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
            '-', ' ', '.', ',', ';', '!', '?']
    
hz = [65.40639132514966, 69.29565774421802, 73.41619197935188, 77.78174593052023, 
      82.4068892282175, 87.30705785825097, 92.4986056779086, 97.99885899543733, 
      103.82617439498628, 110.0, 116.54094037952248, 123.47082531403103]

c, csh, d, dsh, e, f, fsh, g, gsh, a, ash, b = hz[0], hz[1], hz[2], hz[3], hz[4], \
    hz[5], hz[6], hz[7], hz[8], hz[9], hz[10], hz[11]

scale = [c, csh, d, dsh, e, f, fsh, g, gsh, a, ash, b]

''' Entries in chords in order of scale. Length of list should match with alphabet.'''
chords = [[csh, e, a], [csh, dsh, b], [csh, e, fsh, ash], [f, a], [e, g, b], #abcde
       [c, f, a], [g, ash, b], [dsh, fsh, b], [c, e, a], [d, gsh], #fghij
       [dsh, ash], [dsh, a], [fsh, g, gsh, a], [f, fsh, g], [dsh, g, b], #klmno
       [csh, f, a], [c, d, fsh, a], [csh, g, ash], [e, gsh, b], [c, d, g], #pqrst
       [d, g, b], [d, dsh], [d, dsh, e, f], [ash], [b], #uvwxy
       [e, ash], [c, dsh, fsh, a], [csh, e, g, ash], [d, f, gsh, b], [f, b], #zäöüß
       [c], [csh], [d], [dsh], [e], #01234
       [f], [fsh], [g], [gsh], [a], #56789
       [e, b], [0], [c, e, g], [c, e, gsh], [c, d, f, g, a], #- .,;
       [c, d, e, fsh, gsh, ash], [csh, dsh, f, g, a, b]] #!?

if len(alphabet) > len(chords):
    print(str(len(alphabet) - len(chords)) + ' character(s) have no sound assigned.')
        
x = int(sr*dur)
start_end = np.full(int(x/2), 0)

def gen(f0, ampl):
    ''' Generates sine waves.
    Args:
        f0 (float): frequency of sine in Hertz.
        ampl(float): amplitude of sine.
    Returns:
        array of generated sine
    '''
    t = np.linspace(0, dur, x, endpoint=False)
    sig = ampl * np.sin(2 * np.pi * f0 * t)
    
    return sig


def letter_to_sound(letter):
    ''' Generates sound that matches with chord assigned to letter in alphabet.
        Chooses octave for single notes randomly within given boundaries.
        Adjusts amplitude of single sines to number of sines in chord.
    Args:
        letter (str): letter in message to encode.
    Returns:
        array of combined sines
    '''
    letter_index = alphabet.index(str(letter))
    sig = 0
    for letter in chords[letter_index]:
        freq = (letter * (2 ** random.randint(lowest_octave, highest_octave)))
        sig += gen(freq, ampl/len(chords[letter_index]))

    return sig
        
def encode(message):
    ''' Generates a stream of sounds that can be saved to a wav file.
        Each sound corresponds to a letter in the message.
    Args:
        message (str): message to be encoded to sounds.
    Returns:
        array of combined sines concatenated together to a single array
    '''
    message_encoded = start_end
    for letter in message.lower():
        if letter not in alphabet: 
            print('This character could not be encoded: ' + letter)
        else:
            sig = letter_to_sound(letter)
            message_encoded = np.concatenate((message_encoded, sig))
    message_encoded = np.concatenate((message_encoded, start_end))
    if show_chromagram_while_encoding == True:
        chroma = librosa.feature.chroma_stft(message_encoded, sr, n_fft= x, hop_length= x)
        librosa.display.specshow(chroma, x_axis='time', y_axis='chroma')
    if play_while_encoding == True:
        sd.play(message_encoded, sr)
    return message_encoded

'''Enter the message below. It will overwrite previous 'secret_message.wav's.'''
#message_encoded = encode('lorem ipsum')
#wavfile.write('secret_message.wav', sr, message_encoded)

'''Enter the wav file to decode.'''
#sr1, sig1 = wavfile.read('secret_message.wav')

if play_while_decoding == True:
    sd.play(sig1, sr1)

chroma = librosa.feature.chroma_stft(sig1, sr1, n_fft= x, hop_length= x)
if show_chromagram_while_decoding == True:
    librosa.display.specshow(chroma, x_axis='time', y_axis='chroma')
    
chroma_zipped = list(map(list, zip(*chroma)))

def sound_to_chord(column, value):
    ''' Reads chroma features of wavfile and returns them as a list of single notes.
    Args:
        column (int): horizontal index in chromagram
        value (float): between 0 and 1, threshold value of chroma feature, above 
                       which the note will be read as part of the chord.
    Returns:
        list of notes
    '''
    notes = []
    chroma_column = chroma_zipped[column]
    for i in chroma_column:
        if i >= value:
            note_index = chroma_column.index(i)
            notes.append(scale[note_index])
    return notes

def notes_to_letter(column):
    '''Searches for list of notes in 'chords' and matches it with letter in 'alphabet'
    Args:
        column (int): horizontal index in chromagram
    Returns:
        letter that matches with chord
    '''
    value = 0.4
    letter = ''
    if np.amax(chroma_zipped[column]) < 0.1:
        letter = alphabet[chords.index([0])]
    else:
        while value > 0.1:
            try: 
                notes = sound_to_chord(column, value)
                letter = alphabet[chords.index(notes)]
                break
            except ValueError:
                value = value-0.1
    return letter

decoded_message = ''
for i in np.arange(1, len(chroma_zipped) - 1):
    letter = notes_to_letter(i)
    decoded_message += letter
print(decoded_message)

