LASSO := lasso
LASSO_VERS := 2.7.0
LASSO_DIR := $(LASSO)-$(LASSO_VERS)

LASSO_BUILD := $(BUILD_HELPER_DIR)/$(LASSO_DIR)-build
LASSO_UNPACK := $(BUILD_HELPER_DIR)/$(LASSO_DIR)-unpack
LASSO_INTERMEDIATE_INSTALL := $(BUILD_HELPER_DIR)/$(LASSO_DIR)-install-intermediate
LASSO_INSTALL := $(BUILD_HELPER_DIR)/$(LASSO_DIR)-install

LASSO_INSTALL_DIR := $(INTERMEDIATE_INSTALL_BASE)/$(LASSO_DIR)
LASSO_BUILD_DIR := $(PACKAGE_BUILD_DIR)/$(LASSO_DIR)
#LASSO_WORK_DIR := $(PACKAGE_WORK_DIR)/$(LASSO_DIR)

$(LASSO): $(LASSO_BUILD) $(LASSO_INTERMEDIATE_INSTALL)

$(LASSO)-unpack: $(LASSO_UNPACK)

$(LASSO)-int: $(LASSO_INTERMEDIATE_INSTALL)

ifeq ($(filter sles%,$(DISTRO_CODE)),)
$(LASSO_BUILD): $(LASSO_UNPACK) $(PYTHON3_CACHE_PKG_PROCESS) $(PYTHON3_MODULES_CACHE_PKG_PROCESS)
	cd $(LASSO_BUILD_DIR) \
	&& export PYTHONPATH=$$PYTHONPATH:$(PACKAGE_PYTHON3_MODULES_PYTHONPATH) \
	&& export PYTHONPATH=$$PYTHONPATH:$(PACKAGE_PYTHON3_PYTHONPATH) \
	&& export LDFLAGS="$(PACKAGE_PYTHON3_LDFLAGS)" \
	&& export LD_LIBRARY_PATH="$(PACKAGE_PYTHON3_LD_LIBRARY_PATH)" \
	&& export CFLAGS="-I$(PACKAGE_PYTHON3_INCLUDE_PATH)" \
	&& ./configure \
	    --prefix=$(OMD_ROOT) \
	    --disable-gtk-doc \
	    --disable-java \
	    --disable-perl \
	    --enable-static-linking \
	    --with-python=$(PACKAGE_PYTHON3_EXECUTABLE) \
	&& $(MAKE)
	$(TOUCH) $@
else
$(LASSO_BUILD):
	$(MKDIR) $(BUILD_HELPER_DIR)
	$(TOUCH) $@
endif

$(LASSO_INTERMEDIATE_INSTALL): $(LASSO_BUILD)
ifeq ($(filter sles%,$(DISTRO_CODE)),)
	$(MKDIR) $(INTERMEDIATE_INSTALL_BASE)/$(LASSO_DIR)
	export PYTHONPATH=$$PYTHONPATH:$(PACKAGE_PYTHON3_MODULES_PYTHONPATH) \
	&& export PYTHONPATH=$$PYTHONPATH:$(PACKAGE_PYTHON3_PYTHONPATH) \
	&& export LD_LIBRARY_PATH="$(PACKAGE_PYTHON3_LD_LIBRARY_PATH)" \
	&& $(MAKE) DESTDIR=$(LASSO_INSTALL_DIR) -C $(LASSO_BUILD_DIR) install
endif
	$(TOUCH) $@

$(LASSO_INSTALL): $(LASSO_INTERMEDIATE_INSTALL)
ifeq ($(filter sles%,$(DISTRO_CODE)),)
	$(RSYNC) $(LASSO_INSTALL_DIR)/$(OMD_ROOT)/ $(DESTDIR)$(OMD_ROOT)/
	$(TOUCH) $@
endif
	$(TOUCH) $@

$(LASSO)_download:
	cd packages/lasso/ \
	&& wget https://repos.entrouvert.org/lasso.git/snapshot/lasso-$(LASSO_VERS).tar.gz
