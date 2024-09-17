import sys
import os

def sort_key(line: str) -> str:
    return ' '.join(sub for sub in line.split() if not sub.endswith(('%', ':')))

def percentage_val(line: str) -> float:
    return next(float(word[:-1]) for word in line.split() if word.endswith('%'))

def assign_rank(lines: list[str], line: str) -> int:
    assert all(l.endswith(' opps') for l in lines)
    similar_lines = [l for l in lines if l.split()[-2] == line.split()[-2]]
    similar_lines.sort(key=lambda l: percentage_val(l), reverse=True)
    return similar_lines.index(line) + 1

def main() -> None:
    folder_name = sys.argv[1]
    lines: list[str] = []
    output_filename = 'combined.txt'
    for file in os.listdir(os.fsencode(folder_name)):
        filename = os.fsdecode(file)
        if filename == output_filename:
            raise FileExistsError(f"Already a `{output_filename}` file in the {folder_name} folder")
        with open(f"{folder_name}/{filename}", 'r') as f:
            lines.extend(line.rstrip() for line in f)
    lines.sort(key=sort_key)
    lines = [' '.join(line.split()[1:]) for line in lines]
    lines = [f"#{assign_rank(lines, line)}: {line}" for line in lines]
    with open(f"{folder_name}/{output_filename}", 'w') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == '__main__':
    main()