from setuptools import setup, find_packages
# setup(
#     name='global_star',  # 包的名称
#     version='1.0',  # 版本号
#     packages=find_packages(),  # 动态获取packages
#     # description="leeoo package",
#     author='派森',
#     author_email='wangshc1@163.com',
#     url="https://gitee.com/wang-shaocong-123/base_python_tools",
# )
# setup(
#     name='global_star',# 需要打包的名字,即本模块要发布的名字
#     version='v1.0',#版本
#     packages=find_packages(),
#     description='A  module for test', # 简要描述
#     # py_modules=['mySelfSum'],   #  需要打包的模块
#     author='派森', # 作者名
#     author_email='vzhyu@foxmail.com',   # 作者邮件
#     url='https://gitee.com/wang-shaocong-123/base_python_tools', # 项目地址,一般是代码托管的网站
#     # requires=['requests','urllib3'], # 依赖包,如果没有,可以不要
#     # license='MIT'
# )
setup(
    # 指定项目名称，我们在后期打包时，这就是打包的包名称，当然打包时的名称可能还会包含下面的版本号哟~
    name='global_star',
    # 指定版本号
    version='0.1.2',
    # 这是对当前项目的一个描述
    description='Python automatic operation and maintenance platform',
    # 作者是谁，指的是此项目开发的人，这里就写你自己的名字即可
    author='yinzhengjie',
    # 作者的邮箱
    author_email='y1053419035@qq.com',
    # 写上项目的地址，比如你开源的地址开源写博客地址，也开源写GitHub地址，自定义的官网地址等等。
    url='https://www.cnblogs.com/yinzhengjie/p/14124623.html',
    # 指定包名，即你需要打包的包名称，要实际在你本地存在哟，它会将指定包名下的所有"*.py"文件进行打包哟，但不会递归去拷贝所有的子包内容。
    # 综上所述，我们如果想要把一个包的所有"*.py"文件进行打包，应该在packages列表写下所有包的层级关系哟~这样就开源将指定包路径的所有".py"文件进行打包!
    packages=['global_star', "global_star.pkg"],
)