import subprocess
from upseto import gitwrapper


class RootfsLabel:
    def __init__(self, rootfs):
        self._rootfs = rootfs
        if rootfs == "THIS":
            self._label = subprocess.check_output([
                "solvent", "printlabel", "--thisProject", "--product=rootfs"]).strip()
            wrapper = gitwrapper.GitWrapper(".")
            self._hint = wrapper.originURLBasename()
        else:
            self._label = subprocess.check_output([
                "solvent", "printlabel", "--repositoryBasename", rootfs, "--product=rootfs"]).strip()
            self._hint = rootfs

    def label(self):
        return self._label

    def imageHint(self):
        return self._hint
