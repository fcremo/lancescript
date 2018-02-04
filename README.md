# LanceScript

This is an implementation of LanceScript, a language with heavy similarities to the Lance toy language taught at the 
Formal Languages and Compilers course @ Politecnico di Milano.

I made this in a day during my exam session out of boredom, so don't be harsh :)

Code may be (almost certainly is) ugly, stupid, inefficient and won't work in obvious and/or subtle ways.

## How to run
This project requires python3. You'll also need to install `lark-parser`. Feel free to use a virtualenv if you whish.
```
pip3 install lark-parser
```

Then, executing `test.py` in the project root dir will execute all files in the `tests` directory.

## Acknowledgments
- The langage is inspired to Lance, taught at the FLC course of Politecnico di Milano. 
    - I want to thank my professors. It has been one of the most interesting courses I attended!
- Without `lark-parse` I wouldn't have been able to write this project in a week, let alone a single day. It's an awesome library!