git-runstats
============

Display git contribution statistics (insertions + deletions)

[![demo](https://raw.githubusercontent.com/adfinis-sygroup/git-runstats/master/runstats_demo.svg)](https://raw.githubusercontent.com/adfinis-sygroup/git-runstats/master/runstats_demo.svg)

Usage
-----

```
Usage: git-runstats [OPTIONS] [GITARGS]...

  Most arguments of `git log` will work as GITARGS, but do not change the
  output-format. Use -- to separate GITARGS.

Options:
  -l, --limit INTEGER  Number of commits to read
  --tty / --no-tty     Enable tty
```

Live-stats

```bash
git runstats
```

Stats for `README.md`

```bash
git runstats README.md
```

Display help

```bash
git-runstats --help
```

Non-live stats with limit

```bash
git runstats -l 1000 | less
```

Non-live stats reversed

```bash
git runstats -l 1000 | head -n -1 | sort -n
```

Show stats in branch

```bash
git runstats master..my_branch
```

Show stats in current branch

```bash
git runstats master..
```

Show stats from 2019

```bash
git runstats -- --since=2019-01-01 --until=2019-12-31
```

Who knows most about the rust Alpine Linux package

```bash
cd aports
git runstats community/rust
```

Install
-------

```bash
pip install git-runstats
```

Why
---

In comparison to shortlog `runstats` gives immediate feedback and counts changes
instead of commits. Press Ctrl-C once you have enough information. Shortlog can
also be very wrong:

```bash
$> cd linux
$> git shortlog -s -n net/802/ | head -n 10
    11  Stephen Hemminger
    10  Arnaldo Carvalho de Melo
     9  Eric Dumazet
     6  Eric W. Biederman
     5  Alexey Dobriyan
     5  David S. Miller
     4  Paul Gortmaker
     4  David Ward
     3  Linus Torvalds
     3  Adrian Bunk
```

versus

```bash
$> cd linux
$> git runstats net/802/ | head -n 10
      1556  Linus Torvalds
       931  David Ward
       749  Patrick McHardy
       104  Stephen Hemminger
        98  Eric Dumazet
        65  Pavel Emelyanov
        51  Thomas Gleixner
        47  Johannes Berg
        40  Alexey Dobriyan
        30  Joe Perches
```
