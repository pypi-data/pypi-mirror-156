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
    print(parsed_args.paths)

    srcs = find_src_files(parsed_args.paths)

    results = analyze(srcs)

    if len(results.includes) <= 0 and len(results.symbols) <= 0:
        print('No usages found')

@dataclass
class Results:
    includes: dict[str] = field(default_factory=lambda: {})
    symbols:  dict[str] = field(default_factory=lambda: {})

def analyze(srcs: list[Path]) -> Results:
    results = Results()
    for src in srcs:
        lines = read_file_lines(src)
        multi_line_comment = False
        for line in lines:
            uncommented_bits: list[str] = ['']
            single_line_comment = False
            for i, char in enumerate(line.strip()):
                this_token = line[i : i+2] if i < len(line) - 1 else None
                prev_token = line[i-1 : i+1] if i > 0 else None

                if multi_line_comment:
                    if i > 0 and prev_token == '*/':
                        multi_line_comment = False
                        uncommented_bits.append('')
                elif not single_line_comment:
                    # Not already in a comment
                    match this_token:
                        case '/*': multi_line_comment = True
                        case '//': single_line_comment = True
                        case _: uncommented_bits[:-1] += char

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
                        results.symbols[symbol] = 0
                    else:
                        results.symbols[symbol] += 1
    return results

INCLUDE_PATTERN = re.compile('#include <>')

def find_includes(line: str) -> list[str]:
    for match in re.finditer(INCLUDE_PATTERN, line):
        return []

SYMBOL_PATTERN = re.compile('std::')

def find_symbols(line: str) -> list[str]:
    for match in re.finditer(SYMBOL_PATTERN, line):
        return []

def find_src_files(paths: list[Path]) -> list[Path]:
    files = [ path for path in paths if path.is_file() ]
    dirs = [ path for path in paths if path.is_dir() ]
    srcs = [
        file for file in files if is_src_file(file)
    ] + [
        find_src_files(list(dir.iterdir())) for dir in dirs
    ]
    return srcs

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
    'fstream', 'sstream',
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
