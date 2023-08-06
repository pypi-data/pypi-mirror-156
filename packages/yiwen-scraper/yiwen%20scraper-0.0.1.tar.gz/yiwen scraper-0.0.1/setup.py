from setuptools import setup, find_packages
 
classifiers = [
  'Intended Audience :: Education',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='yiwen scraper',
  version='0.0.1',
  description='some web scraping tool for Weibo',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Yiwen Li',
  author_email='liyiwen_2311@163.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='web scraper', 
  packages=find_packages(),
  install_requires=[''] 
)
