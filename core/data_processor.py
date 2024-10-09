#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import json
import codecs
import inspect
from core.data_converter import converter

# 定义一个命名数据列表类，继承自内置的列表类型
class NamedDataList(list):
    def __init__(self, name, *args):
        # 调用父类（list）的初始化方法，初始化列表内容
        super(NamedDataList, self).__init__(args)
        # 检查名称是否为字符串类型，若不是则抛出异常
        if not isinstance(name, str):
            raise ValueError("Name must be a string.")
        # 存储名称属性
        self.name = name

    def __str__(self):
        # 返回一个格式化的字符串，描述该对象的名称和列表内容
        return f"NamedDataList(Name={self.name}, Values={super().__str__()})"

    def length(self):
        # 返回列表的长度
        return len(self)

    def contains(self, element):
        # 检查列表是否包含指定元素
        return element in self

# 定义一个命名数据字典类，继承自内置的字典类型
class NamedDataDict(dict):
    def __init__(self, name, **kwargs):
        # 调用父类（dict）的初始化方法，初始化字典内容
        super(NamedDataDict, self).__init__(kwargs)
        # 检查名称是否为字符串类型，若不是则抛出异常
        if not isinstance(name, str):
            raise ValueError("Name must be a string.")
        # 存储名称属性
        self.name = name

    def __str__(self):
        # 返回一个格式化的字符串，描述该对象的名称和字典内容
        return f"NamedDataDict(Name={self.name}, Values={super().__str__()})"

    def length(self):
        # 返回字典的长度
        return len(self)

    def contains(self, key):
        # 检查字典是否包含指定键
        return key in self

def resolve_relative_path(relative_path, reference_path=None):
    """
    此函数用于将相对路径转换为绝对路径。
    如果未提供参考路径，则默认使用当前脚本所在目录作为参考路径。

    :param relative_path: 相对路径
    :param reference_path: 参考路径，默认为 None
    :return: 绝对路径
    """
    if reference_path is None:
        reference_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(reference_path, relative_path)

def process_file_data(file_path):
    """
    此函数用于读取指定文件路径的文件内容，并解析为 JSON 格式的数据返回。
    如果文件不存在，则抛出 FileNotFoundError 异常。

    :param file_path: 文件路径
    :return: JSON 格式的数据
    """
    if not os.path.isabs(file_path):
        file_path = resolve_relative_path(file_path)
    if not os.path.exists(file_path):
        print(file_path)
        raise FileNotFoundError(f"File not found: {file_path}")
    with codecs.open(file_path, 'r', 'utf-8') as f:
        return json.load(f)

def handle_json_data(arg=None):
    """
    此装饰器用于处理带有 JSON 数据的类。
    它会遍历类的属性，如果属性有 %file_path 标记，
    则读取对应文件路径的 JSON 数据，并将其存储在属性的 file_data 中，
    然后从类中删除该属性。

    :param arg: 可以是一个类，也可以不传参数，作为装饰器工厂函数使用
    :return: 装饰后的类
    """
    def wrapper(cls):
        for name, func in list(cls.__dict__.items()):
            if hasattr(func, '%file_path'):
                file_attr = getattr(func, '%file_path')
                data = process_file_data(file_attr)
                if data is not None:
                    setattr(func, 'file_data', data)
                delattr(cls, name)
        return cls
    return wrapper(arg) if inspect.isclass(arg) else wrapper

def file_data_list(file_path):
    """
    此装饰器用于处理文件中的列表数据。
    它会读取指定文件路径的文件内容，如果是列表数据，
    则创建一个 NamedDataList 对象，并将其作为参数传递给被装饰的函数。

    :param file_path: 文件路径
    :return: 装饰后的函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            resolved_path = resolve_relative_path(file_path)
            data = process_file_data(resolved_path)
            if isinstance(data, list):
                named_data = NamedDataList(resolved_path, *data)
                return func(*args, named_list_data=named_data, **kwargs)
            else:
                raise ValueError(f"Data from file {file_path} is not a list.")
        return wrapper
    return decorator

def file_data_dict(file_path):
    """
    此装饰器用于处理文件中的字典数据。
    它会读取指定文件路径的文件内容，如果是字典数据，
    则创建一个 NamedDataDict 对象，并将其作为参数传递给被装饰的函数。

    :param file_path: 文件路径
    :return: 装饰后的函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            resolved_path = resolve_relative_path(file_path)
            data = process_file_data(resolved_path)
            if isinstance(data, dict):
                named_data = NamedDataDict(resolved_path, **data)
                return func(*args, named_dict_data=named_data, **kwargs)
            else:
                raise ValueError(f"Data from file {file_path} is not a dict.")
        return wrapper
    return decorator

def request_data(dict_data):
    """
    此装饰器用于从给定的字典数据中获取被装饰函数名称对应的字典项中的'request'值，并将其作为参数传递给被装饰的函数。

    :param dict_data: 包含函数名称与相关数据的字典
    :return: 装饰后的函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            value = dict_data.get(func.__name__).get('request')
            return func(value, *args, **kwargs)
        return wrapper
    return decorator

def expect_response(dict_data):
    """
    此装饰器用于从给定的字典数据中获取被装饰函数名称对应的字典项中的'response'值，并将其作为参数传递给被装饰的函数。

    :param dict_data: 包含函数名称与相关数据的字典
    :return: 装饰后的函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            value = dict_data.get(func.__name__).get('response')
            return func(value, *args, **kwargs)
        return wrapper
    return decorator

def detail_content(dict_data):
    """
    此装饰器用于从给定的字典数据中获取被装饰函数名称对应的字典项中的'content'值，并将其作为参数传递给被装饰的函数。

    :param dict_data: 包含函数名称与相关数据的字典
    :return: 装饰后的函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            value = dict_data.get(func.__name__).get('content')
            return func(value, *args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
# 使用装饰器处理类，使其能够处理 JSON 数据。
    @handle_json_data
    class MyTestClass:
        # 使用装饰器处理方法，使其能够接收来自指定文件的列表数据。
        @file_data_list(r'testcase\data\DemoAPI1.json')
        def test_method_with_list(self, named_list_data):
            return converter.perform_enhanced_conversion(list(named_list_data))

        # 使用装饰器处理方法，使其能够接收来自指定文件的字典数据。
        @file_data_dict(r'testcase\data\DemoAPI2.json')
        def test_method_with_dict(self, named_dict_data):
            return converter.perform_enhanced_conversion(dict(named_dict_data))


    test_instance = MyTestClass()
    list_accessor = test_instance.test_method_with_list()
    dict_accessor = test_instance.test_method_with_dict()

    print(list_accessor[0].content)
    print(f"-" * 50)
    print(dict_accessor.testapi1[0].request)