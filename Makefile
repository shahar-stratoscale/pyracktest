all: test check_convention

clean:
	rm -fr logs.racktest

test:
	RACKATTACK_PROVIDER=tcp://localhost:1014@tcp://localhost:1015 UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD):$(PWD)/py:$(PWD)/../rackattack-api python tests/test.py

check_convention:
	pep8 py test* example* --max-line-length=109
