import tornado.ioloop
import tornado.web

def Serving(port, handlers):
    for h in handlers:
        print(h[0])
    application = tornado.web.Application(handlers)
    application.listen(port)
    # 二级域名
    # application.add_handlers(r"www\.myhost\.com", [
    #     (r"/article/([0-9]+)", ArticleHandler),
    # ])
    tornado.ioloop.IOLoop.current().start()