PYTHON=/usr/bin/env python
VERSION=slice2py --version

slice:
	$(VERSION) && slice2py -I $(ICE_HOME)/slice Callback.ice

r:
	$(VERSION) && glacier2router --Ice.Config=config.glacier2

s:
	$(VERSION) && slice2py --version && $(PYTHON) SessionServer.py

c:
	$(VERSION) && slice2py --version && $(PYTHON) Client.py

b:
	$(VERSION) && slice2py --version && $(PYTHON) Backend.py

clean:
	rm -rf Callback_ice.py Demo *.pyc

.PHONY: slice c s r clean
