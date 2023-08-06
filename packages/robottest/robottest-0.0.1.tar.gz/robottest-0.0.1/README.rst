RobotTest测试框架
=================

robottest 安装
==============

使用pip命令安装

.. code:: bash

   pip install robottest

使用文档
========

-  调用系统命令

.. code:: bash

   def test_robot_fix(robot_fix):
       output=robot_fix.cli.exec("dir")
       print(output)

发布记录
========

-  0.0.1 2022-06-27 robot_fix支持调用系统的命令

修改记录
========

-  0.0.1

   -  增加robot_fix，支持调用系统的命令
