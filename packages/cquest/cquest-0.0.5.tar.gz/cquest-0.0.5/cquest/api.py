import os.path

from cquest import root_dir
from cquest.composer import Composer
from cquest.utils import func_loop, timestamp


class Api(Composer):
    """
    用户使用该请求库的主要入口
    配置url.conf后,使用一个类继承Composer进行发起请求
    """

    def __init__(self):
        """
        self.proxies为设置全局代理,局部代理可以在main方法中直接赋值,不可使用self.proxies值
        self.proxies = {
            "http": "http://localhost:8888",
            "https": "http://localhost:8888",
        }
        """
        super(Api, self).__init__()
        self.configfile = os.path.join(root_dir, 'url.conf')
        # 断言失败后是否继续请求,默认为False,失败后停止执行
        self.is_continue = True

    @staticmethod
    def request_hook(r, *args, **kwargs):
        """
        请求钩子函数,可自定义名称
        """
        print(f'request_hook: {r}')

    @staticmethod
    def response_hook(r, *args, **kwargs):
        """
        返回钩子函数,可自定义名称
        """
        print(f'response_hook: {r}')

    @staticmethod
    def assertion_hook(r, *args, **kwargs):
        """
        断言钩子函数,可自定义名称
        """
        print(f'assertion_hook: {r}')

    @staticmethod
    def associated_hook(r, *args, **kwargs):
        """
        关联钩子函数,可自定义名称
        """
        print(f'associated_hook: {r}')

    @func_loop(2)
    def get_data(self):
        """
        必选步骤:1、4
        """
        # 1、需要请求的接口列表,使用接口配置文件的一级名称,执行时会按列表顺序执行请求
        names = ['random', 'all']
        # 2、对配置文件中的请求头添加数据,根据配置文件中变量$${name}插入数据
        tripartite = {'random': {'timestamp': timestamp()},
                      'all': {'timestamp': timestamp()}}
        # 3、发起请求时，设置不同阶段的钩子函数,可获得或修改钩子对象的值,共4种钩子
        hooks = {
            'register': {'request': self.request_hook, 'response': self.response_hook, 'assertion': self.assertion_hook,
                         'associated': self.associated_hook}}
        headers = {'Connection': 'keep-alive', 'Accept': 'application/json, text/plain, */*'}
        # 4、调用主方法发起请求，支持request原生参数
        self.main(names, tripartite=tripartite, hooks=hooks, headers=headers, proxies=self.proxies, timeout=5)


if __name__ == '__main__':
    api = Api()
    api.get_data()
