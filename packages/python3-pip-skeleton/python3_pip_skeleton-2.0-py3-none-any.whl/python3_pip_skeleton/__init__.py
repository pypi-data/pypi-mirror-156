try:
    # Use live version from git
    from setuptools_scm import get_version

    # Warning: If the install is nested to the same depth, this will always succeed
    tmp_version = get_version(root="../../", relative_to=__file__)
    del get_version
except (ImportError, LookupError):
    # Use installed version
    from ._version import version as __version__
else:
    __version__ = tmp_version

__all__ = ["__version__"]
