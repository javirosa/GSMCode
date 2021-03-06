#TODO   signal minimum
#       check valid numbers w/check_num()

min_signal=0 #minimum signal required to send a message

def at(modem, *args):
    """
    """
    if len(args)==0:
        return modem.send('AT\r\n')
    elif len(args)==1:
        return modem.send('AT+'+args[0]+'\r\n')
    else:
        #modem.send("AT+CMGW=\""+str(args[1])+"\"\r\n", args[2])
        modem.send("AT+"+args[0]+str(args[1])+"\"\r\n", args[2])

#MODEM INFORMATION
def mfgr(modem):
    """Return manufacturer id"""
    return at(modem, "CGMI")

def model(modem):
    """Return model id"""
    return at(modem, "CGMM")

def revision(modem):
    """Return revision id"""
    return at(modem, "CGMR")

def imei(modem):
    """Return serial number (IMEI)"""
    return at(modem, "CGSN")

def imsi(modem):
    """Return IMSI"""
    return at(modem, "CIMI")

def ccid(modem):
    """Return CCID"""
    return at(modem, "CCID")

def info(modem):
    """Return dictionary of modem info:
    mfgr : Manufacturer ID 
    model : Model ID
    revision: Revision ID
    imei: Serial Number (IMEI)
    imsi: IMSI
    ccid: CCID
    """
    return {'mfgr': mfgr(modem),
            'model': model(modem), 
            'revision': revision(modem),
            'IMEI': imei(modem),
            'IMSI': imsi(modem),
            'CCID': ccid(modem),}

#MODEM OPTIONS
def set_charset(modem, charset):
    """Set the character set

    charset -- a valid character set, options include:
    "IRA","GSM","PCCP437","8859-1","UCS2","HEX","SYNC" 
    (default "GSM")
    """
    if charset in ("IRA","GSM","PCCP437","8859-1","UCS2","HEX","SYNC"):
        at(modem, 'CSCS="'+charset+'"')
        modem.charset = charset
    else:
        raise ValueError('Incompatible charset: '+charset)

def set_detailed_error(modem, enable=1):
    """Enables/disables detailed error messages from modem
    
    enable -- 1 or true value enables, 0 disables (default 1)
    """ 
    if enable:
        at(modem,"CMEE=2")
    else:
        at(modem,"CMEE=0")

def set_pdu(modem, text=1):
    """Sets text mode to PDU or Text

    text -- 1 or true enables text mode, 
            0 or false enables PDU mode
    """
    if text:
        at(modem, "CMGF=1")
        modem.pdu = False
    else:
        at(modem, "CMGF=0")
        modem.pdu = True

def text_mode(modem):
    if modem.charset != "GSM":
        set_charset(modem, "GSM")
        modem.charset = "GSM"
    if not modem.pdu:
        set_pdu(modem, 1)
        modem.pdu = False

#NETWORK AND CONNECTION
def signal(modem, detail=0):
    """Check signal quality

    detail -- 1 or true value enables detailed value

    returns signal quality values for detailed or True 
    if not unknown and above minimum value
    """
    q = at(modem, "CSQ?")[1].replace("+CSQ:",'').replace(",",'').strip()
    if q[:2] =='99' or q[2:] =='99':
        #Indicates no or unknown signal
        return False
    #elif q[:2]<=min:
    #    return False
    else:
        return True

def connected(modem, detail=0):
    """ Check network registration

    detail -- 1 or true value returns detailed response

    return connection status (True/False or detailed)
    """
    creg = at(modem,"CREG?")[1].replace("+CREG:",'').replace(",",'').strip()
    if detail:
        return creg
    elif creg[1]=='1':
        #Indicates registered
        return True
    else:
        #Not registered
        return False
        
def check_network(modem):
    """ Check network connection and quality

    return status (True/False or detailed)
    """
    if connected(modem) and signal(modem):
        return True
    else:
        return False

#MESSAGING
def send(modem, number, msg):
    """Sends an SMS to the specified number"""
    text_mode(modem)
    #check_num()
    at(modem, "CMGS=\"", number, msg)

def save_msg(modem, number, msg):
    """Sends an SMS to the specified number"""
    text_mode(modem)
    at(modem, "CMGW=\"", number, msg)

def get_all(modem):
    """Get all messages"""
    text_mode(modem)
    return at(modem, 'CMGL="ALL"')

def get_unread(modem):
    """Get all recieved messages"""
    text_mode(modem)
    return at(modem, 'CMGL="REC UNREAD"')

def get_rec(modem):
    """Get unread recieved messages"""
    text_mode(modem)
    return at(modem, 'CMGL="REC UNREAD"').append(\
        at(modem, 'CMGL="REC READ"'))

def get_rec_read(modem):
    """Get read messages"""
    text_mode(modem)
    return at(modem, 'CMGL="REC READ"')

def get_sto_sent(modem):
    """Get stored, sent messages"""
    text_mode(modem)
    return at(modem, 'CMGL="STO SENT"')

def get_sto_unsent(modem):
    """Get stored unsent messages"""
    text_mode(modem)
    return at(modem, 'CMGL="STO UNSENT"')

def get_sto(modem):
    """Get stored messages"""
    text_mode(modem)
    return at(modem, 'CMGL="STO UNSENT"').append(\
        at(modem, 'CMGL="STO SENT"'))

def get_message(modem, index):
    """Get message at index on SIM"""
    text_mode(modem)
    return at(modem, 'CMGR=' + str(index))

#MEMORY
#def mem_config(modem):

def delete(modem, index):
    at(modem, 'CMGD=' + str(index))

#FLOW CONTROL

#MISCELLANEOUS
def parse_message(msg):
    temp = msg[0].split('"')
    if len(temp) >=8:
        return {'status' : temp[1],
                'number' : temp[3],
                'time' : temp[7],
                'msg' : msg[1]
                }
    else:
        return {'status' : temp[1],
                'number' : temp[3],
                'msg' : msg[1]
                }

def parse_all(raw):
    output = []
    for i in range(0, len(raw)/3, 3):
        output.append(parse_message(raw[i:i+3]))
    return output
    
