from typing import *
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass, field
import sys
import re

def main(argv: list[str]=sys.argv) -> Optional[int]:
    prog = argv[0]
    args = argv[1:]
    description = (
        'Analyzes standard library usage in C++ source code'
     ' - Does not analyze compilation, just appearance in code'
    )

    parser = ArgumentParser(prog=prog, description=description)
    parser.add_argument('paths', type=Path, nargs='*', default=[Path.cwd()])
    parsed_args = parser.parse_args(args)

    print("Loading sources")
    srcs = find_src_files(parsed_args.paths)

    if len(srcs) <= 0:
        print('No sources found!')
        return 2

    print("Analyzing...")
    results = parse(srcs)

    if len(results.includes) <= 0 and len(results.symbols) <= 0:
        print('No usages found')
        return 0

    print('~~~~ Results ~~~~')
    print()
    print_results(results)

def find_src_files(paths: list[Path]) -> list[Path]:
    files = [ path for path in paths if path.is_file() ]
    dirs = [ path for path in paths if path.is_dir() ]

    srcs = [ file for file in files if is_src_file(file) ]
    for dir in dirs:
        srcs.extend(find_src_files(list(dir.iterdir())))

    return srcs

# Could check for an error: i.e. including a header but not using it
#   or relying on a dependent include
# Probably too much work
@dataclass
class Results:
    includes: dict[str, int] = field(default_factory=lambda: {})
    symbols:  dict[str, int] = field(default_factory=lambda: {})

def parse(srcs: list[Path]) -> Results:
    results = Results()
    for src in srcs:
        lines = read_file_lines(src)
        multi_line_comment = False
        for line in map(lambda l: l.strip(), filter(lambda l: len(l) >= 2, lines)):
            uncommented_bits: list[str] = ['']
            single_line_comment = False

            for i, char in enumerate(line.strip()):
                this_token = line[i : i+2] if i < len(line) - 1 else None
                prev_token = line[i-1 : i+1] if i > 0 else None

                if multi_line_comment:
                    if this_token is not None:
                        if len(line) == 2:
                            if this_token == '*/':
                                multi_line_comment = False
                                break
                        elif prev_token == '*/':
                            multi_line_comment = False
                            uncommented_bits.append('')
                elif not single_line_comment:
                    # Not already in a comment
                    match this_token:
                        case '/*': multi_line_comment = True
                        case '//': single_line_comment = True
                        case _: uncommented_bits[-1] += char

            for s in uncommented_bits:
                includes = find_includes(s)
                for include in includes:
                    if include not in results.includes:
                        results.includes[include] = 1
                    else:
                        results.includes[include] += 1
                symbols = find_symbols(s)
                for symbol in symbols:
                    if symbol not in results.symbols:
                        results.symbols[symbol] = 1
                    else:
                        results.symbols[symbol] += 1
    return results

INCLUDE_PATTERN = re.compile(r'(#include <)(\w*)(>)', re.ASCII)

def find_includes(line: str) -> list[str]:
    return [ match.group(2) for match in INCLUDE_PATTERN.finditer(line) ]

SYMBOL_PATTERN = re.compile(r'(std::)([^ \n(<>&\*;]*)(.)', re.ASCII | re.DOTALL)

def find_symbols(line: str) -> list[str]:
    return [ match.group(2) for match in SYMBOL_PATTERN.finditer(line) ]

def print_results(results: Results):
    print('Includes:')
    includes = reversed(sorted(
        sorted(list(results.includes.keys()), reverse=True),
        key=lambda h: results.includes[h]
    ))
    for rank, header in enumerate(includes, 1):
        count = results.includes[header]
        print(f'{rank}. {header} ({count})')

    print()

    print('Symbols used:')
    symbols = reversed(sorted(
        sorted(list(results.symbols.keys()), reverse=True),
        key=lambda s: results.symbols[s]
    ))
    for rank, symbol in enumerate(symbols, 1):
        count = results.symbols[symbol]
        print(f'{rank}. {symbol} ({count})')

CPP_SRC_EXTENSIONS = {
    '.cpp', '.cc', '.cxx', '.c++',
    '.hpp', '.hh', '.hxx', '.h++',
    '.h',
    '.tpp'
}

def is_src_file(filename: Path) -> bool:
    return filename.suffix in CPP_SRC_EXTENSIONS

CPP_STD_HEADERS = {
    'string', 'string_view',
    'vector', 'deque', 'queue',
    'span',
    'unordered_map', 'map',
    'algorithm',
    'memory', 'utility', 'tuple',
    'thread', 'mutex', 'atomic',
    'fstream', 'sstream', 'iostream', 'iomanip',
    'functional', 'optional', 'variant',
    'filesystem',
    'chrono', 'ratio',
    'random',
    'concepts', 'type_traits',
    'charconv',
    'compare',
    'source_location',
    'initializer_list',
    'locale',

    'cstdlib', 'cstdio',
    'cstdint', 'cstddef', 'cctype'
}

def is_cpp_header(s: str) -> bool:
    return s in CPP_STD_HEADERS

def read_file_lines(filename: Path) -> list[str]:
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except (OSError, IOError):
        return []

if __name__ == '__main__':
    sys.exit()
