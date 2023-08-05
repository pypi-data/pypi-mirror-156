import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post173"
version_tuple = (0, 4, 0, 173)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post173")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post31"
data_version_tuple = (0, 4, 0, 31)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post31")
except ImportError:
    pass
data_git_hash = "440b5ced08e3f3029483632183904075853d2938"
data_git_describe = "0.4.0-31-g440b5ced"
data_git_msg = """\
commit 440b5ced08e3f3029483632183904075853d2938
Merge: 32c31a07 09339b1d
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Wed Jun 22 17:01:30 2022 +0200

    Merge pull request #588 from silabs-oysteink/silabs-oysteink_zc-seq-41p
    
    Initial implementation of Zc * sequencer

"""

# Tool version info
tool_version_str = "0.0.post142"
tool_version_tuple = (0, 0, 142)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post142")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
