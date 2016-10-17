from collections import namedtuple
import struct
import binascii

MPF_FIXMAP  = 0x80
MPF_MAP16   = 0xde
MPF_MAP32   = 0xdf

MPF_FIXARRAY= 0x90
MPF_ARRAY16 = 0xdc
MPF_ARRAY32 = 0xdd

MPF_FIXSTR  = 0xa0
MPF_STR8    = 0xd9
MPF_STR16   = 0xda
MPF_STR32   = 0xdb

MPF_BIN8    = 0xc4
MPF_BIN16   = 0xc5
MPF_BIN32   = 0xc6

MPF_FALSE   = 0xc2
MPF_TRUE    = 0xc3

MPF_INT8    = 0xd0
MPF_INT16   = 0xd1
MPF_INT32   = 0xd2
MPF_INT64   = 0xd3

MPF_UINT8   = 0xcc
MPF_UINT16  = 0xcd
MPF_UINT32  = 0xce
MPF_UINT64  = 0xcf

MPF_NIL     = 0xc0

rdbheader   = namedtuple("rdbheader","magic_number metadata_offset")
rmsg        = namedtuple("rmsg","typ value")
rfield      = namedtuple("rdbfield","name value")
rrecord     = namedtuple("rrecord","count fields")

def get_rmsg(data,index):
    buf = data[index]
    if  (buf < MPF_FIXMAP):
        return index + 2,rmsg("int",data[index+1])
    elif(buf < MPF_FIXARRAY):
        msglen = buf ^ MPF_FIXMAP
        return index + 1,rmsg("fixmap",msglen)
    elif(buf < MPF_FIXSTR):
        msglen = buf ^ MPF_FIXARRAY
        return index + msglen+1,rmsg("fixarray",data[index+1:index+1+msglen])
    elif(buf < MPF_NIL):
        msglen = buf ^ MPF_FIXSTR
        return index + msglen+1,rmsg("string",data[index+1:index+1+msglen].decode("utf-8"))
    elif(buf > MPF_MAP32):
        return index + 2,rmsg("int",data[index+1] - 0xFF -1)
    elif(buf == MPF_NIL):
        return index + 1,rmsg("nil",0)
    elif(buf == MPF_FALSE):
        return index + 1,rmsg("bool",false)
    elif(buf == MPF_TRUE):
        return index + 1,rsmgtyp("bool",true)
    elif(buf == MPF_STR8 or buf == MPF_STR16 or buf == MPF_STR32):
        bytelen = (buf ^ MPF_STR8) + 1
        unpackformat = str(bytelen) + "B"
        msglen = struct.unpack(unpackformat,data[index+1:index+bytelen+1])[0]
        val = data[index+bytelen+1:index+bytelen+msglen+1].decode("utf-8")
        return index + msglen+bytelen+1,rmsg("string",val)
    elif(buf == MPF_BIN8 or buf == MPF_BIN16 or buf == MPF_BIN32):
        bytelen = (buf ^ MPF_BIN8) + 1
        unpackformat = str(bytelen) + "B"
        msglen = struct.unpack(unpackformat,data[index+1:index+bytelen+1])[0]
        val = binascii.hexlify(data[index+bytelen+1:index+bytelen+msglen+1])
        return index + msglen+bytelen+1,rmsg("binstr",val)
    elif(buf == MPF_INT8):
        val = struct.unpack('>b',data[index+1:index+2])[0]
        return index + 2,rmsg("int",val)        
    elif(buf == MPF_INT16):
        val = struct.unpack('>h',data[index+1:index+3])[0]
        return index + 3,rmsg("int",val) 
    elif(buf == MPF_INT32):
        val = struct.unpack('>i',data[index+1:index+5])[0]
        return index + 5,rmsg("int",val) 
    elif(buf == MPF_INT64):
        val = struct.unpack('>q',data[index+1:index+9])[0]
        return index + 9,rmsg("int",val)
    elif(buf == MPF_UINT8):
        val = struct.unpack('>B',data[index+1:index+2])[0]
        return index + 2,rmsg("uint",val)        
    elif(buf == MPF_UINT16):
        val = struct.unpack('>H',data[index+1:index+3])[0]
        return index + 3,rmsg("uint",val) 
    elif(buf == MPF_UINT32):
        val = struct.unpack('>I',data[index+1:index+5])[0]
        return index + 5,rmsg("uint",val) 
    elif(buf == MPF_UINT64):
        val = struct.unpack('>Q',data[index+1:index+9])[0]
        return index + 9,rmsg("uint",val) 
    else:
        return index + 1,rmsg("unknown",hex(buf))

def set_msg(rmsg):
    if(rmsg.typ=="fixmap"):
        if(rmsg.value<(1 << 4)):
            return bytearray(struct.pack("B",MPF_FIXMAP | rmsg.value))
        elif(rmsg.value<(1 << 16)):
            return bytearray(struct.pack("BH",MPF_MAP16,rmsg.value))
        elif(rmsg.value<(1 << 32)):
            return bytearray(struct.pack("BL",MPF_MAP32,rmsg.value))
    elif(rmsg.typ=="string"):
        strlen = len(rmsg.value)
        if(strlen<(1 << 5)):
            return bytearray(struct.pack("B"+str(strlen)+"s",MPF_FIXSTR | strlen,rmsg.value.encode("utf-8")))
        elif(strlen<(1 << 8)):
            return bytearray(struct.pack("BB"+str(strlen)+"s",MPF_STR8,strlen,rmsg.value.encode("utf-8")))
        elif(strlen<(1 << 16)):
            return bytearray(struct.pack("BH"+str(strlen)+"s",MPF_STR16,strlen,rmsg.value.encode("utf-8")))
        else:
            return bytearray(struct.pack("BL"+str(strlen)+"s",MPF_STR32,strlen,rmsg.value.encode("utf-8")))
    elif(rmsg.typ=="binstr"):
        binstr = bytearray(binascii.unhexlify(rmsg.value))
        strlen = len(binstr)
        if(strlen<(1 << 8)):
            return bytearray(struct.pack("BB"+str(strlen)+"B",MPF_BIN8,strlen,*binstr))
        elif(strlen<(1 << 16)):
            return bytearray(struct.pack("BH"+str(strlen)+"B",MPF_BIN16,strlen,*binstr))
        else:
            return bytearray(struct.pack("BL"+str(strlen)+"B",MPF_BIN32,strlen,*binstr))
    elif(rmsg.typ=="uint"):
        if(rmsg.value<(1 << 8)):
            return bytearray(struct.pack(">BB",MPF_UINT8,rmsg.value))
        elif(rmsg.value<(1 << 16)):
            return bytearray(struct.pack(">BH",MPF_UINT16,rmsg.value))
        elif(rmsg.value<(1 << 32)):
            return bytearray(struct.pack(">BI",MPF_UINT32,rmsg.value))
        else:
            return bytearray(struct.pack(">BQ",MPF_UINT64,rmsg.value))
    elif(rmsg.typ=="int"):
        if(rmsg.value>=0 and rmsg.value <(1 << 7)):
            return bytearray(struct.pack("b",rmsg.value))
        if(rmsg.value<0 and rmsg.value > (-1 << 5)):
            return bytearray(struct.pack("b",rmsg.value))
        if(rmsg.value<(1 << 7) or rmsg.value >=(-1 << 7)):
            return bytearray(struct.pack(">Bb",MPF_INT8,rmsg.value))
        elif(rmsg.value<(1 << 15) or rmsg.value >=(-1 << 15)):
            return bytearray(struct.pack(">Bh",MPF_INT16,rmsg.value))
        elif(rmsg.value<(1 << 31) or rmsg.value >=(-1 << 31)):
            return bytearray(struct.pack(">Bi",MPF_INT32,rmsg.value))
        else:
            return bytearray(struct.pack(">Bq",MPF_INT64,rmsg.value))
    elif(rmsg.typ == "nil"):
        return bytearray(struct.pack("B",MPF_NIL))
    elif(rmsg.typ == "bool"):
        if(rmsg.value==True):
            return bytearray(struct.pack("B",MPF_TRUE))
        else:
            return bytearray(struct.pack("B",MPF_FALSE))
    else:
        return bytearray()

def read_rfield(data,offset):
    index = offset
    index, namemsg = get_rmsg(data,index)
    index, valuemsg = get_rmsg(data,index)
    fld = rfield(namemsg.value,valuemsg.value)
    return index, fld

def write_rfield(name,value,typ):
    data = bytearray()
    data+=(set_msg(rmsg("string",name)))
    data+=(set_msg(rmsg(typ,value)))
    return data
    
def open_rdb(filename):
    rdbf = open(filename,"rb")
    data = bytearray(rdbf.read())
    index = 0
    header = rdbheader._make(struct.unpack("8sQ",data[index:16]))
    index += 16
    db = []    
    while(index<len(data)):
        index,msg = get_rmsg(data,index)
        if(msg.typ == "fixmap"):
            record=[]
            for fieldid in range(0,msg.value):
                index, fld = read_rfield(data,index)
                record.append(fld)
            if(msg.value==1 and fld.name == "count"):
                print str(fld.value) + " records exported"
            else:   
                db.append(record)
    return db

def write_rdb(filename,db):
    rdbf = open(filename,"wb")
    header = rdbheader("RARCHDB\0",0)
    rdbf.write(struct.pack("8sQ",*header))
    for record in db:
        nbfields = 0
        for field in record:
            if not (field.value is None or field.value=="" or field.value==0):
                nbfields += 1
        rdbf.write(set_msg(rmsg("fixmap",nbfields)))
        for field in record:
            if not (field.value is None or field.value=="" or field.value==0):
                if(field.name in ['name','description','rom_name','genre','franchise','developer','publisher','origin']):    
                    rdbf.write(write_rfield(field.name,field.value,"string"))
                elif(field.name in ['size','releasemonth','releaseyear','users']):
                    rdbf.write(write_rfield(field.name,int(field.value),"uint"))
                elif(field.name in ['crc','md5','sha1']):
                    rdbf.write(write_rfield(field.name,field.value,"binstr"))
    rdbf.write(set_msg(rmsg("nil","")))
    rdbf.write(set_msg(rmsg("fixmap",1)))
    rdbf.write(write_rfield("count",len(db),"uint"))
    rdbf.close()
