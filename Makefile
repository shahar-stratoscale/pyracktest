all: check_convention

clean:
	rm -fr logs.racktest

racktest:
	UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD):$(PWD)/py python tests/test.py $(REGEX)
virttest:
	RACKATTACK_PROVIDER=tcp://localhost:1014@tcp://localhost:1015 $(MAKE) racktest
phystest:
	RACKATTACK_PROVIDER=tcp://rackattack-provider:1014@tcp://rackattack-provider:1015 $(MAKE) racktest

check_convention:
	pep8 py test* example* --max-line-length=109
