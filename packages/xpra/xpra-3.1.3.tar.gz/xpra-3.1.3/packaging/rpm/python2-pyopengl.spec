# Remove private provides from .so files in the python_sitearch directory
%global __provides_exclude_from ^%{python2_sitearch}/.*\\.so$
%{!?__python2: %define __python2 python2}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_version: %global python2_version %(%{__python2} -c "import sys; sys.stdout.write(sys.version[:3])")}
%define _disable_source_fetch 0

#this spec file is for both Fedora and CentOS
%global srcname PyOpenGL

Name:           python2-pyopengl
Version:        3.1.5
Release:        1xpra1%{?dist}
Summary:        Python bindings for OpenGL
License:        BSD
URL:            http://pyopengl.sourceforge.net/
Source0:        https://files.pythonhosted.org/packages/b8/73/31c8177f3d236e9a5424f7267659c70ccea604dab0585bfcd55828397746/%{srcname}-%{version}.tar.gz
Source1:        https://files.pythonhosted.org/packages/a2/3c/f42a62b7784c04b20f8b88d6c8ad04f4f20b0767b721102418aad94d8389/%{srcname}-accelerate-%{version}.tar.gz

Requires:       freeglut
Obsoletes:      python-pyopengl < %{version}-%{release}
Provides:       python-pyopengl = %{version}-%{release}
Obsoletes:      pyopengl < %{version}-%{release}
Provides:       pyopengl = %{version}-%{release}
Conflicts:		pyopengl < %{version}-%{release}
Obsoletes:      PyOpenGL < %{version}-%{release}
Provides:       PyOpenGL = %{version}-%{release}
Conflicts:		PyOpenGL < %{version}-%{release}
#Fedora broke our xpra repository :(
Obsoletes:      PyOpenGL-accelerate < %{version}-%{release}
Provides:       PyOpenGL-accelerate = %{version}-%{release}
Conflicts:		PyOpenGL-accelerate < %{version}-%{release}

%if 0%{?fedora}%{?el8}
%global __provides_exclude_from ^(%{python2_sitearch})/.*\\.so$
Requires:       python2-numpy
BuildRequires:  python2-setuptools
BuildRequires:  python2-devel
%else
Requires:       numpy
BuildRequires:  python-setuptools
BuildRequires:  python-devel
%endif

%description
PyOpenGL is the cross platform Python binding to OpenGL and related APIs. It
includes support for OpenGL v1.1, GLU, GLUT v3.7, GLE 3 and WGL 4. It also
includes support for dozens of extensions (where supported in the underlying
implementation).

PyOpenGL is inter-operable with a large number of external GUI libraries
for Python including (Tkinter, wxPython, FxPy, PyGame, and Qt).

%package -n     python2-pyopengl-tk
Summary:        %{srcname} Python 2.x Tk widget
BuildArch:      noarch
Requires:       python2-pyopengl = %{version}-%{release}
Requires:       tkinter
Obsoletes:      PyOpenGL-Tk < 3.1.2
Provides:       PyOpenGL-Tk = %{version}-%{release}
Obsoletes:      python-pyopengl-tk < 3.1.2
Provides:       python-pyopengl-tk = %{version}-%{release}

%description -n python2-pyopengl-tk
%{srcname} Togl (Tk OpenGL widget) 1.6 support for Python 2.x.

%prep
sha256=`sha256sum %{SOURCE0} | awk '{print $1}'`
if [ "${sha256}" != "4107ba0d0390da5766a08c242cf0cf3404c377ed293c5f6d701e457c57ba3424" ]; then
	echo "invalid checksum for %{SOURCE0}"
	exit 1
fi
sha256=`sha256sum %{SOURCE1} | awk '{print $1}'`
if [ "${sha256}" != "12e5518b0216a478527c7ce5ddce623c3d0517adeb87226da767772e8b7f2f06" ]; then
	echo "invalid checksum for %{SOURCE1}"
	exit 1
fi
%setup -q -c -n %{srcname}-%{version} -T -a0 -a1
rm %{srcname}-%{version}/OpenGL/EGL/debug.py
rm %{srcname}-%{version}/tests/osdemo.py


%build
for dir in %{srcname}-%{version} %{srcname}-accelerate-%{version} ; do
    pushd $dir
	%{__python2} setup.py build
    popd
done


%install
for dir in %{srcname}-%{version} %{srcname}-accelerate-%{version} ; do
    pushd $dir
	%{__python2} setup.py install -O1 --skip-build --root %{buildroot}
    popd
done

# Fix up perms on compiled object files
find %{buildroot}%{python2_sitearch}/OpenGL_accelerate/ -name *.so -exec chmod 755 '{}' \;

%files
%{python2_sitelib}/%{srcname}-%{version}-py%{python2_version}.egg-info
%{python2_sitelib}/OpenGL/
%exclude %{python2_sitelib}/OpenGL/Tk
%{python2_sitearch}/OpenGL_accelerate/
%{python2_sitearch}/%{srcname}_accelerate-%{version}-py%{python2_version}.egg-info/

%files -n python2-pyopengl-tk
%{python2_sitelib}/OpenGL/Tk

%changelog
* Wed Jan 22 2020 Antoine Martin <antoine@xpra.org> - 3.1.5-1xpra1
- new upstream release

* Wed Dec 04 2019 Antoine Martin <antoine@xpra.org> - 3.1.4-1xpra1
- new upstream release

* Mon Nov 25 2019 Antoine Martin <antoine@xpra.org> - 3.1.3rc1-1xpra1
- new upstream pre-release

* Tue Jul 03 2018 Antoine Martin <antoine@xpra.org> - 3.1.1a1-10xpra1
- try harder to prevent rpm db conflicts

* Thu Dec 07 2017 Antoine Martin <antoine@xpra.org> - 3.1.1a1-9xpra1
- remove opensuse bitrot

* Thu Jul 13 2017 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.2xpra4
- also obsolete / provide "python-opengl" package name

* Tue Jan 10 2017 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.1xpra4
- also use "python2-opengl" package name on CentOS

* Fri Aug 05 2016 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.1xpra3
- Fedora 23 does not have the python2 renamed packages yet
- only opensuse calls numpy python-numpy

* Mon Aug 01 2016 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.1xpra2
- and again

* Mon Aug 01 2016 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.xpra2
- Try harder to force centos to behave, override more versions too

* Thu Jul 28 2016 Antoine Martin <antoine@xpra.org> - 3.1.1a1-4.xpra1
- Try to ensure this updates the Fedora upstream package

* Mon Jul 18 2016 Antoine Martin <antoine@xpra.org> - 3.1.1a1r2-1
- Fix upgrade path for PyOpenGL_accelerate

* Sat Nov 28 2015 Antoine Martin <antoine@xpra.org> 3.1.1a1r1-1
- Force bump to ensure this supercedes the previous "final" builds

* Fri Nov 13 2015 Antoine Martin <antoine@xpra.org> 3.1.1a1-2
- Force rebuild with version lockstep change

* Sun Jul 12 2015 Antoine Martin <antoine@xpra.org> 3.1.1a1-1
- Force rebuild to workaround breakage caused by Fedora packaging differences
- Use new alpha build (no issues found so far)

* Wed Sep 17 2014 Antoine Martin <antoine@xpra.org> - 3.1.0final-3
- fixed Tk package dependencies

* Wed Sep 17 2014 Antoine Martin <antoine@xpra.org> - 3.1.0final-2
- Add Python3 package

* Fri Sep 05 2014 Antoine Martin <antoine@xpra.org> 3.1.0final-1
- Fix version string to prevent upgrade to older beta version

* Fri Aug 08 2014 Antoine Martin <antoine@xpra.org> 3.1.0-1
- Initial packaging for xpra
