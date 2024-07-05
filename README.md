## VACCINE virus remover

Simple script for remove _vaccine_ virus from MA files

```shell
python vaccine_remover.py /path/to/file.ma -b
python vaccine_remover.py /path/to/dir -b -r
```

*-r, --replace*: Replace the old file (the old file will be removed if the flag -b is not set) or rename the cleared file with a suffix

*-b, --backup*: Make an MA file backup on replace instead of removing it.

Examples:

Create `*.clean` files above original

```shell
python vaccine_remover.py [path] 
```

Replace original files

```shell
python vaccine_remover.py [path] -r 
```

Backup original files and rename cleared to original name

```shell
python vaccine_remover.py [path] -r -b
```

