import re
import subprocess
import allure

class CliOutput(object):
    def __init__(self):
        self.__output=""
        self.__code=None

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self,out):
        self.__output=out

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self,exec_code):
        self.__code=exec_code

    def __str__(self):
        return self.__output


class Cli(object):

    def __init__(self):
        pass

    def exec(self,cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = ""
        for line in p.stdout.readlines():
            line = line.decode("gbk")
            out += line + "\n"
        code=p.returncode
        p.kill()
        allure.attach(out+"\n命令返回码："+str(code), cmd, allure.attachment_type.TEXT)
        output=CliOutput()
        output.output=out
        output.code=code
        return output