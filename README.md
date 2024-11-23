# _pcatch_ (Pattern Catcher)
# Video Demo: https://youtu.be/YUnIjrNXx_o
# Description:
`pcatch` or `pcat`, short for Pattern Catcher, is a CLI tool that is an immitation of [`ripgrep`](https://github.com/BurntSushi/ripgrep) (a poor one admittingly). It searches for a pattern in files.
## Why did I make this?
Because I love CLI tools.
## How does it work?
- It takes a pattern, optional path(s) and other options and then uses [`argparse`](https://docs.python.org/3/library/argparse.html) to parse them.
- It uses memory mapping ([`mmap`](https://docs.python.org/3/library/mmap.html)) to open files which helps make the process faster in case of large files
- It uses regex ([`re`](https://docs.python.org/3/library/re.html#)) to search for matching patterns in files and then print them.

## Usage:
```
usage: python project.py [-h] [-w] [-i] PATTERN [PATH ...]

Checks for given pattern in files

positional arguments:
  PATTERN            Pattern to search for in file(s)
  PATH               Files(s) to search for. If no value is given, it will search the curreny working directory (non-recursively)

options:
  -h, --help         show this help message and exit
  -w, --word         Search pattern as word
  -i, --ignore-case  Search case-insensitively
```
### How to use (step-by-step):
1. Clone the repo:
   ```
    git clone https://github.com/NextStep-IM/pcatch.git
   ```
2. Enter the repo:
   ```
    cd pcatch
   ```
3. Run the program:
   ```
    python pcatch.py <PATTERN> <FILE>
   ```
   You can give multiple files as input. The PATTERN can be a simple string or a regex pattern. You can use wildcards in place of FILES.
   
   Example command (to be run in the `pcatch` directory):
   ```
    python pcatch.py "parse" "*"
   ```

## Features:
- User can search case-insensitively and by word
- The inputted pattern can be a regex
- Allows multiple files or directories
- Allows wildcards in paths
- Gives colored output
## Discussion:
### Why are lines sliced if they exceed certain length?
> [!NOTE]
> Need an algorithm to decide how much of a line is sliced.

That is because when I was not filtering binary file, I came upon files with _very_ long lines during pattern search. Now binary files are filtered but the code will still be there just in case longer lines are encountered. The length is `768` because that's the approximate amount of bytes four lines have on my 1920x1080 monitor :).
### Binary files:
After madly searching the internet for a way to skip binary files (in Python), I came upon [`binaryornot`](https://pypi.org/project/binaryornot/). It used several code snippets found around the internet to check for binary files. I only found out that it was hogging most of the runtime by using [`cProfile`](https://docs.python.org/3/library/profile.html#module-cProfile). It took 50s more if I was searching this path: `/opt/**/*`. So I got rid of it and just used a list of binary file extensions to filter the paths, which is faster.
### Runtime:
It's currently fast because it skips all the non-text files but I feel like it could be faster with or without skipping the files.
### `mmap` and `byte` strings:
Memory-mapped files work with [`byte` strings](https://realpython.com/python-strings/#bytes-objects) and this caused a little bit of a problem. My color codes were normal strings and concatenating them with matched patterns (which were `bytes` objects) was not possible and my user-given pattern was also a `byte` string. I used `decode()` (See: https://docs.python.org/3/howto/unicode.html) to handle this. Now my reason for removing them is a little weak. I saw in my `cProfile.run()` data that `feed` from `universaldetector.py` was taking a lot of time so I researched it. It was related to encoding/decoding so I thought removing them might reduce runtime. If it did, it didn't reduce much.
### `UnicodeDecodeError`:
I am pretty sure it was because of a binary file. Using `latin-1` as a param for `decode()` for fixed the error so I assume the file was encoded in `latin-1`(?). 
### Reading Epub/Mobu/Pdf:
[`pymupdf`](https://pymupdf.readthedocs.io/en/latest/index.html) allows opening pdf/mobi/epub but I didn't implement this feature because I thought it might be useless if it isn't accompanied by a gui and other useful info (like page number). 
