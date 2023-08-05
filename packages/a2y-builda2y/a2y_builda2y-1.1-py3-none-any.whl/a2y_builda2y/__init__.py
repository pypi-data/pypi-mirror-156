from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
from os.path import splitext as _splitext
from os import unlink as _unlink, rmdir as _rmdir
from shutil import copyfile as _copy_file
import pathlib as _path
from sys import argv as _argv


def build_bin_pkg(ext_src_name, version, description='', install_requires=tuple(), data_files=tuple()):
	basic_name = _splitext(ext_src_name)[0]
	ext_name = 'a2y_%s' % basic_name
	src_name = ext_src_name
	ext = Extension(name=ext_name, sources=[src_name])
	pkg_name = ext_name
	md_name = 'README.md'

	with open(md_name, 'r', encoding='utf8') as fh:
		long_description = fh.read()

	setup(
		name=pkg_name,
		version=version,
		author='Yu Han',
		author_email='hanjunyu@163.com',
		description=description,
		license='Private',
		platforms=['Windows', 'Linux'],
		long_description=long_description,
		long_description_content_type='text/markdown',
		url='http://www.sorobust.com/a2y/%s.html' % basic_name,
		ext_modules=cythonize(ext),
		data_files=data_files,
		install_requires=install_requires,
		classifiers=[
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"License :: Free For Educational Use",
			"Programming Language :: Python :: 3.5",
			"Operating System :: Microsoft :: Windows :: Windows 10",
			"Operating System :: POSIX :: Linux",
		],
	)


def build_src_pkg(ext_org_name, version, description='', install_requires=tuple(), data_files=tuple()):
	ext_name = 'a2y_%s' % ext_org_name
	pkg_name = ext_name
	md_name = 'README.md'

	with open(md_name, 'r', encoding='utf8') as fh:
		long_description = fh.read()

	setup(
		name=pkg_name,
		version=version,
		author='Yu Han',
		author_email='hanjunyu@163.com',
		description=description,
		license='Private',
		platforms=['Windows', 'Linux'],
		long_description=long_description,
		long_description_content_type='text/markdown',
		url='http://www.sorobust.com/a2y/%s.html' % ext_org_name,
		packages=find_packages(),
		data_files=data_files,
		install_requires=list(install_requires),
		classifiers=[
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"License :: Free For Educational Use",
			"Programming Language :: Python :: 3.5",
			"Operating System :: Microsoft :: Windows :: Windows 10",
			"Operating System :: POSIX :: Linux",
		],
	)


def build_bin_as_src(ext_org_name, version, description='', install_requires=tuple(), data_files=tuple()):
	"""
	我们做的很多模块是以不开放源码的方式发布。但这样做也给我们自己调试代码带来了困难。为此，我们也为内部人员提供开放源码的包。
	为了方便构建这种既有二进制形式又有源码形式的包，创建了这个函数。
	请注意不要把源码包上传到公共包库。
	:param ext_org_name: 模块的源名。如果目标模块名是a2y_mew，那么这里应该传入“mew”。
	:param version: 模块的版本号。
	:param description: 模块描述。
	:param install_requires: 安装此模块时的依赖项。
	:param data_files: 其他需要与模块一起打包的文件列表。
	:return: None
	"""
	basic_name = _splitext(ext_org_name)[0]
	module_name = 'a2y_%s' % basic_name
	module_path = _path.Path(module_name)
	src_file = ext_org_name
	tgt_file = module_path / '__init__.py'
	fresh_dir = False
	fresh_file = False
	if not module_path.exists():
		module_path.mkdir()
		fresh_dir = True
	if not tgt_file.exists():
		_copy_file(src=src_file, dst=tgt_file)
		fresh_file = True

	build_src_pkg(basic_name, version, description, install_requires, data_files)

	if fresh_file:
		_unlink(tgt_file)
	if fresh_dir:
		_rmdir(module_path)


def build_bin_or_src_pkg(*args, **kwargs):
	if len(_argv) < 2:
		_argv.append('bdist_wheel')
	if _argv[1] == 'bdist_wheel':
		builder = build_bin_pkg
	elif _argv[1] == 'sdist_wheel':
		builder = build_bin_as_src
		_argv[1] = 'bdist_wheel'
	else:
		print('Unknown argument value.')
		print('Usage: python setup.py bdist_wheel|sdist_wheel')
		return

	builder(*args, **kwargs)
