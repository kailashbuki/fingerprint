#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates fingerprints of text document.
"""
import string
import sys

__author__ = 'kailash.buki@gmail.com (Kailash Budhathoki)'
__all__ = [
    'Fingerprint',
    'FingerprintException',
]

guid = lambda x: ord(x)


class FingerprintException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Fingerprint(object):
    """
    Generates fingerprints of the input text file or plain string. Please consider taking a look at http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf for detailed description on how fingerprints are computed.

    Attributes:
        kgram_len (Optional[int]): length of the contiguous substring. Defaults to 50.
        base (Optional[int]): base required for computing the rolling hash function. Defaults to 101.
        modulo (Optional[int]): hash values cannot exceed this value. Defaults to sys.maxint.
        window_len (Optional[len]): length of the windows when computing fingerprints. Defaults to 100.
        kgrams (List(str)): k-grams extracted from the text
        hashes (List(int)): hash values of the k-grams
        fingerprints (List(tuple(int))): selected representative hash values along with their positions.
    """

    def __init__(self, kgram_len=None, base=None, modulo=None, window_len=None):
        self.kgram_len = kgram_len or 50
        self.base = base or 101
        self.modulo = modulo or sys.maxsize
        self.window_len = window_len or 100

    def get_min_with_pos(self, sequence):
        min_val = sys.maxsize
        min_pos = 0
        for pos, val in enumerate(sequence):
            if val <= min_val:
                min_val = val
                min_pos = pos
        return min_val, min_pos

    def normal_hash(self, kgram):
        hash = 0
        for i, c in enumerate(kgram):
            hash += guid(c) * self.base ** (self.kgram_len - 1 - i)
        hash = hash % self.modulo
        return hash

    def rolling_hash(self, old_hash, del_char, new_char):
        # more powerful version of rolling hash
        hash = ((old_hash - guid(del_char) * self.base **
                 self.kgram_len) + guid(new_char)) * self.base
        hash = hash % self.modulo
        return hash

    def prepare_storage(self):
        self.kgrams = []
        self.hashes = []
        self.fingerprints = []
        self.str = ""

    def generate_kgrams(self):
        self.kgrams = [self.str[i:i + self.kgram_len]
                       for i in range(len(self.str) - self.kgram_len + 1)]

    def hash_kgrams(self):
        prev_kgram = self.kgrams[0]
        prev_hash = self.normal_hash(prev_kgram)
        self.hashes.append(prev_hash)

        for cur_kgram in self.kgrams[1:]:
            prev_hash = self.rolling_hash(
                prev_hash, prev_kgram[0], cur_kgram[-1])
            self.hashes.append(prev_hash)
            prev_kgram = cur_kgram

    def generate_fingerprints(self):
        windows = [self.hashes[i:i + self.window_len]
                   for i in range(len(self.hashes) - self.window_len + 1)]

        cur_min_hash, cur_min_pos = self.get_min_with_pos(windows[0])
        self.fingerprints.append((cur_min_hash, cur_min_pos))

        for i, window in enumerate(windows[1:]):
            min_hash, min_pos = self.get_min_with_pos(window)
            min_pos += i + 1
            if min_hash != cur_min_hash or min_hash == cur_min_hash and min_pos > cur_min_pos:
                cur_min_hash, cur_min_pos = min_hash, min_pos
                self.fingerprints.append((min_hash, min_pos))

    def validate_config(self):
        if len(self.str) < self.window_len:
            raise FingerprintException(
                "Length of the string is smaller than the length of the window.")

    def sanitize(self, str):
        sanitized = ""
        exclude = string.punctuation
        for c in str:
            if c not in exclude and c not in ('\n', '\r', ' '):
                sanitized += c
        return sanitized

    def generate(self, str=None, fpath=None):
        """generates fingerprints of the input. Either provide `str` to compute fingerprint directly from your string or `fpath` to compute fingerprint from the text of the file. Make sure to have your text decoded in `utf-8` format if you pass the input string.

        Args:
            str (Optional(str)): string whose fingerprint is to be computed.
            fpath (Optional(str)): absolute path of the text file whose fingerprint is to be computed.

        Returns:
            List(int): fingerprints of the input.

        Raises:
            FingerprintException: If the input string do not meet the requirements of parameters provided for fingerprinting.
        """
        self.prepare_storage()
        self.str = self.load_file(fpath) if fpath else self.sanitize(str)
        self.validate_config()
        self.generate_kgrams()
        self.hash_kgrams()
        self.generate_fingerprints()
        return self.fingerprints

    def load_file(self, fpath):
        with open(fpath, 'r') as fp:
            data = fp.read()
        data = data.encode().decode('utf-8')
        return data


if __name__ == "__main__":
    f = Fingerprint(kgram_len=4, window_len=5, base=10, modulo=1000)
    print(f.generate(str="adorunrunrunadorunrun"))
    print(f.generate(fpath="../CHANGES.txt"))
