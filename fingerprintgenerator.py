#!/usr/bin/env python 
# Copyright (c) 2011 <Kailash Budhathoki>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED,INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Generates the fingerprints from a text file or directly from a standard
string. Winnowing-local algorithms for document fingerprinting is implemented
to calculate the fingerprints. Fingerprint generation is carried out in the
three phases;
[1st phase]: generates the k-grams from the standard string
[2nd phase]: generates the hash values for each k-gram using rolling hash function
[3rd phase]: generates the fingerprints from the hash values using winnowing

For more details on winnowing-local algorithms for document fingerprinting,
make yourself comfortable at
> http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf
"""

"""GLOBALS"""
KLENGTH = 50     # length of each kgram
BASE = 101       # base for rolling hash generation
DIVISOR = 2**32  # divisor for rolling hash generation
WINDOWSIZE = 100 # window size for winnowing 

class CircularList(list):
    
    """A list that wraps around instead of throwing an index error. Code snippet
    copied from http://snippets.dzone.com/posts/show/10279
    """

    def __getitem__(self, key):
        # try normal list behavior
        try:
            return super(CircularList, self).__getitem__(key)
        except IndexError:
            pass
        # key can be either integer or slice object,
        # only implementing int now.
        try:
            index = int(key)
            index = index % self.__len__()
            return super(CircularList, self).__getitem__(index)
        except ValueError:
            raise TypeError


class FingerprintGenerator:
    
    """ An action class whose instance is used for creating fingeprints of string
    """
    
    def __init__(self, input_string=None):
        """ member variables initializer"""
        self.text = input_string
        self.kgrams = []
        self.hash_values = []
        self.hash_windows = []
        self.fingerprints = []
        self.index = 0
        self.prev_hash_pos_local = 0
        self.prev_hash_pos_global = 0
        self.circular_list = []

    def generate_kgrams(self):
        """Generates the kgrams from the given string
        """
        totalChars = len(self.text)
        frontCount = 1
        for i in xrange(0, totalChars):
            if (i+KLENGTH)>len(self.text):
                kgram = self.text[i:]+self.text[:frontCount]
                frontCount += 1
            else:
                kgram = self.text[i:i+KLENGTH]
            self.kgrams.append(kgram)
        
    def generate_rollinghash(self):
        """Generates the hash values for each kgram using Karp-Rabin rolling
        hash function
        """
        first_kgram= self.kgrams[0]
        prev_hash_value = 0
        for i in xrange(0, KLENGTH):
            prev_hash_value += ord(first_kgram[i])*(BASE**(KLENGTH-1-i))
        
        prev_hash_value *= BASE
        self.hash_values.append(prev_hash_value%DIVISOR)
        prev_hash_value = prev_hash_value%DIVISOR
        for i in xrange(0, len(self.kgrams)-1):
            # Improvement on Rolling Hash | Each character potentially affect all of the hash's bit
            new_hash_value = ((prev_hash_value-ord(self.text[i])*BASE**(KLENGTH))+\
                            ord(self.kgrams[(i+KLENGTH)%self.kgrams.__len__()][0]))*BASE
            prev_hash_value = new_hash_value
            prev_hash_value = prev_hash_value%DIVISOR
            self.hash_values.append(new_hash_value%DIVISOR)
            
    def next_hash(self):
        """Provides the next hash value from a circular hash list for winnowing
        """
        try:
            next_hash = self.circular_list[self.index]
        except Exception:
            print 'index value=', self.index
            exit(1)
        self.index += 1
        return next_hash
    
    def record_global_pos(self, min_hash, min_hash_pos):
        """Records the global position of a fingerprint from its local position within the window              
        """
        if self.prev_hash_pos_local<min_hash_pos:
            temp_pos = min_hash_pos-self.prev_hash_pos_local
        else:
            modified_new_pos = WINDOWSIZE+min_hash_pos
            temp_pos = modified_new_pos-self.prev_hash_pos_local
        new_hash_pos_global = temp_pos+self.prev_hash_pos_global
        self.fingerprints.append([min_hash, new_hash_pos_global])
        self.prev_hash_pos_global = new_hash_pos_global
        self.prev_hash_pos_local = min_hash_pos
        
    def winnow(self):
        """Carries winnowing operation to produce fingerprints from the hash values
        """
        self.circular_list = CircularList(self.hash_values)
        
        h = [] 
        for i in xrange(0, WINDOWSIZE):
            h.append(self.next_hash())
        r = WINDOWSIZE-1                   # window right end
        min_hash_pos = WINDOWSIZE-1        # index of minimum hash
        
        for i in xrange(0, len(self.hash_values)-WINDOWSIZE+1):
            if min_hash_pos==r:
                # The previous minimum is no longer in this window 
                # Scan h leftward starting from r for the rightmost minimal hash
                min_hash = min(h)
                min_hash_pos = h.index(min_hash)
                self.record_global_pos(min_hash, min_hash_pos)
            else:
                # Otherwise the previous minimum is still in this window 
                # Compare against the new value and update min if necessary
                if h[r] <= min_hash:
                    min_hash_pos = r
                    min_hash = h[r]
                    self.record_global_pos(min_hash, min_hash_pos)
            r = (r+1)%WINDOWSIZE   # shift the window by one
            h[r] = self.next_hash()
            
    def generate_fingerprints(self):
        """mediator method for managing the order of the entire fingerprint
        generation process 
        """
        self.generate_kgrams()
        self.generate_rollinghash()
        self.winnow()


def file_content_refiner(filepath):
    """reads a file and sanitizes the string. removes newline, carriage return
    """
    f = open(filepath, 'r')
    content = f.read()
    refined_content = "".join([c for c in content if c not in('\n', '\r' ,' ')])
    refined_content = refined_content.lower()
    return refined_content

def main():
    s = """This is a sample text to demonstrate the fingerprint generation process.
    Only sanitized string is passed to the generator class but for real tasks,
    one can use file_content_reader method to read the content of the file and
    return the sanitized standard string. I am hoping to receive feedbacks from
    you. Thanking you -- ka!lashbuk!
    """
    
    fpg = FingerprintGenerator(input_string=s)
    fpg.generate_fingerprints()
    
    print '........................Fingerprints of text........................'
    print fpg.fingerprints
    print '...................................................................\n'
    
    """small test from sigmod3. change the WINDOWSIZE to 5"""
    f = FingerprintGenerator()
    f.hash_values = [77, 74, 42, 17, 98, 50, 17, 98, 8, 88, 67, 39, 77, 74, \
                       42, 17, 98]
    f.winnow()
    print '...................Fingerprints of test hash values.................'
    print f.fingerprints
    print '....................................................................'

if __name__ == '__main__':
    main()
