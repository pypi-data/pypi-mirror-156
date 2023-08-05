import grpc
from typing import Callable, List
import blindecdh
import pskca
from cryptography.x509 import Certificate


ECDHVerificationCallback = Callable[[str, blindecdh.CompletedECDH], bool]
CertificateIssuedCallback = Callable[
    [str, Certificate, List[Certificate]],
    bool,
]


class Rejected(Exception):
    """Base class for rejections."""


class RejectedByPeer(Rejected):
    """
    This exception is raised when the client code runs the ECDH exchange,
    and the server callback rejected the exchange.
    """

    pass


class RejectedBySelf(Rejected):
    """
    This exception is raised when the client code runs the ECDH exchange,
    and the client callback rejected the exchange.
    """

    pass


class Ignored(Rejected):
    """
    This exception is raised when the server never authorized the ECDH
    exchange in the deadline given to the CAKESCLient.run() method.
    """


Pending = pskca.Pending

CannotDecrypt = pskca.CannotDecrypt


EPERM = grpc.StatusCode.PERMISSION_DENIED
EWAIT = grpc.StatusCode.UNAUTHENTICATED
EINVAL = grpc.StatusCode.INVALID_ARGUMENT
