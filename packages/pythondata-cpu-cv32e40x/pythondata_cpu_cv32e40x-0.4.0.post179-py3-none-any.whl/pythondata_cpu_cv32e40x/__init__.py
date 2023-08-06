import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post179"
version_tuple = (0, 4, 0, 179)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post179")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post37"
data_version_tuple = (0, 4, 0, 37)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post37")
except ImportError:
    pass
data_git_hash = "cc78743386f34a8790d0c12919b4e23d66f36cbd"
data_git_describe = "0.4.0-37-gcc787433"
data_git_msg = """\
commit cc78743386f34a8790d0c12919b4e23d66f36cbd
Merge: 8aef8f3d 1ba572b2
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Fri Jun 24 14:28:45 2022 +0200

    Merge pull request #594 from Silabs-ArjanB/ArjanB_irqackc
    
    Added CLIC signals to irq_ack mechanism

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
