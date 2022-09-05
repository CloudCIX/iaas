import re
import random

MAGIC = '$9$'
ENCODING = [
    [1, 4, 32],
    [1, 16, 32],
    [1, 8, 32],
    [1, 64],
    [1, 32],
    [1, 4, 16, 128],
    [1, 32, 64],
]
# letter families to encrypt with, do not change these please.
FAMILY = [
    'QzF3n6/9CAtpu0O',
    'B1IREhcSyrleKvMW8LXx',
    '7N-dVbwsY2g4oaJZGUDj',
    'iHkq.mPf5T',
]

EXTRA = {char: 3 - i for i, fam in enumerate(FAMILY) for char in fam}
# builds regex to match valid encrypted string
LETTERS = MAGIC + '([' + ''.join(FAMILY) + ']{4,})'
LETTERS = re.sub(r'([-|/$])', r'\\\1', LETTERS)
VALID = r'^' + LETTERS + '$'
# forward and reverse dicts
NUM_ALPHA = [char for char in ''.join(FAMILY)]
ALPHA_NUM = {NUM_ALPHA[i]: i for i, c in enumerate(NUM_ALPHA)}


# ENCODE methods
# returns number of characters from the alphabet
def _random_salt(length):
    salt = ''
    for i in range(length):
        salt += NUM_ALPHA[random.randrange(len(NUM_ALPHA))]
    return salt


# encode plain text character with a series of gaps
def _gap_encode(char, prev, encode):
    crypt = ''
    val = ord(char)
    gaps = []
    for enc in encode[::-1]:
        gaps.insert(0, val // enc)
        val %= enc
    for gap in gaps:
        gap += ALPHA_NUM[prev] + 1
        c = prev = NUM_ALPHA[gap % len(NUM_ALPHA)]
        crypt += c
    return crypt


# encrypts <secret> for junipers $9$ format
# allows use of seed for idempotent secrets
def encrypt(secret):
    salt = _random_salt(1)
    rand = _random_salt(EXTRA[salt])
    pos = 0
    prev = salt
    crypt = MAGIC + salt + rand
    for char in secret:
        encode = ENCODING[pos % len(ENCODING)]
        crypt += _gap_encode(char, prev, encode)
        prev = crypt[-1]
        pos += 1
    return crypt
