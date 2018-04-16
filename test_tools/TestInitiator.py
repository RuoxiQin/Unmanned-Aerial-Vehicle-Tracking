#!/usr/bin/python
#-*-coding:utf-8-*-

from PlatForm import PlatForm
from ResultRecord import ResultRecord

class TestInitiator(object):
    def __init__(self,algorithem, setting):
        self.__plat = PlatForm(decide_algorithem = algorithem, **setting)
        self.__plat.test()

        return super(TestInitiator,self).__init__()

    def get_result(self):
        return self.__plat.get_result()
