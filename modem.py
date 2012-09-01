import serial
import time
from commands import *
#send sms to 101 with desired phone number, should get response confirming
'''
TODO
check store policy
store sorted?
    reorder if deleted
    check for most recent by date
flow control
AT&R0- Pause before sending CTS signal after receiving the Request to Send (RTS).
The delay is required by some synchronous mainframes and does not apply to asynchronous calls.

enable hardware flow control
AT&R2
'''

class ModemError(Exception):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value

class TimeoutException(Exception):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value

#check message commands/require input
#response_commands=[]
def modem_demo():
    s=Modem()
    s.test_cmd()
    print s.info()
    print s.check_network()
    print 'SIM Memory used: ', s.get_used_capacity()
    #print s.check_all()
    #print s.get_message()
    #print 'SIM Memory used: ', s.get_used_capacity()
    print 'Sending message to 9999995'
    s.send('9999995', 'Neoway modem demo '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),0)

class Modem:
    def __init__(self, port='COM7', baud=115200, retries=5, min_signal=0):
        """Creates a Modem object to establish serial communication with a modem

        port -- specify com port for serial connection (default 7)
        baud -- specify modem baud rate (default 115200)
        retries -- maximum retries for at commands before raising exception
        min_signal -- sets minimum required signal quality to send message

        Function opens serial port using pyserial, sends AT test command to verify connection, sets charset to GSM, turns on detailed error reporting
        """
        self.timeout=5
        self.retries=retries
        self.min_signal=min_signal
        #try:    
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=.5)
        self.send()
        #    self.set_charset("GSM")
        #    self.detailed_error()
        #except serial.serialutil.SerialException:
        #    print 'select another port'
    
    def send(self, cmd='AT\r\n', input=None):
        """
        display = True displays output from test (False by default)
        restart used to indicate whether previous test required a modem restart
        
        checks for errors (no echo or modem restart detected)
        retries AT command for defined retries
        exceeding retries (AT test failed) raises TimeoutException

        returns True if successful

        on 1st SerialException attempts restarting serial connection
        retries test_cmd with restart parameter set to True
        on 2nd attempt prints "port disconnected"
        
        try:
            if input:
                data=[]
                #self.ser.write("AT+CMGW=\""+str(10)+"\"\r\n")
                self.ser.write(cmd+"\""+str(10)+"\"\r\n")
                data.append(self.ser.readline().replace('\r','').replace('\n',''))
                time.sleep(.05)
                #self.ser.write("test Function"+chr(26))
                self.ser.write(input+chr(26))
                data+=self.parse_data(self.ser.readlines())
                return data
            else:  
                self.ser.flush()
                self.ser.write(cmd)
                self.timeout=0.1
                data=self.ser.readlines()
                return self.parse_data(data)

        except serial.serialutil.SerialException:
            if restart:
                print 'port disconnected'
            else:
                self.restart_serial()
                self.test_cmd(False,True)


    def parse_data(self, data):
        """
        data = list of modem responses
        removes new line characters
        returns new list
        """
        #print 'parsing data'
        output=[]
        for entry in data:
            output.append(entry.replace('\r','').replace('\n',''))
        return output
    
    def check_errors(self, data):
        """
        data = list of modem responses

        checks for ERROR

        returns False for no errors
        returns error message from modem for first ERROR in list
        """
        #print 'checking errors'
        for entry in data:
            if entry.find('ERROR')!=-1:
                return entry
        return False        

    def check_restart(self, data):
        """
        data = modem data from at command

        checks for strings indicating modem restarted

        returns True if restart detected
        returns False if no restart
        """
        for entry in data:
            if entry.find('MODEM:STARTUP')!=-1: 
                #print 'restart detected'
                return True
            if entry.find('+PBREADY')!=-1:
                #print 'ready'
                return True
        return False
    
    def restart_serial(self):
        """
        restarts serial connection
        closes and reopens port
        checks 
        """
        self.ser.close()
        self.ser.open()
        #assert self.test_cmd(False)

    def reset(self):
        """
        resets modem to factory settings
        """
        self.at_cmd('Z')

    def full_reset(self):
        """
        full software reset of modem
        """
        self.at_cmd('CFUN=1')
    
    def reconnect(self):
        """
        attempts to reconnect to network
        checks if connected
        if not tries reset
        if still not connected tries software resets to specified retry limit
        """
        self.test_cmd()
        if not self.check_network: 
            self.reset()
        attempt=0
        while not self.check_network and attempt<self.retries:
            self.full_reset()
            attempt+=1

    def at_cmd(self, cmd, attempt=0):
        """
        sends at command
        cmd= characters following "AT" in command
        automatically adds "+" if cmd is longer than 2 characters
        parses data
        checks for error codes
        retries for given retry limit
        unsuccessful raises TimeoutException

        returns data

        raises exception if test AT command fails
        """
        try:
            self.ser.flush()
            #print 'test'
            assert self.test_cmd()
            if len(cmd)<3 or cmd[0]==0:
                self.ser.write('AT'+cmd.upper()+'\r\n')
            else:
                self.ser.write('AT+'+cmd.upper()+'\r\n')
            data=self.parse_data(self.ser.readlines())
            errors=self.check_errors(data)
            #print 'at data: ',data
            #print 'errors ',errors
            if attempt==4 and errors!=False:
                raise TimeoutException('Command Failed:'+errors)
            elif errors!=False:
                #print 'repeating'
                self.at_cmd(cmd, attempt+1)
            else:
                return data
        except AssertionError:
            print 'test failed'
            # double check, may be redundant
            #    self.recover()

    def parse_messages(self, orig):
        """
        parses message
        orig = list of messages
        returns list of dictionaries containing message data and text
        """
        data=orig[1:len(orig)-1]
        output=[]
        for i in range(0, len(data), 3):
            message_data=data[i].split(',')
            message_text=data[i+1]
            output.append({'status':message_data[1], 'number':message_data[2],'date':message_data[4],'time':message_data[5],'text':message_text})
        return output

    def get_used_capacity(self,tot="50"):
        """
        checks sim card capacity used
        default value set to 50 for max
        """
        data=self.at_cmd("CPMS?")
        index=data[1].find(tot)-1
        if data[1][index-1]==',':
            return data[index]
        else:
            return data[1][index-1:index]
    
    def get_message(self, key=-1,delete=1,binary=False):
        """
        gets most recent message
        key=specified message to return
        delete=specified message to delete
        binary = True for binary messages

        for key=-1 (default) gets most recent message
        deletes oldest message
        ^small bug in deleting, need to make sure it finds the oldest message if 1st one is deleted
        """
        '''-1 to not delete'''
        try:
            if key==-1:
                key=self.get_used_capacity()
            if binary:
                self.at_cmd("CMGF=0")
            else:
                self.at_cmd("CMGF=1")
            data=self.at_cmd("CMGR="+str(key))
            message_data=data[1].split(',')
            message_text=data[2]
            if delete!=-1:
                self.at_cmd("CMGD="+str(delete))
            return{'status':message_data[0].replace('+CMGR:','').strip(), 'number':message_data[1],'date':message_data[3],'time':message_data[4],'text':message_text}
        except IndexError:
            return {'data':message_data,'text':message_text}
