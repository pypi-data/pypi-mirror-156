import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post186"
version_tuple = (0, 4, 0, 186)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post186")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post44"
data_version_tuple = (0, 4, 0, 44)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post44")
except ImportError:
    pass
data_git_hash = "f9cab8b9c2e2524b646baf85dae4fca34dd94c4d"
data_git_describe = "0.4.0-44-gf9cab8b9"
data_git_msg = """\
commit f9cab8b9c2e2524b646baf85dae4fca34dd94c4d
Merge: 25cda141 d78d0116
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Tue Jun 28 16:08:22 2022 +0200

    Merge pull request #597 from silabs-oysteink/silabs-oysteink_misc-w26
    
    Temporarily set localparam ZC_EXT to 0

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
