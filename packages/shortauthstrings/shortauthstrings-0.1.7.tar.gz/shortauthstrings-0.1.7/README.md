# Short authentication strings for Python

This package implements rendering of short authenticated strings, which you
can use in your application after an unauthenticated exchange such as a
Diffie-Hellman process.

The usual way in which this works is, both sides of the exchange display
(hopefully) the same sequence based on the shared key (or a derivative of it),
indicating that the shared key is, in fact, shared and has not been tampered
with by an active man in the middle.

Here is a sample from a Python REPL:

```
>>> from shortauthstrings import emoji
>>> print(emoji(bytes([4,88,75,34,99,124])))
🍋 🍧 🍝 🌰 🍮 🦝
>>>
```

A ready-to-go module to perform Diffie-Hellman key agreement can be found in
the [blindecdh repository](https://github.com/Rudd-O/blindecdh).

See [module](https://github.com/Rudd-O/shortauthstrings/blob/master/src/shortauthstrings/__init__.py) for more documentation.

This package is distributed under the GNU Lesser General Public License v2.1.
For relicensing, contact the package author.
