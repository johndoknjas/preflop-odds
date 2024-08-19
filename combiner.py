import sys
import os

def sort_key(line: str) -> str:
    return ' '.join(sub for sub in line.split() if not sub.endswith(('%', ':')))

def main():
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
    with open(f"{folder_name}/{output_filename}", 'w') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == '__main__':
    main()