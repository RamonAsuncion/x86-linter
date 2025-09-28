import argparse
import re

DEBUG = False
TABSIZE = 4

def check_mixed_indentation(lines):
    # TODO: Check for tabs / spaces depending on flag.
    for idx, line in enumerate(lines, 1):
        #if re.match(r"^ +", line):
        #    print(f"Warning: Line {idx} starts with spaces.")
        #elif
        if re.match(r"^ *\t", line):
            print(f"Warning: Line {idx} has mixed spaces and tabs.")


def parse_instr(line, cmt_char=";"):
    """ Parse one line of assembly into tuple

    Returns:
        type: b=blank, c=comment, l=label, k=keyword, i=instruction
    """
    raw = line.rstrip("\n")
    s_line = raw.strip()

    # blank line
    if not s_line:
        return ("b", "", "", "", "")

    # comment only
    if s_line.startswith(cmt_char):
        if DEBUG: print(f"Indent: {indentation}, Comment: {s_line[1:].strip()}")
        return ("c", "", "", "", s_line.lstrip(cmt_char).strip())

    code, _, cmt = s_line.partition(cmt_char)
    cmt = cmt.strip()

    # label (ends with :)
    if ":" in code:
        label_part, after_label = code.split(":", 1)
        label = label_part.strip()
        rest = after_label.strip()
        if DEBUG:
            print("label:", label)
        if rest:
            tokens = rest.split(None, 1)
            mnem = tokens[0].lower()
            ops = tokens[1] if len(tokens) > 1 else ""
            return ("i", label, mnem, ops, cmt)
        else:
            return ("l", label, "", "", cmt)

    tokens = code.strip().split(None, 1)
    if not tokens:
        return ("b", "", "", "", cmt)

    first = tokens[0].lower()
    rest = tokens[1] if len(tokens) > 1 else ""

    if first in ("equ", "%assign", "%define", "section", "bits", "org", "global", "extern"):
        return ("k", "", first, rest, cmt)

    return ("i", "", first, rest, cmt)

def compute_width(parsed):
    label_width = 0
    mnemonic_width = 0
    ops_width = 0

    for t, label, mnem, ops, _ in parsed:
        if label:
            label_width = max(label_width, len(label))
        if mnem:
            mnemonic_width = max(mnemonic_width, len(mnem))
        if ops:
            ops_width = max(ops_width, len(ops))

    return {
        "label": label_width,
        "mnemonic": mnemonic_width,
        "ops": ops_width,
    }

def align_file(file_path, output_path=None, cmt_char=";", col=40, gap=2):
    if file_path == output_path:
        user_choice = input(f"Do you want to overwrite: {file_path}? [Y/n] ")
        if user_choice.lower() not in ("y", ""):
            print("Skipping...")
            output_path = None

    with open(file_path, "r") as f:
        lines = f.read().splitlines()
        if DEBUG:
            check_mixed_indentation(lines)

    parsed = [parse_instr(line, cmt_char) for line in lines]
    widths = compute_width(parsed)
    if DEBUG:
        print("Gap: ", widths["label"] + gap)
    indent = " " * (widths["label"] + gap + 1) # + 1 for colon

    if DEBUG:
        print("Label length", widths["label"])
        print("Mnemonic length", widths["mnemonic"])
        print("Ops length", widths["ops"])

    out_lines = []
    for t, label, mnem, ops, cmt in parsed:
        if t == "b":
            line = ""
        elif t == "c":
            line = f"{cmt_char} {cmt}"
        elif t == "l":
            line = f"{label}:"
        elif t in ("i", "k"):
            parts = []
            if label:
                parts.append(f"{label}:".ljust(len(indent)))
            else:
                parts.append(indent)

            parts.append(mnem.ljust(widths["mnemonic"]))
            if DEBUG:
                print(f"Part 1: {len(parts[0])}\nPart 2: {len(parts[1])}")
                print(parts)
            if ops:
                parts.append(" " * gap + ops)

            line = "".join(parts)
        else:
            line = ""


        if cmt and t not in ("c", "b"):
            width = abs(len(line) - col) + 1
            if DEBUG:
                print(f"Width: {width}")
            line += (" " * width) + f"{cmt_char} {cmt}"

        out_lines.append(line)

    output = "\n".join(out_lines) + "\n"

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
    parser.add_argument("-g", "--gapsize", type=int, default=2, help="Spaces between columns (default: 2)")

    args = parser.parse_args()

    align_file(args.input, args.output, args.comment_char, args.col, args.gapsize)


if __name__ == "__main__":
    main()

