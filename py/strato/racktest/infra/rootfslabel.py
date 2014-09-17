import subprocess
from upseto import gitwrapper
from upseto import run


class RootfsLabel:
    def __init__(self, rootfs):
        self._rootfs = rootfs
        if rootfs == "THIS":
            self._label = run.run([
                "solvent", "printlabel", "--thisProject", "--product=rootfs"]).strip()
            wrapper = gitwrapper.GitWrapper(".")
            self._hint = wrapper.originURLBasename()
        else:
            self._label = run.run([
                "solvent", "printlabel", "--repositoryBasename", rootfs, "--product=rootfs"]).strip()
            self._hint = rootfs

    def label(self):
        return self._label

    def imageHint(self):
        return self._hint
