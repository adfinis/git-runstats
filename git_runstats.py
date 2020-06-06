import os
import re
import shutil
import signal
import sys
import time
from subprocess import PIPE, CalledProcessError, Popen, check_call

import click

cmd = (
    "git log --ignore-blank-lines --ignore-all-space " "--no-merges --shortstat"
).split(" ") + ["--pretty=tformat:next: %aN\u25CF%ai",]

stats_line = re.compile(
    r"(\d+)\s*files? changed,\s*(\d+)\s*insertions?\(\+\)"
    r"(,\s*(\d+)\s*deletions?\(\-\))?"
)

_running = True


class EndOfFile(Exception):
    pass


def exit_handler(signum, frame):
    global _running
    _running = False


signal.signal(signal.SIGINT, exit_handler)


class Stats:
    __slots__ = ("author", "files", "insertions", "deletetions", "sum")

    def __init__(self, author):
        self.author = author
        self.files = 0
        self.insertions = 0
        self.deletetions = 0
        self.sum = 0

    def __repr__(self):
        return f"{self.sum:10}  {self.author}"


def readline(stream):
    if not (line := stream.readline()):
        raise EndOfFile()
    return line.strip().decode("UTF-8")


def write(string):
    sys.stdout.write(string)


def flush():
    sys.stdout.flush()


def update_from_match(stats, match):
    files, insertions, _, deletetions = match.groups("0")
    files = int(files)
    insertions = int(insertions)
    deletetions = int(deletetions)
    stats.files += files
    stats.insertions += insertions
    stats.deletetions += deletetions
    stats.sum += insertions + deletetions


def process(stream, stats):
    while (line := readline(stream)) is not None:
        if line.startswith("next: "):
            _, _, author = line.partition("next: ")
            author, date = author.split("\u25CF")
            author = " ".join([x for x in author.split(" ") if x])
        elif match := stats_line.match(line):
            current = stats.get(author)
            if current is None:
                current = Stats(author)
                stats[author] = current
            update_from_match(current, match)
            break
    return date


def output(stats, commits, date, max=None):
    rows = sorted(stats.items(), key=lambda x: x[1].sum, reverse=True)
    if max is not None:
        rows = rows[:max]
    for item in rows:
        print(item[1])
    print(f"\n{commits:10}  commits ({date})")


def term_output(stats, commits, date, max):
    rows = sorted(stats.items(), key=lambda x: x[1].sum, reverse=True)[:max]
    for item in rows:
        write("\033[K")  # clear line
        print(item[1])
    write("\033[K\n\033[K")  # clear two lines
    write(f"{commits:10} commits ({date})")
    flush()


def display(stamp, stats, commits, date):
    new = time.monotonic()
    if new - stamp > 0.2:
        size = shutil.get_terminal_size((80, 20))
        lines = min(25, size.lines - 2)
        write("\033[0;0f")  # move to position 0, 0
        term_output(stats, commits, date, lines)
        return new, size.lines
    return stamp, None


def processing(limit, isatty, proc):
    date = None
    lines = None
    commits = 0
    stats = {}
    stream = proc.stdout
    try:
        if isatty:
            write("\033[?25l")  # hide cursor
            write("\033[H\033[J")  # clear screen
            stamp = time.monotonic() - 0.1
            while _running and (not limit or commits < limit):
                date = process(stream, stats)
                stamp, lines_update = display(stamp, stats, commits, date)
                if lines_update:
                    lines = max(4, lines_update - 6)
                commits += 1
        else:
            while _running and (not limit or commits < limit):
                date = process(stream, stats)
                commits += 1
    except EndOfFile:
        pass
    finally:
        if isatty:
            write("\033[?25h")  # show cursor
        if date:
            if isatty and commits:
                write("\033[H\033[J")  # clear screen
            output(stats, commits, date, lines)


@click.command(
    help=(
        "Display git contribution statistics (insertions + deletions). "
        "Most arguments of `git log` will work as GITARGS, but do not change "
        "the output-format. Use -- to separate GITARGS."
    )
)
@click.option("-l", "--limit", default=0, type=int, help="Number of commits to read")
@click.option("--tty/--no-tty", default=True, help="Enable tty")
@click.argument("gitargs", nargs=-1)
def main(limit, gitargs, tty):
    ext = []
    if gitargs:
        ext = list(gitargs)
    try:
        test = ext
        if "-n" in ext:
            pos = ext.index("-n")
            test = ext[:pos] + ext[pos + 2 :]
        check_call(cmd + ["-n", "0"] + test)
    except CalledProcessError:
        raise click.Abort()
    isatty = tty and os.isatty(sys.stdout.fileno())
    proc = Popen(cmd + ext, stdout=PIPE, preexec_fn=os.setsid)
    try:
        processing(limit, isatty, proc)
    finally:
        proc.terminate()
        if not proc.wait(1):
            proc.kill()


if __name__ == "__main__":
    main()
