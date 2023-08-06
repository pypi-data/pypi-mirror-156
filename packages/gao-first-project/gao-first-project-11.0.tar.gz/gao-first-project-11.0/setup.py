#coding:UTF-8
from setuptools import setup,find_packages
setup(
	name="gao-first-project",
	version="11.0",
	author="高子敬",
	url="http://www.hzyrun.com",
	packages=find_packages("src"),#src就是模块保存地
	package_dir={"":"src"},#打包的目录
	package_data={
		#任何包中含有.txt文件，都包含它
		"":["*.txt","*.info","*.properties","*.py"],
		#包含demo包data文件夹中的*.data文件
		"":["data/*.*"],
	},
	exclude=["*.test","*.test.*","test.*","test"] #取消所有测试包

)