# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pakkanpdf']

package_data = \
{'': ['*']}

install_requires = \
['pdfminer.six[image]>=20220524,<20220525']

setup_kwargs = {
    'name': 'pakkanpdf',
    'version': '0.1.2',
    'description': 'pdf 内の text や image へのアクセスをコンテキストマネージャーを使ってシンプルに行える',
    'long_description': '# pakkan-pdf\n\nPDF 内の text や image へのアクセスをコンテキストマネージャーを使ってシンプルに行える。\n[pdfminer/pdfminer.six](https://github.com/pdfminer/pdfminer.six) の Wrapper ライブラリです。\n\n# install\n\n`pip install pakkanpdf`\n\n# 使い方\n\n- PdfExtractor の pdf_path に pdf のパスを与え、work_dir に存在するディレクトリを指定する\n  - work_dir に image を書き出すための一時ディレクトリが作成さえる\n- extractor.text を使うと、PDF の text を取得できる\n- extractor.image_file_paths を使うと、PDF の image (file path) を取得できる\n\n``` python3\nfrom pakkanpdf import PdfExtractor\n\ndef test_sample():\n    with PdfExtractor(pdf_path="data/example.pdf", work_dir="demo_work_dir") as extractor:\n        assert "これはサンプルのPDFです" in extractor.text\n        assert extractor.image_file_paths == ["demo_work_dir/work_images/X8.jpg"]\n\n```',
    'author': 'Niten Nashiki',
    'author_email': 'n.nashiki.work@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nnashiki/pakkan-pdf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
