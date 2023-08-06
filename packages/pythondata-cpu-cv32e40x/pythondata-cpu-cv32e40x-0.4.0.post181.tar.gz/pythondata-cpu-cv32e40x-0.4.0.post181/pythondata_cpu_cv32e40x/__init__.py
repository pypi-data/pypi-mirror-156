import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post181"
version_tuple = (0, 4, 0, 181)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post181")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post39"
data_version_tuple = (0, 4, 0, 39)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post39")
except ImportError:
    pass
data_git_hash = "4000e8ead724fd1391ccea7af4389020b8daa60b"
data_git_describe = "0.4.0-39-g4000e8ea"
data_git_msg = """\
commit 4000e8ead724fd1391ccea7af4389020b8daa60b
Merge: cc787433 c0e8ccce
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri Jun 24 17:21:47 2022 +0200

    Merge pull request #592 from Silabs-ArjanB/ArjanB_docrvfii
    
    Corrected and clarified rvfi_intr, rvfi_dbg table. Fixes https://gith…

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
