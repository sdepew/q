from bot.command_map import command_map


@command_map.register_command()
def flip(query=[], user=""):
    '''
    We all have those table flip moments.
    *Usge:*
    `!flip Something That Upsets You`
    '''
    output = "(╯°□°）╯︵ ┻━┻  "
    char_map = {
        'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ə',
        'f': 'ɟ', 'g': 'ɓ', 'h': 'ɥ', 'i': '!', 'j': 'ɾ',
        'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o',
        'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ',
        'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x', 'y': 'ʎ',
        'z': 'z', 'A': '∀', 'B': '𐐒', 'C': 'Ↄ', 'D': '◖',
        'E': 'Ǝ', 'F': 'Ⅎ', 'G': '⅁', 'H': 'H', 'I': 'I',
        'J': 'ſ', 'K': '⋊', 'L': '⅂', 'M': 'W', 'N': 'ᴎ',
        'O': 'O', 'P': 'Ԁ', 'Q': 'Ό', 'R': 'ᴚ', 'S': 'S',
        'T': '⊥', 'U': '∩', 'V': 'ᴧ', 'W': 'M', 'X': 'X',
        'Y': '⅄', 'Z': 'Z', '0': '0', '1': 'Ɩ', '2': 'ᄅ',
        '3': 'Ɛ', '4': 'ᔭ', '5': 'ϛ', '6': '9', '7': 'Ɫ',
        '8': '8', '9': '6', '_': '¯', "'": ',', ',': "'",
        '\\': '/', '/': '\\', '!': '¡', '?': '¿', '&': '⅋',
        '.': '˙', '‿': '⁀', '⁀': '‿'
    }
    user_input = " ".join(query)
    output += ''.join([char_map[c] if c in char_map else c for c in user_input[::-1]])
    return output
