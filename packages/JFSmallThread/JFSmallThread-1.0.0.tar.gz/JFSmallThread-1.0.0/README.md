# JFSmallThread

## 简易版并发请求库：支持http协议高并发发送，比 aiohttp和requests 更快。 设置tps，控制函数发送速度, 提高执行效率

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## Installation

```sh
pip install JFSmallThread

设置tps
tps_pool = TpsThreadPoolExecutor(tps=20)
    for i in range(100):
        # tps_pool.submit(f1, i)
        tps_pool.submit(test_by_nb_http_client)
    tps_pool.shutdown()
    
不设置
http_pool = ObjectPool(object_type=HttpOperator, object_pool_size=50,
                       object_init_kwargs=dict(host='xxxx', port=xxx),
                       max_idle_seconds=30)

thread_pool = BoundedThreadPoolExecutor(50)


def test_http_client():
    """
    type: typing.Union[HttpOperator,HTTPConnection]
    http对象池的请求速度暴击requests的session和直接requests.get
    """
    with http_pool.get() as conn:
        r1 = conn.speed_request()
        print(r1.text)
```

## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

[dill]: <https://github.com/joemccann/dillinger>

[git-repo-url]: <https://github.com/joemccann/dillinger.git>

[john gruber]: <http://daringfireball.net>

[df1]: <http://daringfireball.net/projects/markdown/>

[markdown-it]: <https://github.com/markdown-it/markdown-it>

[Ace Editor]: <http://ace.ajax.org>

[node.js]: <http://nodejs.org>

[Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>

[jQuery]: <http://jquery.com>

[@tjholowaychuk]: <http://twitter.com/tjholowaychuk>

[express]: <http://expressjs.com>

[AngularJS]: <http://angularjs.org>

[Gulp]: <http://gulpjs.com>

[PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>

[PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>

[PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>

[PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>

[PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>

[PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
