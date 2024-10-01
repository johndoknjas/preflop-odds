"""Given two sim results files, output info about discrepancies between lines."""

from __future__ import annotations
import sys
import Utils

def readlines(file: str) -> list[str]:
    with open(file, 'r') as f:
        return [line.strip() for line in f]

def get_components(line: str) -> tuple[str, float]:
    equity_percentage = next(float(x[:-1]) for x in line.split() if x.endswith('%'))
    text = ' '.join(x for x in line.split() if '#' not in x and '%' not in x)
    return (text, equity_percentage)

def main() -> None:
    Utils.pypy_notice()
    shorter, longer = sorted((readlines(sys.argv[1]), readlines(sys.argv[2])), key=len)
    missing_lines: list[tuple[str, float]] = []
    equity_percent_diffs: list[tuple[str, float]] = []
    for line in longer:
        components = get_components(line)
        other = next((t for x in shorter if (t := get_components(x))[0] == components[0]), None)
        if other is None:
            missing_lines.append(components)
            continue
        equity_percent_diffs.append((components[0], abs(components[1] - other[1])))
    equity_percent_diffs.sort(key=lambda d: d[1])
    print("\nChanges in equity percentage in sorted order:")
    for diff in equity_percent_diffs:
        print(f"{diff[0].split()[0]} has a change in equity percentage of {diff[1]}%")
    print(f"\nNum missing lines in the longer file but not the shorter: {len(missing_lines)}")
    print('\n'.join(str(t) for t in missing_lines))
    print(f'Average change in equity percentage: ' +
          f'{sum(j for _, j in equity_percent_diffs) / len(equity_percent_diffs)}%')


if __name__ == '__main__':
    main()