"""Real HTTP checks against an isolated ephemeral server and database."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from legacy.server import make_server


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Path('var/tests').mkdir(parents=True,exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(dir='var/tests')
        cls.server=make_server(0,Path(cls.temp.name)/'http.sqlite3')
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()

    def request(self,path,body=None,cookie=None,origin=True,host=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=15)
        headers={}
        if cookie:headers['Cookie']=cookie
        if host:headers['Host']=host
        if body is not None:
            headers['Content-Type']='application/json'
            if origin:headers['Origin']=f'http://127.0.0.1:{self.server.server_port}'
        conn.request('GET' if body is None else 'POST',path,json.dumps(body) if body is not None else None,headers)
        response=conn.getresponse();status=response.status;hdr=dict(response.getheaders());raw=response.read();conn.close()
        return status,hdr,json.loads(raw) if hdr['Content-Type'].startswith('application/json') else raw

    def test_static_assets_and_headers(self):
        for path in ('/','/style.css','/app.js','/favicon.svg'):
            status,headers,_=self.request(path)
            self.assertEqual(status,200)
            self.assertIn('Content-Security-Policy',headers)
            self.assertEqual(headers['X-Content-Type-Options'],'nosniff')

    def test_private_files_never_served(self):
        for path in ('/legacy/server.py','/legacy/web/index.html','/var/chill.sqlite3','/../Answer%20V3.docx','/.env'):
            self.assertEqual(self.request(path)[0],404)

    def test_reject_cross_origin_and_host(self):
        self.assertEqual(self.request('/api/game',{'mode':'demo'},origin=False)[0],403)
        self.assertEqual(self.request('/api/bootstrap',host='evil.example')[0],403)

    def test_cookie_and_guest_isolation(self):
        _,headers,_=self.request('/api/bootstrap')
        cookie=headers['Set-Cookie'].split(';')[0]
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        self.assertIn('SameSite=Strict',headers['Set-Cookie'])
        status,_,game=self.request('/api/game',{'mode':'demo'},cookie)
        self.assertEqual(status,200)
        self.assertEqual(self.request('/api/game?id='+game['id'])[0],404)
        self.assertEqual(self.request('/api/game?id='+game['id'],cookie=cookie)[0],200)

    def test_http_learning_flow_and_export_gate(self):
        _,headers,_=self.request('/api/bootstrap');cookie=headers['Set-Cookie'].split(';')[0]
        _,_,game=self.request('/api/game',{'mode':'demo'},cookie)
        _,_,review=self.request('/api/review',{'id':game['id']},cookie)
        e=review['moments'][0];self.assertNotIn('analysis',e)
        _,_,export=self.request('/api/export',cookie=cookie)
        for r in export['data']:
            if r['kind']=='exercise':self.assertNotIn('analysis',r['data'])
        self.assertEqual(self.request('/api/attempt',{'id':e['id'],'move':'a2a7'},cookie)[0],400)
        _,_,e=self.request('/api/reflect',{'id':e['id'],'evaluation':'Có cơ hội','threat':'Xe','plan':'a2a7'},cookie)
        self.assertIn('explanation',e)
        _,_,e=self.request('/api/attempt',{'id':e['id'],'move':'a2a7'},cookie)
        self.assertTrue(e['complete'])
        _,_,d=self.request('/api/dashboard',cookie=cookie)
        self.assertEqual(d['total_attempts'],1)

    def test_invalid_request(self):
        self.assertEqual(self.request('/api/game',{'mode':'wrong'})[0],400)
        self.assertEqual(self.request('/api/game',[])[0],400)

    def test_missing_or_wrong_required_fields_are_bad_requests(self):
        for path in ('/api/move','/api/bot','/api/review','/api/draft','/api/reflect','/api/attempt','/api/hint','/api/feedback'):
            self.assertEqual(self.request(path,{})[0],400,path)
            self.assertEqual(self.request(path,{'id':[]})[0],400,path)

    def test_http_draft_resume_keeps_answer_locked(self):
        _,headers,_=self.request('/api/bootstrap');cookie=headers['Set-Cookie'].split(';')[0]
        _,_,e=self.request('/api/practice',{'skill':'material'},cookie)
        self.assertEqual(self.request('/api/draft',{'id':e['id'],'plan':'Nghĩ tiếp'},cookie)[0],200)
        self.assertEqual(self.request('/api/draft',{'id':e['id'],'plan':'Other'})[0],404)
        _,_,view=self.request('/api/exercise?id='+e['id'],cookie=cookie)
        self.assertEqual(view['draft']['plan'],'Nghĩ tiếp')
        self.assertNotIn('analysis',view)
        self.assertNotIn('explanation',view)
        _,_,dashboard=self.request('/api/dashboard',cookie=cookie)
        self.assertEqual(dashboard['pending'][0]['id'],e['id'])
        self.assertTrue(dashboard['pending'][0]['has_draft'])


if __name__=='__main__':unittest.main()
