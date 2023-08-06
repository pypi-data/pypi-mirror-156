__version__ = "0.2.0"


class KeyringEntryPointNotFoundError(Exception):
    pass


def keyring_subprocess():
    import sys

    if sys.version_info > (3, 10):
        from importlib import metadata
    else:
        import importlib_metadata as metadata

    eps = metadata.entry_points(group="console_scripts")

    if "keyring" not in eps.names:
        raise KeyringEntryPointNotFoundError(
            "No 'keyring' entry point found in the 'console_scripts' group, is keyring installed?"
        )

    keyring = eps["keyring"].load()

    return keyring()
