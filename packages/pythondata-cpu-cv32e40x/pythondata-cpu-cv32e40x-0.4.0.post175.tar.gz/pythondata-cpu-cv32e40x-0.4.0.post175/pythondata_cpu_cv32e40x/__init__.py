import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post175"
version_tuple = (0, 4, 0, 175)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post175")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post33"
data_version_tuple = (0, 4, 0, 33)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post33")
except ImportError:
    pass
data_git_hash = "967e206303a9f02d5befe49e63b8dc4ab17de233"
data_git_describe = "0.4.0-33-g967e2063"
data_git_msg = """\
commit 967e206303a9f02d5befe49e63b8dc4ab17de233
Merge: 440b5ced aa095e6c
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Wed Jun 22 19:51:56 2022 +0200

    Merge pull request #590 from silabs-oysteink/silabs-oysteink_zc-seq-41p
    
    Added missing assertion file.

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
