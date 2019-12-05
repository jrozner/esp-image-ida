from struct import *
from ida_entry import add_entry
import idaapi

MAGIC = 0xe9
MAX_SEGMENTS = 16
HEADER_SIZE = 24
MEMORY_MAP = [[0x3F400000, 0x3F800000, "DROM", "DATA"],
              [0x3F800000, 0x3FC00000, "EXTRAM_DATA", "DATA"],
              [0x3FF80000, 0x3FF82000, "RTC_DRAM", "DATA"],
              [0x3FF90000, 0x40000000, "BYTE_ACCESSIBLE", "DATA"],
              [0x3FFAE000, 0x40000000, "DRAM", "DATA"],
              [0x3FFAE000, 0x40000000, "DMA", "DATA"],
              [0x3FFE0000, 0x3FFFFFFC, "DIRAM_DRAM", "DATA"],
              [0x40000000, 0x40070000, "IROM", "CODE"],
              [0x40070000, 0x40078000, "CACHE_PRO", "CODE"],
              [0x40078000, 0x40080000, "CACHE_APP", "CODE"],
              [0x40080000, 0x400A0000, "IRAM", "CODE"],
              [0x400A0000, 0x400BFFFC, "DIRAM_IRAM", "CODE"],
              [0x400C0000, 0x400C2000, "RTC_IRAM", "CODE"],
              [0x400D0000, 0x40400000, "IROM", "CODE"],
              [0x50000000, 0x50002000, "RTC_DATA", "CODE"]]

def accept_file(li, filename):
    li.seek(0)
    first_byte = unpack('B', li.read(1))[0]
    if first_byte != MAGIC:
        return 0
  
    return {"format": "ESP32 Rom Image Format", "processor": "xtensa", "options":1|idaapi.ACCEPT_FIRST}

def load_file(li, neflags, format):
    idaapi.set_processor_type('xtensa', idaapi.SETPROC_LOADER)

    li.seek(0)

    # reading this member by member because of bitfields that are less than 8
    # bits. Python is a shitty language that makes this difficult
    magic = unpack('B', li.read(1))[0]
    if magic != 0xe9:
        return 0

    segment_count = unpack('B', li.read(1))[0]
    if segment_count > MAX_SEGMENTS:
        return 0

    spi_mode = unpack('B', li.read(1))[0]
    # TODO: verify spi mode is real

    spi_speed_size = unpack('B', li.read(1))[0]
    spi_speed = spi_speed_size & 0x0f
    # TODO: verify spi speed is valid

    spi_size = spi_speed_size >> 4
    # TODO: verify spi size is valid

    entry_point = unpack('<i', li.read(4))[0]

    wp_pin = unpack('B', li.read(1))[0]

    spi_pin_drv = list(unpack('BBB', li.read(3)))

    reserved = list(unpack('BBBBBBBBBBB', li.read(11)))

    hash_appended = unpack('B', li.read(1))[0]

    assert li.tell() == HEADER_SIZE, li.tell()

    pos = HEADER_SIZE

    for i in range(segment_count):
        load_addr = unpack('<i', li.read(4))[0]
        segment_len = unpack('<i', li.read(4))[0]
        seg = idaapi.segment_t()
        seg.start_ea = load_addr
        seg.end_ea = load_addr + segment_len
        seg.bitness = 1
        segment = next(filter(lambda segment: seg.start_ea >= segment[0] and seg.end_ea <= segment[1], MEMORY_MAP), None)
        assert(segment != None)
        idaapi.add_segm_ex(seg, segment[2], segment[3], 0)
        li.file2base(pos+8, seg.start_ea, seg.end_ea, 1)
        pos += 8 + segment_len

    add_entry(entry_point, entry_point, "start", 1)

    return 1
