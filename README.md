# Musikencoder

This program takes a string and converts it to sine waves saved to 'secret_message.wav'.
To create a new 'secret_message.wav', uncomment lines 118 and 119 and run the code with 
your string replacing 'lorem ipsum' in line 118.

To decode a 'secret_message.wav', comment those lines again and uncomment line 122.

This works by chroma anaylsis. So while each letter is represented by specfic tone
combinations, their octaves can be randomised so that the same letter always sounds
somewhat different.
