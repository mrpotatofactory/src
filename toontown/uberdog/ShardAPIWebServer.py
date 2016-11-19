from direct.stdpy.threading import Lock
from direct.stdpy.thread import start_new_thread
from BaseHTTPServer import *
import urllib
import json

import ShardAPIManagerUD

def _encode(d):
    return json.dumps(d, sort_keys=True, indent=4,
                      separators=(',', ': '),
                      encoding='latin-1')

class ShardAPIRequestHandler(BaseHTTPRequestHandler):
    mgr = None
    
    def do_GET(self):
        with Lock():
            self.process()
            
    def process(self):
        path = self.path
        params = {}
        if '?' in path:
            path, paramdata = path.split('?', 1)
            
            for param in paramdata.split('&'):
                if not param.strip():
                    continue
                    
                if '=' not in param:
                    self.send_error(500, 'Internal server error')
                    return
                    
                param, value = param.split('=', 1)
                params[param] = urllib.unquote(value)
            
        path = [p.strip() for p in path.split('/') if p.strip()]
        if len(path) != 1:
            self.send_error(404, 'Resource not found')
            return
            
        ret = self.handle_API(path[0].lower(), params)
        if ret:
            self.wfile.write(ret)
            
        else:
            self.send_error(404, 'Resource not found')
        
    def handle_API(self, request, params):
        if request == 'shards':
            return _encode({'error': None, 'shards': self.mgr.shards.keys()})
            
        elif request == 'invasions':
            lang = params.get('lang', 'en')
            ShardAPIManagerUD.setLanguageContext(lang)
        
            invasions = self.mgr.listInvasions()
            if not invasions:
                ret = {'error': 'No shards'}
            
            else:
                ret = {'error': None}
                ret.update(invasions)
            
            return _encode(ret)
            
        elif request == 'buildings':
            return self.findBuildings(params)
            
    def findBuildings(self, params):
        '''
        Possible params:
            lang - Building title language [en,pt] (default: en)
        '''
        
        lang = params.get('lang', 'en')
        ShardAPIManagerUD.setLanguageContext(lang)
            
        ret = {'error': None}
        for shardId, shard in self.mgr.shards.items():
            s = {}
            
            for hoodId, hood in shard.hoods.items():
                for streetId, street in hood.streets.items():
                    for blockNumber, block in street.blocks.items():                        
                        s.setdefault(hoodId, {}).setdefault(streetId, {})[blockNumber] = block.writeDict()
            
            data = {'districtName': shard.name, 'buildings': s}
            ret.update({shardId: data})
            
        return _encode(ret)
        
def start(mgr):
    ShardAPIRequestHandler.mgr = mgr
    httpd = HTTPServer(('', 19200), ShardAPIRequestHandler)
    start_new_thread(httpd.serve_forever, ())
    return httpd
    