#!/usr/bin/env python
import argparse
import lib
from prettytable import PrettyTable
def Help():
    print('Help:\n')
    print('pm\t\tPrint MBR sector')
    print('pg\t\tPrint GPT sector')
    print('pmps\t\tPrint MBR partitions')
    print('pmp <num>\tPrint MBR partition <num>')
    print('pgps\t\tPrint GPT partitions')
    print('pgp <num>\tPrint GPT partition <num>')
    print('dms\t\tDump MBR partitions')
    print('dm <num>\tDump MBR partition <num>')
    print('dgs\t\tDump GPT partitions')
    print('dg <num>\tDump GPT partition <num>')
    print('q\t\tExit')

def print_mbr_info(mbr):
    print('Bootcode: '+mbr.print_bootcode())

def print_mbr_partition(mbr,i):
    r = mbr.print_partition(i)
    t = PrettyTable(['Index', 'First CHS','Last CHS','LBA First','# Sectors','Bootable bit','Partition Type'])
    t.add_row(r)
    print(t)

def print_mbr_partitions(mbr):
    r = mbr.print_partitions()
    t = PrettyTable(['Index', 'First CHS','Last CHS','LBA First','# Sectors','Bootable bit','Partition Type'])
    for i in r:
        t.add_row(i)
    print(t)

def print_mbr(mbr):
    print('-*'*25+'MBR'+'-*'*25)
    print_mbr_info(mbr)
    print_mbr_partitions(mbr)
    print('-'*103) 

def print_gpt_information(gpt):
    print(gpt.disk_info())

def print_gpt_partitions(gpt):
    r = gpt.ppartitions()
    t = PrettyTable(['Index','Type GUID','Part GUID','First LBA','Last LBA','Flag attribute','Partition Name'])
    for i in r:
        if 'Unused' in  i[1]:
            continue
        t.add_row(i)
    print(t)

def print_gpt(gpt):
    print('-*'*25+'GPT'+'-*'*25)
    print_gpt_information(gpt)
    print_gpt_partitions(gpt)
    print('-'*103)

def print_gpt_partition(gpt,i):
    r = gpt.partition(i)
    t = PrettyTable(['Index','Type GUID','Part GUID','First LBA','Last LBA','Flag attribute','Partition Name'])
    t.add_row(r)
    print(t)

def main(args):
    mbr,gpt = lib.analyze(args)
    while True:
        print('\n\n')
        Help()
        cmd=input('Command: ')
        cmd = cmd.split()
        if cmd[0] == 'q':
            break
        if cmd[0] == 'pm':
            print_mbr(mbr)
        if cmd[0] == 'pg':
            #print_gpt
            pass
        if cmd[0] == 'pmps':
            print_mbr_partitions(mbr)
        if cmd[0] == 'pmp':
            print_mbr_partition(mbr,int(cmd[1]))
        if cmd[0] == 'pg':
            print_gpt(gpt)
        if cmd[0] == 'pgp':
            print_gpt_partition(gpt,int(cmd[1]))
        if cmd[0] == 'pgps':
            print_gpt_partitions(gpt)
        if cmd[0] == 'dm':
            mbr.dump_partition(int(cmd[1])-1)
        if cmd[0] == 'dms':
            mbr.dump_partitions()
        if cmd[0] == 'dg':
            gpt.dump_partition(int(cmd[1])-1)
        if cmd[0] == 'dgs':
            gpt.dump_partitions()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract partition data from MBR/GPT file")
    parser.add_argument('filename',help='Dump\'s file')
    parser.add_argument('-v','--verbose',action='store_true',default=False,help='Verbose output')
    args = parser.parse_args()
    lib.verb = args.verbose
    main(args)
