# Fingerprint -- Document Fingerprint Generator

## Fingerprint of a document
Fingerprint is a signature of the document. In particular, it is a representative subset of hash values from the set of all hash values of a document. For more detail, please consider taking a look at [Winnowing: Local Algorithms for Document Fingerprinting](http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf) *(specifically Figure 2)*.

## Super simple to use
Fingerprint is very simple to use.
```python
f = Fingerprint(kgram_len=4, window_len=5, base=10, modulo=1000)
print f.generate(str="adorunrunrunadorunrun")
print f.generate(fpath="/Users/test/docs/CHANGES.txt")
```
The default values for the parameters are
```python
kgram_len = 50
window_len = 100
base = 101
modulo = sys.maxint
```

## Install
```sh
pip install fingerprint
```

