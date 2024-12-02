include $(REPO_PATH)/defines.make

PYTHON3_MODULES := python3-modules

# Used by other OMD packages
PACKAGE_PYTHON3_MODULES_PYTHON_DEPS := deps_install_bazel

PACKAGE_PYTHON3_MODULES_PYTHONPATH := $(DESTDIR)$(OMD_ROOT)/lib/python$(PYTHON_MAJOR_DOT_MINOR)/site-packages
# May be used during omd package build time. Call sites have to use the target
# dependency "$(PACKAGE_PYTHON3_MODULES_PYTHON_DEPS)" to have everything needed in place.
PACKAGE_PYTHON3_MODULES_PYTHON         := \
	PYTHONPATH="$$PYTHONPATH:$(PACKAGE_PYTHON3_MODULES_PYTHONPATH):$(PACKAGE_PYTHON_PYTHONPATH)" \
	LDFLAGS="$$LDFLAGS $(PACKAGE_PYTHON_LDFLAGS)" \
	LD_LIBRARY_PATH="$$LD_LIBRARY_PATH:$(PACKAGE_PYTHON_LD_LIBRARY_PATH)" \
	$(PACKAGE_PYTHON_EXECUTABLE)
