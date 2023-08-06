import sys
from typing import List
import blindecdh
from cryptography.x509 import Certificate


def unconditional_accept_ecdh(
    peer: str,
    unused: blindecdh.CompletedECDH,
) -> bool:
    """
    Stub callback function to auto-accept an ECDH exchange.

    Do not use in production.  Blindly "verifying" an ECDH exchange without
    comparing the two CompleteECDH exchanges on both sides makes your code
    vulnerable to active man-in-the-middle attacks.
    """
    return True


def unconditional_accept_cert(
    peer: str,
    unused: Certificate,
    unused_list: List[Certificate],
) -> bool:
    """
    Stub callback function to auto-accept an issued certificate.

    You may use this in production.
    """
    return True


def accept_ecdh_via_console(
    peer: str,
    complete: blindecdh.CompletedECDH,
) -> bool:
    """
    Sample function to accept ECDHs via terminal standard input/output.

    Your CAKES servicer will ask you on the terminal if you use this function
    as verification callback for ECDHs.

    This is useful for prototyping services on a console, but should not be
    used in production.
    """
    print("Peer says it's %s" % peer)
    print("Key appears to be %r" % complete.derived_key)
    print("Accept?  [Y/N then ENTER]")
    line = sys.stdin.readline()
    result = line.lower().startswith("y")
    return result


__all__ = [
    "unconditional_accept_ecdh",
    "unconditional_accept_cert",
    "accept_ecdh_via_console",
]
