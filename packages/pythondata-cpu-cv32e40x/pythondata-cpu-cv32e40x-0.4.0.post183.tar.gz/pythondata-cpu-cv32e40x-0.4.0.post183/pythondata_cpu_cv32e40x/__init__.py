import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post183"
version_tuple = (0, 4, 0, 183)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post183")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post41"
data_version_tuple = (0, 4, 0, 41)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post41")
except ImportError:
    pass
data_git_hash = "25cda141e3f86c8d82a4920b6644eb455b0f57da"
data_git_describe = "0.4.0-41-g25cda141"
data_git_msg = """\
commit 25cda141e3f86c8d82a4920b6644eb455b0f57da
Merge: 4000e8ea 352226ab
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Mon Jun 27 08:02:21 2022 +0200

    Merge pull request #595 from Silabs-ArjanB/ArjanB_csru
    
    Fix mstatush_n for RVFI hookup

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
