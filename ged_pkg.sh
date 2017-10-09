#!/bin/bash

#preconditions:
## Ubuntu Mate 16.04
## ros-kinetic-fulldesktop

##postconditions
##

#prj_root=/home/$USER/${pkg_name}
prj_root=.
pkg_name=ged
pkg_root=/opt/ros/${ROS_DISTRO}
pkg_files_lib="${pkg_name}_server.py  \
				${pkg_name}_client.py \
				ACB${pkg_name}/__init__.py"
#pkg_deps="genmsg std_msgs actionlib_msgs actionlib turtle_actionlib actionlib_tutorials" #indirectly depending on "all your body needs"
pkg_deps="message_generation message_runtime std_msgs actionlib_msgs actionlib turtle_actionlib actionlib_tutorials" #indirectly depending on "all your body needs"
#prj_root=/opt/ros/kinetic/local/$pkg_name
if [ "$1" = "" ];then 
	cat <<EOF
	sintaxis: $0 CMD
	where in (create_ws,create_pkg)

	pkg_name=$pkg_name
EOF
	exit 1
fi

set -x
if [ $1 = "create_ws" ];then 
	mkdir -p ${prj_root}/catkin_ws/src
	cd ${prj_root}/catkin_ws/src
	catkin_init_workspace
	cd ${prj_root}/catkin_ws
	catkin_make
	echo source ${prj_root}/catkin_ws/devel/setup.bash >>$HOME/.bashrc #TODO: cleanup after uninstall
	find ${prj_root}/catkin_ws
	set +x
fi	
	

if [ $1 = "remove_ws" ];then 
	rm -rf ${prj_root}/catkin_ws
	#TODO: clean .bashrc up after uninstall
	#TODO: clean ROS up after uninstall (?)
fi

if [ $1 = "remove_pkg" ];then 
	cmd="sudo rm -rf "
	${cmd} ${pkg_root}/share/${pkg_name}
	${cmd} ${pkg_root}/lib/${pkg_name}
	#TODO: clean .bashrc up after uninstall
	#TODO: further clean ROS up after uninstall (?)
fi

if [ $1 = "create_pkg" ];then 
	cd ${prj_root}/catkin_ws/src

	#TODO: globals for pkg data
	#TODO: format="2" (?)
	catkin_create_pkg \
		-D "${pkg_name}: Challenge " \
		-V 0.1.0 \
		-l GPLv3 \
		-a "Leandro Batlle" \
		-m "TBD" \
		--rosdistro ${ROS_DISTRO} \
		${pkg_name} \
		${pkg_deps} 

	exit
	mkdir ${prj_root}/catkin_ws/src/${pkg_name}/launch
	cd ${prj_root}/catkin_ws
	#TODO: global for path
	catkin_make \
		-DCMAKE_BUILD_TYPE=Release \
		${pkg_name}
	catkin_make install -DCMAKE_INSTALL_PREFIX=/opt/ros/${ROS_DISTRO}
	#TODO: proper installation of launchfiles through cmake files
	mkdir ${prj_root}/catkin_ws/install/share/${pkg_name}/launch/
	cp -av ${prj_root}/${pkg_name}.launch ${prj_root}/catkin_ws/install/share/${pkg_name}/launch/
	#TODO: test doesn't work: topic paths match..
	cp -av ${prj_root}/${pkg_name}-test.launch ${prj_root}/catkin_ws/install/share/${pkg_name}/launch/
	echo source ${prj_root}/catkin_ws/install/setup.bash >>$HOME/.bashrc #TODO: cleanup after uninstall
	
	#install lib files
	#mkdir -p ${prj_root}/catkin_ws/install/lib/${pkg_name}/ACB${pkg_name}
	#TODO: copy instead of hardlinking (for debugging sessions)
	#for mypath in ${pkg_files_lib}; do
	#	cp --link -v ${prj_root}/${mypath} ${prj_root}/catkin_ws/install/lib/${pkg_name}/${mypath}
	#	done
	set +x
fi

if [ $1 = "install_pkg" ];then 
	cd ${prj_root}/catkin_ws
	catkin_make \
		-DCMAKE_BUILD_TYPE=Release \
		${pkg_name}
	sudo chown $USER /opt/ros/${ROS_DISTRO}/share
	sudo chown $USER /opt/ros/${ROS_DISTRO}/lib
	catkin_make install -DCMAKE_INSTALL_PREFIX=/opt/ros/${ROS_DISTRO}
	# if [ $? -] #TODO: errorlevel...
	set +x
fi


if [ $1 = "save_ws" ];then 
	DEST=${prj_root}/backup
	mkdir -p ${DEST}
	#cd ${prj_root}/catkin_ws
	#cp -av src/${pkg_name}/CMakeLists.txt ${DEST}
	#cp -av src/${pkg_name}/package.xml  ${DEST}
	rsync -av --copy-links ${prj_root}/catkin_ws $DEST
	set +x
fi



if [ $1 = "install" ];then 
#	./ged_pkg.sh remove_ws  #deprecated
	./ged_pkg.sh remove_pkg
#	./ged_pkg.sh create_ws 
#	./ged_pkg.sh create_pkg 
	./ged_pkg.sh install_pkg
	cd catkin_ws
	catkin_make clean
	set +x
fi


if [ $1 = "start" ];then 
	cd ${prj_root}/WebSvr/web2py
	echo cd ${prj_root}/WebSvr/web2py
	echo starting webserver for Monitor and Operator interfaces
	python web2py.py -a ged -i 0.0.0.0 &
	echo starting ROS
	roslaunch ged ged.launch
	set +x
fi


if [ $1 = "placeholder" ];then 
	cd ${prj_root}/catkin_ws
	echo just a humble placeholder...
	set +x
fi



exit

#HELP pages

usage: catkin_create_pkg [-h] [--meta] [-s [SYS_DEPS [SYS_DEPS ...]]]
                         [-b [BOOST_COMPS [BOOST_COMPS ...]]] [-V PKG_VERSION]
                         [-D DESCRIPTION] [-l LICENSE] [-a AUTHOR]
                         [-m MAINTAINER] [--rosdistro ROSDISTRO]
                         name [dependencies [dependencies ...]]

Creates a new catkin package

positional arguments:
  name                  The name for the package
  dependencies          Catkin package Dependencies

optional arguments:
  -h, --help            show this help message and exit
  --meta                Creates meta-package files
  -s [SYS_DEPS [SYS_DEPS ...]], --sys-deps [SYS_DEPS [SYS_DEPS ...]]
                        System Dependencies
  -b [BOOST_COMPS [BOOST_COMPS ...]], --boost-comps [BOOST_COMPS [BOOST_COMPS ...]]
                        Boost Components
  -V PKG_VERSION, --pkg_version PKG_VERSION
                        Initial Package version
  -D DESCRIPTION, --description DESCRIPTION
                        Description
  -l LICENSE, --license LICENSE
                        Name for License, (e.g. BSD, MIT, GPLv3...)
  -a AUTHOR, --author AUTHOR
                        A single author, may be used multiple times
  -m MAINTAINER, --maintainer MAINTAINER
                        A single maintainer, may be used multiple times
  --rosdistro ROSDISTRO
                        The ROS distro (default: environment variable
                        ROS_DISTRO if defined)
