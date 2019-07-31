# maba
Helper for dumping/analyzing MBR/GPT dump file

## Introduction
This little python script is an helper for handling MBR/GPT file.

It takes a file that contains a valid MBR partition (protective MBR for GPT) and print out information (like bootcode/GUID) and partitions.

## Installing
### Dependencies
* Python (version 3)
* python prettytable
* dd
#### ARCH
```
pacman -S python
pacman -S python-prettytable
```
#### Other distribution
1. Install `python` (version 3) and `pip`
2. `pip install PrettyTable`

## How to use it
```
./maba.py -h
  usage: maba.py [-h] [-v] filename

  Extract partition data from MBR/GPT file

  positional arguments:
    filename       Dump's file

  optional arguments:
    -h, --help     show this help message and exit
    -v, --verbose  Verbose output
```
Simply use `./maba <filename>`.
```
  ./maba.py ../full_system

  Help:

  pm              Print MBR sector
  pg              Print GPT sector
  pmps            Print MBR partitions
  pmp <num>       Print MBR partition <num>
  pgps            Print GPT partitions
  pgp <num>       Print GPT partition <num>
  dms             Dump MBR partitions
  dm <num>        Dump MBR partition <num>
  dgs             Dump GPT partitions
  dg <num>        Dump GPT partition <num>
  q               Exit
```
The dumped partition are saved in the same directory of the file.

## NOTE
There are a lot of error and the code is not optimized. For example, there is no check in the partition number (crash). Improvements will be introducted during my IoT reverse engieering journey. Any contributions are welcome.
