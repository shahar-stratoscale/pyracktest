all: check_convention

clean:
	rm -fr logs.racktest

test:
	RACKATTACK_PROVIDER=tcp://localhost:1014@tcp://localhost:1015 UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD):$(PWD)/py python tests/test.py
phystest:
	RACKATTACK_PROVIDER=tcp://rackattack-provider:1014@tcp://rackattack-provider:1015 UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD):$(PWD)/py python tests/test.py

check_convention:
	pep8 py test* example* --max-line-length=109
