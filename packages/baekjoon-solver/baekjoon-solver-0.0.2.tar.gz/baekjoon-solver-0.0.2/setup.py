# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['baekjoon_solver']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4==4.11.1', 'colorama==0.4.5', 'httpx==0.23.0']

entry_points = \
{'console_scripts': ['solver = baekjoon_solver.main:run']}

setup_kwargs = {
    'name': 'baekjoon-solver',
    'version': '0.0.2',
    'description': 'baekjoon solver 문제 풀이',
    'long_description': '## baekjoon-solver\n\n### Installation\n```shell\n$ pip install baekjoon_solver\n```\n\n### Usage\n```shell\n$ solve <filename> -p <problem_id> # or\n$ solve <filename> # 문제 파일 가장 상단에 주석으로 문제번호 명시 (# <problem _id>)\n\n\n# ex)\n$ solve test.py -p 11403\n\n테스트 케이스 1\n============================= 통과 0.024250507354736328s =============================\n테스트 케이스 2\n============================= 통과 0.02342987060546875s =============================\n```\n',
    'author': 'Youngkwang Yang',
    'author_email': 'immutable000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/2ykwang/baekjoon-solver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
