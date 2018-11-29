OMD := omd
OMD_VERS := $(OMD_VERSION)
OMD_DIR := $(OMD)-$(OMD_VERS)

ifeq ($(DISTRO_NAME),SLES)
    DEFAULT_RUNLEVELS=2 3 5
else
    DEFAULT_RUNLEVELS=2 3 4 5
endif

OMD_INSTALL := $(BUILD_HELPER_DIR)/$(OMD_DIR)-install

.PHONY: $(OMD) $(OMD)-install $(OMD)-skel

$(OMD):

$(OMD)-install: $(OMD_INSTALL)

$(OMD_INSTALL):
	mkdir -p $(DESTDIR)$(OMD_ROOT)/bin
	install -m 755 $(PACKAGE_DIR)/$(OMD)/omd.bin $(DESTDIR)$(OMD_ROOT)/bin/omd
	mkdir -p $(DESTDIR)$(OMD_ROOT)/lib/python/omdlib
	install -m 644 $(PACKAGE_DIR)/$(OMD)/omdlib/*.py $(DESTDIR)$(OMD_ROOT)/lib/python/omdlib/
	sed -i 's|###OMD_VERSION###|$(OMD_VERSION)|g' $(DESTDIR)$(OMD_ROOT)/bin/omd $(DESTDIR)$(OMD_ROOT)/lib/python/omdlib/__init__.py
	mkdir -p $(DESTDIR)$(OMD_ROOT)/share/omd/htdocs
	install -m 644 $(PACKAGE_DIR)/$(OMD)/logout.php $(DESTDIR)$(OMD_ROOT)/share/omd/htdocs
	mkdir -p $(DESTDIR)$(OMD_ROOT)/share/man/man8
	install -m 644 $(PACKAGE_DIR)/$(OMD)/omd.8 $(DESTDIR)$(OMD_ROOT)/share/man/man8
	gzip $(DESTDIR)$(OMD_ROOT)/share/man/man8/omd.8
	install -m 755 $(PACKAGE_DIR)/$(OMD)/omd.init $(DESTDIR)$(OMD_ROOT)/share/omd/omd.init
	sed -i 's|###DEFAULT_RUNLEVELS###|$(DEFAULT_RUNLEVELS)|g' $(DESTDIR)$(OMD_ROOT)/share/omd/omd.init
	install -m 644 $(PACKAGE_DIR)/$(OMD)/omd.service $(DESTDIR)$(OMD_ROOT)/share/omd/omd.service
	mkdir -p $(DESTDIR)$(OMD_ROOT)/share/doc/$(NAME)
	install -m 644 $(PACKAGE_DIR)/$(OMD)/README $(PACKAGE_DIR)/$(OMD)/COPYING $(DESTDIR)$(OMD_ROOT)/share/doc/$(NAME)
	mkdir -p $(DESTDIR)$(OMD_ROOT)/lib/omd
	install -m 644 $(PACKAGE_DIR)/$(OMD)/init_profile $(DESTDIR)$(OMD_ROOT)/lib/omd/
	install -m 755 $(PACKAGE_DIR)/$(OMD)/port_is_used $(DESTDIR)$(OMD_ROOT)/lib/omd/
	install -m 644 $(PACKAGE_DIR)/$(OMD)/bash_completion $(DESTDIR)$(OMD_ROOT)/lib/omd/
	mkdir -p $(DESTDIR)$(OMD_ROOT)/lib/omd/scripts/post-create
	install -m 755 $(PACKAGE_DIR)/$(OMD)/ADMIN_MAIL $(DESTDIR)$(OMD_ROOT)/lib/omd/hooks/
	install -m 755 $(PACKAGE_DIR)/$(OMD)/APACHE_MODE $(DESTDIR)$(OMD_ROOT)/lib/omd/hooks/
	install -m 755 $(PACKAGE_DIR)/$(OMD)/AUTOSTART $(DESTDIR)$(OMD_ROOT)/lib/omd/hooks/
	install -m 755 $(PACKAGE_DIR)/$(OMD)/CORE $(DESTDIR)$(OMD_ROOT)/lib/omd/hooks/
	install -m 755 $(PACKAGE_DIR)/$(OMD)/TMPFS $(DESTDIR)$(OMD_ROOT)/lib/omd/hooks/

	$(TOUCH) $@

$(OMD)-skel:
	mkdir -p $(SKEL)/etc/bash_completion.d

$(OMD)-clean:
