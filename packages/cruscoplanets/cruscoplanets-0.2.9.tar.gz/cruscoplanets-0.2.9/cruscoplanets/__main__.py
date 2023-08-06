import os, sys
from . import cmdline


def main():

	libvipspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c_libraries", "vips-dev-w64-web-8.12.1", "vips-dev-8.12", "bin")
	sys.path.append(libvipspath)
	cmdline.main()
	
if __name__ == '__main__':
	main()
