#!/usr/bin/env python

import argparse
import struct
import subprocess
verb = False
filename = ""

## Utilities
def verbose(data):
    global verb
    if verb == True:
        print("# "+str(data))

def chs_decode(data):
    verbose(data)
    cyl = data[2] | ((data[1] & 0xC0)<<2)
    head = data[0]
    sect = data[1] & 0x3F
    return [cyl,head,sect]

def dump(start,end,sector,output):
    global filename
    cmd = ['dd','if='+filename,'of='+output,'bs='+str(sector),'skip='+str(start),'count='+str(end)]
    print(str(cmd))
    subprocess.check_output(cmd)
   

## GPT Class
class GPT():
    def __init__(self,reader):
        verbose('Starting dumping GPT')
        verbose('Open partition type file \'guid.type\'')
        pp = open('./lib/guid.type','r')
        guid_type={}
        for i in pp.readlines():
            sp = i.split(',')
            verbose(sp)
            inx = sp[0]
            description = ""
            for t in sp[1:]:
                description+=t
            description = description.strip()
            guid_type[inx]=description
            verbose('Description:' +description)
        pp.close()
        ## Signature
        signature = reader.read(8)
        verbose('Signature: '+str(signature))
        if signature != b'EFI PART':
            verbose("GPT signature is wrong! ("+str(signature)+")")
            return
        ## Revision number
        revision = reader.read(4)
        verbose('Revision: '+str(revision))
        self.revision = struct.unpack('>I',revision)[0]
        verbose('Revision version: '+str(self.revision))
        ## Header size
        header_size = reader.read(4)
        verbose('Header size: '+str(header_size))
        self.header_size = struct.unpack('<I',header_size)[0]
        verbose('Header size:'+str(header_size))
        ## CRC
        crc = reader.read(4)
        verbose('CRC: '+str(crc))
        self.crc = struct.unpack('<I',crc)[0]
        verbose('CRC: '+hex(self.crc))
        ## Reserved bytes
        verbose('Reserved bytes (should be zero): '+hex(struct.unpack('<I',reader.read(4))[0]))
        ## Current LBA
        curr_lba = reader.read(8)
        verbose('Current LBA: '+str(curr_lba))
        self.curr_lba = struct.unpack('<Q',curr_lba)[0]
        verbose("Current LBA: "+hex(self.curr_lba))
        ## Backup LBA
        back_lba = reader.read(8)
        verbose('Backup LBA: '+str(back_lba))
        self.back_lba = struct.unpack('<Q',back_lba)[0]
        verbose("Backup LBA: "+hex(self.back_lba))
        ## First LBA
        first_lba = reader.read(8)
        verbose('First LBA: '+str(first_lba))
        self.first_lba = struct.unpack('<Q',first_lba)[0]
        verbose('First LBA: '+hex(self.first_lba))
        ## Last LBA
        last_lba = reader.read(8)
        verbose('Last LBA: '+str(last_lba))
        self.last_lba = struct.unpack('<Q',last_lba)[0]
        verbose("Last usable LBA: "+hex(self.last_lba))
        ## Disk GUID
        disk_guid_t = reader.read(16)
        self.disk_guid = ''.join('%02X'%i for i in reversed(disk_guid_t[0:4])) + '-' + ''.join('%02X' % i for i in reversed(disk_guid_t[4:6])) + '-' + ''.join('%02X' % i for i in reversed(disk_guid_t[6:8])) + '-' + ''.join('%02X' % i for i in disk_guid_t[8:10]) + '-' + ''.join('%02X' % i for i in disk_guid_t[10:])
        verbose('Disk GUID: '+self.disk_guid)
        ## Starting LBA
        starting_lba = reader.read(8)
        verbose('Staring LBA: '+str(starting_lba))
        self.starting_lba = struct.unpack('<Q',starting_lba)[0]
        verbose("Starting LBA: "+hex(self.starting_lba))
        ## Number of partitions
        n_partitions = reader.read(4)
        verbose('Number of entry: '+str(n_partitions))
        self.n_partitions = struct.unpack('<I',n_partitions)[0]
        verbose("Number of partitions entry:"+str(n_partitions))
        ## Partition's size
        part_size = reader.read(4)
        verbose('Partition size: '+str(part_size))
        self.part_size = struct.unpack('<I',part_size)[0]
        verbose("Partition size:"+str(part_size))
        ## Partition CRC
        p_crc = reader.read(4)
        verbose('Partition CRC: '+str(p_crc))
        self.p_crc = struct.unpack('<I',p_crc)[0]
        verbose("Partition CRC:"+hex(self.p_crc))
        ## Reading the remained header
        remained = self.header_size - 92
        verbose('Remained data: '+str(remained))
        self.reserved = reader.read(remained)
        if remained != 0:
            verbose('Reserved data: '+str(reserved))
        padding = reader.read(512-92-remained)
        #Looping over partitions
        self.partitions = []
        inx = 0
        while inx < self.n_partitions:
            verbose('Partition N: '+str(inx+1))
            tm = {}
            p1 = reader.read(self.part_size)
            verbose('Partition entry: '+str(p1))
            i=0
            type_guid_t = p1[i:i+16]
            i+=16
            ## Type GUID
            type_guid = ''.join('%02X'%i for i in reversed(type_guid_t[0:4])) + '-' + ''.join('%02X' % i for i in reversed(type_guid_t[4:6])) + '-' + ''.join('%02X' % i for i in reversed(type_guid_t[6:8])) + '-' + ''.join('%02X' % i for i in type_guid_t[8:10]) + '-' + ''.join('%02X' % i for i in type_guid_t[10:])
            try:
                tm['type_guid'] = [type_guid,guid_type[type_guid]]
                verbose('Partition type GUID:   '+type_guid + '('+guid_type[type_guid]+')')
            except KeyError:
                tm['type_guid'] = [type_guid,'Unkown'] 
                verbose('Partition type GUID:   '+type_guid + '(Unkown)')
            ## part GUID
            part_guid_t = p1[i:i+16]
            i+=16
            part_guid = ''.join('%02X'%i for i in reversed(part_guid_t[0:4])) + '-' + ''.join('%02X' % i for i in reversed(part_guid_t[4:6])) + '-' + ''.join('%02X' % i for i in reversed(part_guid_t[6:8])) + '-' + ''.join('%02X' % i for i in part_guid_t[8:10]) + '-' + ''.join('%02X' % i for i in part_guid_t[10:])
            verbose('Unique partition GUID: '+part_guid)
            tm['part_guid'] = part_guid
            ## First LBA
            first_lba = p1[i:i+8]
            i+=8
            tm['first_lba'] = struct.unpack('<Q',first_lba)[0]
            verbose('First partition LBA: '+str(tm['first_lba']))
            ## Last LBA
            tm['last_lba'] = struct.unpack('<Q',p1[i:i+8])[0]
            i+=8
            verbose('Last partition LBA: '+str(tm['last_lba'])) 
            ## Attribute FLAG TODO:: DECODE IT!
            attr_flag = p1[i:i+8]
            tm['attr_flag'] = bin(struct.unpack('<Q',attr_flag)[0])
            i+=8
            verbose("Attribute flag: "+str(attr_flag))
            tm['name'] = p1[i:i+72].decode('utf-16le')
            verbose('Partition name: '+str(tm['name']))
            i+=72
            if i < self.part_size:
                remained = p1[i:]
                verbose("Remained data:"+str(remained))
            self.partitions.append(tm)
            inx +=1
    def dump_partitions(self):
        i = 0
        while i < len(self.partitions):
            self.dump_partition(i)
            i+=1
    def dump_partition(self,i):
        global filename
        part = self.partitions[i]
        print(part['type_guid'][1])
        if 'Unused' in part['type_guid'][1]:
            print('!!!!')
            return
        ff = filename.split('/')[:-1]
        n = ""
        for i in ff:
            n += i+'/'
        name = n + part['name'].replace('\x00','')
        dump(part['first_lba'],part['last_lba'] - part['first_lba'] + 1,512,name)
    def disk_info(self):
        ret = ""
        ret += 'GPT Revision:'  + str(self.revision)+'\n'
        ret += 'Header size:'   + str(self.header_size)+'\n'
        ret += 'Header CRC:'    + hex(self.crc)+'\n'
        ret += 'Current LBA:'   + str(self.curr_lba)+'\n'
        ret += 'Backup LBA:'    + str(self.back_lba)+'\n'
        ret += 'First LBA:'     + str(self.first_lba)+'\n'
        ret += 'Last LBA:'      + str(self.last_lba)+'\n'
        ret += 'Disk GUID:'     + self.disk_guid+'\n'
        ret += 'Starting LBA:'  + str(self.starting_lba)+'\n'
        ret += 'Number of partitions:'+ str(self.n_partitions)+'\n'
        ret += 'Partition size:'    + str(self.part_size)+'\n'
        ret += 'Partitions CRC:'    + str(self.p_crc)+'\n'
        return ret
    def ppartitions(self):
        ret = []
        i = 0
        while i < len(self.partitions):
            ret.append(self.partition(i))
            i+=1
        return ret
    def partition(self,i):
        tm = self.partitions[i]
        ret = []
        ret.append(str(i+1))
        ret.append(tm['type_guid'][1]+'\n('+tm['type_guid'][0]+')')
        ret.append(tm['part_guid'])
        ret.append(str(tm['first_lba']))
        ret.append(str(tm['last_lba'])) 
        ret.append(tm['attr_flag']) 
        ret.append(tm['name'])
        return ret 
## class MBR
class MBR():
    def __init__(self,header):
        self.filename = filename
        verbose('Open partition type file \'partitions.type\'')
        pp = open('./lib/partitions.type','r')
        p_type={}
        for i in pp.readlines():
            sp = i.split(',')
            verbose(sp)
            inx = int(sp[0],16)
            description = ""
            for t in sp[1:]:
                description+=t
            description = description.strip()
            p_type[inx]=description
            verbose('Description:' +description)
        pp.close()
        self.bootcode    = header[:446]
        self.partitions  = []
        self.gpt         = False
        i           = 446
        inx         = 0
        verbose('Boot code:\n'+str(self.bootcode))
        verbose('Looping over partition')
        while i < 510:
            tm = {}
            p1 = header[i:i+16]
            verbose('Partition:\n'+str(p1))
            i+=16
            if p1[0] == 0x80:
                b_stx = 'bootable'
            elif p1[0] == 0x00:
                b_stx = 'not bootable'
            else:
                b_stx = 'invalid'
            tm['bootable'] = [p1[0],b_stx]
            verbose('\tBootable bit: '+hex(p1[0])+' ('+b_stx+')')
            chs = chs_decode(p1[1:4])
            tm['chs_first'] = chs
            verbose('\tCHS first sector:')
            verbose('\t\tCylinder:'+hex(chs[0]))
            verbose('\t\tHead:'+hex(chs[1]))
            verbose('\t\tSector:'+hex(chs[2]))
            verbose('\tPartition type:'+hex(p1[4])+' ('+p_type[p1[4]]+')')
            tm['p_type'] = [p1[4],p_type[p1[4]]] 
            if p1[4] == 0xEE:
                self.gpt = True
            verbose('\tCHS last sector:')
            chs = chs_decode(p1[5:8])
            tm['chs_last'] = chs
            verbose('\t\tCylinder:'+hex(chs[0]))
            verbose('\t\tHead:'+hex(chs[1]))
            verbose('\t\tSector:'+hex(chs[2]))
            x = struct.unpack('<I',p1[8:12])[0]
            tm['LBA_first'] = [x, hex(x)]
            verbose('\tLBA of first sector:'+hex(x))
            x = struct.unpack('<I',p1[12:16])[0]
            verbose('\tNumber of sector:'+hex(x))
            tm['num_sector'] = [x,hex(x)]
            self.partitions.append(tm)
            inx+=1
    def dump_partition(self, i):
        part = self.partitions[i]
        dump(part['LBA_first'][0],part['num_sector'][0],512,filename+'.part'+str(i+1))
    def dump_partitions(self):
        i = 0
        while i < len(self.partitions):
            self.dump_partition(i)
            i+=1
    def print_bootcode(self):
        ret = ''.join('%02X' % i for i in self.bootcode)
        #ret += '\n\nDisassembled:TODO'
        return str(ret)
    def print_partitions(self):
        ret = []
        i = 0
        while i < len(self.partitions):
            ret.append(self.print_partition(i))
            i+=1
        return ret
    def print_partition(self,i):
        ret = []
        part = self.partitions[i]
        ret.append(str(i+1))
        ret.append(str(part['chs_first'][0])+'-'+str(part['chs_first'][1])+'-'+str(part['chs_first'][2]))
        ret.append(str(part['chs_last'][0])+'-'+str(part['chs_last'][1])+'-'+str(part['chs_last'][2]))
        ret.append(str(part['LBA_first'][0])+' ('+part['LBA_first'][1]+')')
        ret.append(str(part['num_sector'][0])+' ('+part['num_sector'][1]+')')
        ret.append(part['bootable'][1]+' ('+str(part['bootable'][0])+')')
        ret.append(part['p_type'][1]+' ('+str(part['p_type'][0])+')')
        return ret
## Entry point of the analyzer
def analyze(args):
    ## Returned object
    ## Reader object
    global filename
    filename = args.filename
    reader = open(args.filename,'rb')
    ## header data
    header = reader.read(512)
    verbose('MBR Raw data:\n'+str(header))
    verbose('Test if it is an MBR partition')
    sign = header[-2:]
    verbose('Signature:\n'+str(sign))
    ## Is a MBR data?
    if sign == b'\x55\xaa':
        mbr = None
        gpt = None
        verbose("Detected MBR sector, proceed with extraction");
        mbr = MBR(header);
        verbose("There also a GPT partition? "+str(mbr.gpt));
        verbose('Dump partitions: '+str(mbr.partitions))
        if mbr.gpt == True:
            verbose("Found a GPT protective MBR partition.")
            gpt = GPT(reader)
        return mbr,gpt
    else:
        print("Can not find MBR signature. Exiting...")
        return
