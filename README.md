# pyutility

python 常用方法封装，新开发的爬虫建议使用 v1.1 分支中的版本，代码相对规范一些。

# install

下载源码，进入项目根目录，执行脚本：

``` shell
python install.py
```

# dependence

使用 pip 安装依赖模块

## common (必须)

* [lxml](https://pypi.python.org/pypi/lxml/3.4.4)
* requests
* pyinstaller

## image_util (可选)

* Pillow

## vcode (可选)

* [Pillow](https://pypi.python.org/pypi/Pillow/3.4.2)
* [tesseract](https://github.com/tesseract-ocr/tesseract/wiki)
* [pytesseract](https://pypi.python.org/pypi/pytesseract/0.1.6)

# uninstall

仅 Mac/Linux 可用

``` shell
cat install.txt | xargs rm -rf
```
