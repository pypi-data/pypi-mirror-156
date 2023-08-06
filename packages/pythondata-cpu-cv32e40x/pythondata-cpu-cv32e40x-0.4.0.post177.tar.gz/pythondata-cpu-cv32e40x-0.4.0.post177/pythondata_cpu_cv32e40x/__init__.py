import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post177"
version_tuple = (0, 4, 0, 177)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post177")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post35"
data_version_tuple = (0, 4, 0, 35)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post35")
except ImportError:
    pass
data_git_hash = "8aef8f3daf10271891654afdc34f0a6b58db637c"
data_git_describe = "0.4.0-35-g8aef8f3d"
data_git_msg = """\
commit 8aef8f3daf10271891654afdc34f0a6b58db637c
Merge: 967e2063 40449531
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Fri Jun 24 12:40:20 2022 +0200

    Merge pull request #593 from Silabs-ArjanB/ArjanB_Zce1
    
    Removed ZC_EXT as top level parameter. ZC_EXT is now a localparam, al…

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
