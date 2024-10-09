#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import copy
import threading
from collections import OrderedDict


class DataConverter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            # 使用锁确保在多线程环境下只有一个线程能创建实例
            with cls._lock:
                if cls._instance is None:
                    # 使用 super 调用父类的 __new__ 方法创建实例
                    cls._instance = super().__new__(cls)
                    # 初始化线程局部变量用于存储缓存数据
                    cls._instance.local_cache = threading.local()
        return cls._instance

    def __generate_data_hash(self, data):
        """
        生成自定义哈希值，根据数据类型进行不同处理。

        :param data: 输入数据
        :return: 可哈希的值
        """
        try:
            if isinstance(data, dict):
                # 对于字典类型，递归调用生成每个值的哈希，并只对特定类型的值进行处理，然后排序
                immutable_items = [(k, self.__generate_data_hash(v)) for k, v in data.items() if isinstance(v, (int, str, float, tuple, frozenset, dict, list))]
                return tuple(sorted(immutable_items))
            elif isinstance(data, list):
                # 对于列表类型，递归调用生成每个元素的哈希，然后将结果转换为元组并计算哈希值
                return hash(tuple(map(self.__generate_data_hash, data)))
            else:
                # 对于其他类型，直接使用内置的哈希函数
                return hash(data)
        except Exception as e:
            raise ValueError(f"无法生成哈希值：{e}")

    def __perform_data_conversion(self, data):
        """
        执行数据转换。如果数据已经被处理过，则从缓存中获取结果，否则进行处理并缓存结果。

        :param data: 输入数据
        :return: 转换后的结果
        """
        try:
            data_custom_hash = self.__generate_data_hash(data)
            if not hasattr(self.local_cache, 'converted_data_cache'):
                self.local_cache.converted_data_cache = {}
            if data_custom_hash in self.local_cache.converted_data_cache:
                # 如果数据已在缓存中，直接返回缓存的副本
                return copy.copy(self.local_cache.converted_data_cache[data_custom_hash])
            result = self.__process_data(data)
            # 将处理后的结果存入缓存并返回副本
            self.local_cache.converted_data_cache[data_custom_hash] = copy.copy(result)
            return result
        except Exception as e:
            raise ValueError(f"数据转换失败：{e}")

    def __process_data(self, data):
        """
        根据数据类型选择相应的处理函数。

        :param data: 输入数据
        :return: 处理后的结果
        """
        try:
            if isinstance(data, dict):
                return self.__process_dict(data)
            elif isinstance(data, list):
                return self.__process_list(data)
            else:
                return data
        except Exception as e:
            raise ValueError(f"数据处理失败：{e}")

    def __process_dict(self, data):
        """
        处理字典类型的数据，将每个键值对进行处理后，转换为可通过点号访问的字典子类。

        :param data: 输入字典
        :return: 处理后的结果
        """
        try:
            # 递归处理字典中的每个值，并创建新字典
            new_dict = {k: self.__perform_data_conversion(v) for k, v in data.items()}
            return self.__create_accessible_dict(new_dict)
        except Exception as e:
            raise ValueError(f"字典处理失败：{e}")

    def __process_list(self, data):
        """
        处理列表类型的数据，对列表中的每个元素进行处理。

        :param data: 输入列表
        :return: 处理后的结果
        """
        try:
            # 递归处理列表中的每个元素
            return [self.__perform_data_conversion(item) for item in data]
        except Exception as e:
            raise ValueError(f"列表处理失败：{e}")

    def __create_accessible_dict(self, data):
        """
        创建可通过点号访问的字典子类。

        :param data: 输入字典
        :return: 可通过点号访问的字典子类实例
        """
        class DotAccessibleDictSubclass(OrderedDict):
            def __getattr__(self, item):
                try:
                    # 通过键获取值，如果键不存在则抛出属性错误
                    return self[item]
                except KeyError:
                    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

            def __setattr__(self, key, value):
                # 通过键设置值
                self[key] = value

            def __repr__(self):
                # 返回字典的字符串表示，递归处理值
                return str({k: self.__represent_value(v) for k, v in self.items()})

            def __represent_value(self, value):
                if hasattr(value, '_fields'):
                    # 如果值有_fields属性，递归处理每个字段的值并返回字典表示
                    fields = {field: self.__represent_value(getattr(value, field)) for field in value._fields}
                    return fields
                else:
                    # 否则直接返回值
                    return value

        return DotAccessibleDictSubclass(data)

    def perform_enhanced_conversion(self, data):
        """
        执行增强的数据转换方法，调用 __perform_data_conversion 进行转换。

        :param data: 输入数据
        :return: 转换后的结果
        """
        try:
            return self.__perform_data_conversion(data)
        except Exception as e:
            raise ValueError(f"增强转换失败：{e}")

    class LazyDataConverter:
        def __init__(self, data):
            """
            初始化方法，存储原始数据并将转换后的数据初始化为 None。

            :param data: 输入数据
            """
            self._original_data = data
            self._converted_data = None

        def __getattr__(self, item):
            """
            当访问一个不存在的属性时触发。如果转换后的数据尚未生成，则进行转换，
            然后通过属性访问获取转换后的数据的对应属性值。

            :param item: 要访问的属性名
            :return: 属性值
            """
            if self._converted_data is None:
                parent_converter = DataConverter()
                self._converted_data = parent_converter.perform_enhanced_conversion(self._original_data)
            return getattr(self._converted_data, item)

    def __process_large_data_generator(self, func):
        """
        处理大型数据的生成器装饰器。

        :param func: 要应用于每个数据项的函数
        :return: 包装后的生成器函数
        """

        def wrapper(data):
            """
            生成器函数，遍历输入数据并对每个数据项应用传入的函数。

            :param data: 输入数据列表
            :yield: 处理后的单个数据项
            """
            for item in data:
                yield func(item)

        return wrapper

    def __convert_data_item(self, item):
        """
        用于处理大型数据的单个数据项转换函数。

        :param item: 输入数据项
        :return: 转换后的结果
        """
        try:
            return self.__perform_data_conversion(item)
        except Exception as e:
            raise ValueError(f"大型数据项转换失败：{e}")

    def process_large_data(self, data):
        """
        处理大型数据的方法。

        此方法使用生成器装饰器来处理大型数据列表。首先，通过调用生成器装饰器函数
        self.__process_large_data_generator，并传入单个数据项转换函数self.__convert_data_item，
        得到一个装饰后的生成器函数。然后将输入数据data传入这个装饰后的生成器函数，
        最后将生成器转换为列表并返回。这样可以高效地处理大型数据，避免一次性将所有数据加载到内存中。

        :param data: 要处理的大型数据列表
        :return: 处理后的大型数据列表结果
        """
        try:
            return list(self.__process_large_data_generator(self.__convert_data_item)(data))
        except Exception as e:
            raise ValueError(f"大型数据处理失败：{e}")


converter = DataConverter()


if __name__ == "__main__":

    dict1={"test1":[{"content":"1","request":{"request_1":"5","request_2":""},"reponse":{"reponse_1":"","reponse_2":""}}],"test2":[{"content":"2","request":{"request_1":"","request_2":""},"reponse":{"reponse_1":"","reponse_2":""}}]}
    list1 = [{"content":"1","request":{"request_1":"2"},"reponse":{"reponse_1":"3"}},{"content":"2","request":{"request_1":"2"},"reponse":{"reponse_1":"2"}}]

    converted_dict1 = converter.perform_enhanced_conversion(dict1)
    converted_list1 = converter.perform_enhanced_conversion(list1)

    print(converted_list1[0].content)
    print(converted_list1[0].request)
    print(converted_list1[0].request.request_1)

    print(converted_dict1.test1[0].content)
    print(converted_dict1.test1[0].request)
    print(converted_dict1.test1[0].request.request_1)

    lazy_converter = converter.LazyDataConverter(dict1)
    print(lazy_converter.test1[0].content)

    converted_large_list = converter.process_large_data(list1)
    for item in converted_large_list:
        print(item.content)