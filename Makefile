# Should be changed to reflect where your vim installation is.
# Most likely ~/.vim/colors/
install_dir = ${VIMINSTALL}colors

default:
	python gen.py > colors/film_noir.vim

install: default
	cp colors/film_noir.vim "${install_dir}\film_noir.vim"
