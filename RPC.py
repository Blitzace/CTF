'''
Created on May 20, 2012

@author: Blitzace
'''
'''
Created on May 12, 2012

@author: Blitzace
'''

if __name__ == '__main__':
    pass

from SocketServer import ThreadingMixIn 
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES
from Crypto import Random
from Crypto.Util import number
import cPickle, sqlite3, os

class voting_BS:
    
    print '''    Welcome to the central tabulation facility server!
    -----------------------------------------------------------
    -----------------------------------------------------------
    ===========================================================
    '''
    path = 'vote_tally.db'
    if not os.path.exists(path):
        #create new DB, create table stocks
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.text_factory = str
        c = conn.cursor()
        c.execute('CREATE TABLE votes (ID text, vote text)')
        c.execute('CREATE TABLE voters (ID text, SSN text, name text)')
        conn.commit()
    
    else:
        #use existing DB
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.text_factory = str
        c = conn.cursor()
        
    msgs = []
    bfs = {}
    rng = Random.new().read
    CTF_key = RSA.generate(1024, rng)
    msg_no=0
    finished = 1
    voter_list = []
    PADDING = '{'
    SSN = '0'
    
    def get_publickey(self):
        return cPickle.dumps(self.CTF_key.publickey())
        
    def send_messages(self, m_list):
        self.msgs = cPickle.loads(m_list)
        n = 0
        req_msg = []
        rnd = number.getRandomInteger(5, self.rng)
        rnd = rnd%9
        self.msg_no = rnd
        while n<10:
            if (n != rnd):
                req_msg.append(n)
            n = n+1
        return req_msg
             
    def send_bfs(self, bf_dict, ID):
        count = 0
        self.c.execute('SELECT SSN FROM voters WHERE ID=?', (ID,))
        for row in self.c:
            SSN = row[0]
            count = count + 1
        print self.SSN
        if(count>0):
            self.SSN = SSN
        else:
            return cPickle.dumps('INVALID MSG')
        obj = DES.new(SSN, DES.MODE_ECB)
        self.bfs = bf_dict
        for i in self.bfs.keys():
            m1 = obj.decrypt(self.msgs[int(i)][0]).rstrip(self.PADDING)
            m2 = obj.decrypt(self.msgs[int(i)][1]).rstrip(self.PADDING)
            Message = (self.CTF_key.encrypt(self.CTF_key.unblind(self.CTF_key.decrypt(m1), bf_dict[i]), 5)[0], self.CTF_key.encrypt(self.CTF_key.unblind(self.CTF_key.decrypt(m2), bf_dict[i]), 5)[0])
            #check if msg ID is already stored in DB
            ID1 = Message[0].split("|")[0]
            ID2 = Message[1].split("|")[0]
            self.c.execute('SELECT vote FROM votes WHERE ID=?', (ID1 or ID2,))
            for row in self.c:
                return cPickle.dumps('ID EXISTS')
            if(Message[0].split("|")[0] == Message[1].split("|")[0] and Message[0].split("|")[1] == "Yes" and Message[1].split("|")[1] == "No"):
                pass
            else:
                return cPickle.dumps('INVALID MSG')
        m1 = obj.decrypt(self.msgs[self.msg_no][0]).rstrip(self.PADDING)
        m2 = obj.decrypt(self.msgs[self.msg_no][1]).rstrip(self.PADDING)
        signed_message = (self.CTF_key.decrypt(m1), self.CTF_key.decrypt(m2))
        return cPickle.dumps(signed_message)
    
    def send_vote(self, vote):
        exists = 0
        vote = cPickle.loads(vote)
        plain_vote = self.CTF_key.encrypt(vote, 5)[0]
        [ID, v] = plain_vote.split('|')
        self.c.execute('SELECT vote FROM votes WHERE ID=?', (ID,))
        for row in self.c:
            exists = 1
        
        if(exists != 1):
            self.c.execute('INSERT INTO votes VALUES(?, ?)', (ID, v))
            self.conn.commit()
            print 'Vote DB Updated: ' + plain_vote
            return 1
        else:
            return 0
        
    def ABC(self):
        if(self.finished == 1):
            self.c.execute('SELECT ID, vote FROM votes')
            for row in self.c:
                self.voter_list.append((row[0], row[1]))
            return self.voter_list
        else:
            return 0
            
        
    
        
        
class ForkingServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

serveraddr = (('localhost', 8000))
srvr = ForkingServer(serveraddr, SimpleXMLRPCRequestHandler)
srvr.register_instance(voting_BS())
srvr.serve_forever()


