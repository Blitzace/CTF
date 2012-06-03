# Create your views here.

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
from django.views.decorators.csrf import csrf_exempt
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from SocketServer import ThreadingMixIn 
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES
from Crypto import Random
from Crypto.Util import number
import cPickle, sqlite3, os
from vrecords.models import Voter, Choice
from django.shortcuts import render_to_response
from matplotlib.backends.backend_agg import FigureCanvasAgg
from pylab import figure, axes, pie, title
import matplotlib.pyplot
from django.core.cache import cache


dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None)

@csrf_exempt
def rpc_handler(request):
        """
        the actual handler:
        if you setup your urls.py properly, all calls to the xml-rpc service
        should be routed through here.
        If post data is defined, it assumes it's XML-RPC and tries to process as such
        Empty post assumes you're viewing from a browser and tells you about the service.
        """

        if len(request.POST):
                response = HttpResponse(mimetype="application/xml")
                response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
        else:
                response = HttpResponse()
                response.write("<b>This is an XML-RPC Service.</b><br>")
                response.write("You need to invoke it using an XML-RPC Client!<br>")
                response.write("The following methods are available:<ul>")
                methods = dispatcher.system_listMethods()

                for method in methods:
                        # right now, my version of SimpleXMLRPCDispatcher always
                        # returns "signatures not supported"... :(
                        # but, in an ideal world it will tell users what args are expected
                        sig = dispatcher.system_methodSignature(method)

                        # this just reads your docblock, so fill it in!
                        help =  dispatcher.system_methodHelp(method)

                        response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help))

                response.write("</ul>")
                response.write('<a href="http://www.djangoproject.com/"> <img src="http://media.djangoproject.com/img/badges/djangomade124x25_grey.gif" border="0" alt="Made with Django." title="Made with Django."></a>')

        response['Content-length'] = str(len(response.content))
        return response
    
    
class voting_BS:
    
    print '''    Welcome to the central tabulation facility server!
    -----------------------------------------------------------
    -----------------------------------------------------------
    ===========================================================
    '''

        
    msgs = []
    bfs = {}
    rng = Random.new().read
    CTF_key = RSA.generate(1024, rng)
    msg_no=0
    finished = 1
    voter_list = []
    PADDING = '{'
    
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
        test = ""
        try:
            v = Voter.objects.get(pk=ID)
        except:
            return cPickle.dumps('INVALID ENTRY')

        if(v.get_status() == "1"):
            SSN = v.get_ssn()
        else:
            return cPickle.dumps('VOTE REP')
        obj = DES.new(SSN, DES.MODE_ECB)
        self.bfs = bf_dict
        for i in self.bfs.keys():
            m1 = obj.decrypt(self.msgs[int(i)][0]).rstrip(self.PADDING)
            m2 = obj.decrypt(self.msgs[int(i)][1]).rstrip(self.PADDING)
            Message = (self.CTF_key.encrypt(self.CTF_key.unblind(self.CTF_key.decrypt(m1), bf_dict[i]), 5)[0], self.CTF_key.encrypt(self.CTF_key.unblind(self.CTF_key.decrypt(m2), bf_dict[i]), 5)[0])
            #check if msg ID is already stored in DB
            ID1 = Message[0].split("|")[0]
            ID2 = Message[1].split("|")[0]
            #self.c.execute('SELECT vote FROM votes WHERE ID=?', (ID1 or ID2,))
            #for row in self.c:
            #    return cPickle.dumps('ID EXISTS')
            if(Message[0].split("|")[0] == Message[1].split("|")[0] and Message[0].split("|")[1] == "Yes" and Message[1].split("|")[1] == "No"):
                pass
            else:
                return cPickle.dumps('INVALID MSG')

        m1 = obj.decrypt(self.msgs[self.msg_no][0]).rstrip(self.PADDING)
        m2 = obj.decrypt(self.msgs[self.msg_no][1]).rstrip(self.PADDING)
        v.status = "2"
        v.save()
        signed_message = (self.CTF_key.decrypt(m1), self.CTF_key.decrypt(m2))
        return cPickle.dumps(signed_message)
    
    def send_vote(self, vote):
        exists = 0
        vote = cPickle.loads(vote)
        plain_vote = self.CTF_key.encrypt(vote, 5)[0]
        [ID, v] = plain_vote.split('|')
        #self.c.execute('SELECT vote FROM votes WHERE ID=?', (ID,))
        #for row in self.c:
        #    exists = 1
        
        if(exists != 1):
            #self.c.execute('INSERT INTO votes VALUES(?, ?)', (ID, v))
            #self.conn.commit()
            tmp = ID
            if(v == "Yes"):
                tmp2 = "1"
            else:
                tmp2 = "2"
            c = Choice(US = tmp, votes = tmp2)
            c.save()
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
            
        
        
dispatcher.register_instance(voting_BS())

def results(request):
    cache._cache.clear()
    results_list = Choice.objects.all()
    return render_to_response('results.html', {'results_list': results_list})

def showResults(request):
    Y_tally = 0
    N_tally = 0
    results_list = Choice.objects.all()
    
    for object in results_list:
        if object.votes == '1':
            Y_tally = Y_tally + 1
        else:
            N_tally = N_tally + 1
    

    # make a square figure and axes
    f = figure(figsize=(6,6))
    ax = axes([0.1, 0.1, 0.8, 0.8])
    #labels = 'Yes', 'No'
    labels = 'Yes', 'No'
    fracs = [Y_tally,N_tally]
    explode=(0, 0)
    pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
    title('Election Results', bbox={'facecolor':'0.8', 'pad':5})
    canvas = FigureCanvasAgg(f)    
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    matplotlib.pyplot.close(f)
    f.clear()
    return response

