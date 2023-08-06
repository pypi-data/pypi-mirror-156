# -*- coding: UTF-8 -*-
# tcp 中继器

# https://tornado-zh-cn.readthedocs.io/zh_CN/latest/iostream.html
# https://www.cnblogs.com/cynchanpin/p/7157815.html
import tornado.ioloop
import tornado.iostream
import socket
import os

LOCAL_URI = ''
class RepeaterHandler(tornado.web.RequestHandler):
   def get(self):
       # redirect重定向 可以实现内部和外部跳转
       # 内部：self.redirect('/abc')
       self.redirect(LOCAL_URI, status=307)
       
   def post(self):
       # redirect重定向 可以实现内部和外部跳转
       # 内部：self.redirect('/abc')
       self.redirect(LOCAL_URI, status=307)

def Handle(config):
    global LOCAL_URI
    LOCAL_URI = config['local_uri']
    proxy_uri = os.path.join(r"/", config['base_uri'], config['proxy_uri'])
    print(config, LOCAL_URI, proxy_uri)
    return [
        (proxy_uri, RepeaterHandler),
        ]

# @tornado.web.asynchronous
# def connect(request):
#     '''
#     对于HTTPS连接。代理应当作为TCP中继
#     '''
#     def req_close(data):
#         if conn_stream.closed():
#             return
#         else:
#             conn_stream.write(data)

#     def write_to_server(data):
#         conn_stream.write(data)

#     def proxy_close(data):
#         if req_stream.closed():
#             return
#         else:
#             req_stream.close(data)

#     def write_to_client(data):
#         req_stream.write(data)

#     def on_connect():
#         '''
#         创建TCP中继的回调
#         '''
#         req_stream.read_until_close(req_close, write_to_server)
#         conn_stream.read_until_close(proxy_close, write_to_client)
#         req_stream.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

#     print('Starting Conntect to %s' % request.uri)
#     # 获取request的socket
#     req_stream = request.connection.stream

#     # 找到主机端口。一般为443
#     host, port = (None, 443)
#     netloc = request.uri.split(':')
#     if len(netloc) == 2:
#         host, port = netloc
#     elif len(netloc) == 1:
#         host = netloc[0]

#     # 创建iostream
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#     conn_stream = tornado.iostream.IOStream(s)
#     conn_stream.connect((host, port), on_connect)

# if __name__ == '__main__':
#     connect(request)
    
# def send_request():
#     stream.write(b"GET / HTTP/1.0\r\nHost: friendfeed.com\r\n\r\n")
#     stream.read_until(b"\r\n\r\n", on_headers)

# def on_headers(data):
#     headers = {}
#     for line in data.split(b"\r\n"):
#        parts = line.split(b":")
#        if len(parts) == 2:
#            headers[parts[0].strip()] = parts[1].strip()
#     stream.read_bytes(int(headers[b"Content-Length"]), on_body)

# def on_body(data):
#     print(data)
#     stream.close()
#     tornado.ioloop.IOLoop.current().stop()

# if __name__ == '__main__':
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#     stream = tornado.iostream.IOStream(s)
#     stream.connect(("www.baidu.com", 80), send_request)
#     tornado.ioloop.IOLoop.current().start()