import argparse
import re

DEBUG = False
TABSIZE = 4


def get_indent_level(line_of_code):
    match = re.match(r"^(\t*)", line_of_code)
    return len(match.group(1)) if match else 0


def check_mixed_indentation(lines):
    # TODO: Check for tabs / spaces depending on flag.
    for idx, line in enumerate(lines, 1):
        #if re.match(r"^ +", line):
        #    print(f"Warning: Line {idx} starts with spaces.")
        #elif
        if re.match(r"^ *\t", line):
            print(f"Warning: Line {idx} has mixed spaces and tabs.")


def parse_instr(line, cmt_char=";"):
    # type, indent_or_label, mnemonic, operands, comment
    indentation = len(line) - len(line.lstrip())
    s_line = line.strip()

    # constants
    for word in ["equ", "%assign", "%define", "section", "bits", "org", "global", "extern"]:
        if re.search(r"\b" + word + r"\b", s_line.lower()):
            code, _, cmt = s_line.partition(cmt_char)
            tokens = code.strip().split(None, maxsplit=1)
            if not tokens:
                return ["k", "", "", "", cmt.strip()]
            keyword = tokens[0]
            ops = tokens[1] if len(tokens) > 1 else ""
            return ["k", "", keyword, ops, cmt.strip()]

    # blank line
    if not s_line:
        return ["b", "", "", "", ""]

    # comment only
    if s_line.lstrip().startswith(cmt_char):
        print(f"Indent: {indentation}, Comment: {s_line[1:].strip()}")
        return ["c", indentation, "", "", s_line[1:].strip()]

    # label
    if re.match(r"^[\w.]+:$", s_line):
        return ["l", line, "", "", ""]

    code, _, cmt = s_line.partition(cmt_char)
    cmt = cmt.strip() if cmt else ""
    tokens = code.strip().split(None, 1)
    mnemonic = tokens[0] if tokens else ""
    ops = tokens[1] if len(tokens) > 1 else ""

    return ["i", "", mnemonic, ops, cmt]


def format_line(mnemonic, operands, cmt, col=40, indent=True, keyword=False):
    prefix = " " * TABSIZE if indent else ""

    if keyword:
        line = f"{prefix}{mnemonic:<20} {operands}".rstrip()
    else:
        line = f"{prefix}{mnemonic:<8} {operands}".rstrip()
    if DEBUG and not indent:
        print(f"Current line {line}")
    if cmt:
        visual_len = len(line)
        padding = max(1, col - visual_len)
        line += " " * padding + f"; {cmt}"
    return line


def align_file(file_path, output_path=None, cmt_char=";", col=40, tabsize=4):
    global TABSIZE
    TABSIZE = tabsize

    if file_path == output_path:
        user_choice = input(f"Do you want to overwrite: {file_path}? [Y/n] ")
        if user_choice.lower() not in ("y", ""):
            print("Skipping...")
            output_path = None

    with open(file_path, "r") as f:
        lines = f.read().splitlines()
        if DEBUG:
            check_mixed_indentation(lines)

    blank_line = 0
    result_lines = []
    macro_buf = []

    for line in lines:
        typ, indent_or_label, mnemonic, ops, cmt = parse_instr(line, cmt_char)

        line = line.rstrip()

        if typ == "b":
            blank_line += 1
            if blank_line <= 2:
                result_lines.append("")
            continue
        else:
            blank_line = 0

        if typ == "l":
            result_lines.append(indent_or_label)
        elif typ == "k":
            keyword_line = format_line(
                mnemonic, ops, cmt, col, indent=False, keyword=True
            )
            result_lines.append(keyword_line)
        elif typ == "c":
            #indent_level = indent_or_label
            #indent_spaces = min(indent_level, TABSIZE) * " "
            #cmt = cmt.lstrip()
            #comment_line = f"{indent_spaces}; {cmt}"
            #result_lines.append(comment_line)
            result_lines.append(cmt)
        elif typ == "i":
            instr = format_line(mnemonic, ops, cmt, col, indent=True, keyword=False)
            result_lines.append(instr)

    while result_lines and result_lines[-1].strip() == "":
        result_lines.pop()
    result_lines.append("")

    output = "\n".join(result_lines) + "\n"

    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
    else:
        if not DEBUG:
            print(output)


def main():
    parser = argparse.ArgumentParser(description="Basic ASM Linter")
    parser.add_argument("input", help="Input file")
    parser.add_argument(
        "-o", "--output", help="Output file (optional, default: stdout)"
    )
    parser.add_argument(
        "-c",
        "--col",
        type=int,
        default=40,
        help="Column to align comments to (default: 40)",
    )
    parser.add_argument(
        "-m", "--comment-char", default=";", help="Comment character (default: ;)"
    )
    parser.add_argument("-t", "--tabsize", type=int, default=4, help="Tab size (default: 4)")

    args = parser.parse_args()

    align_file(args.input, args.output, args.comment_char, args.col, args.tabsize)


if __name__ == "__main__":
    main()

