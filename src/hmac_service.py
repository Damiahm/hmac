"""Module with HMAC sign functions"""




class HMACSigner:
    """Class for HMAC sign and verify signature"""

    # TODO: реализуйте функцию подписи
    def sign(self, msg: str) -> bytes:
        """
        Sign message with HMAC algorithm.

        :param msg: Message for sign.
        :return: Signature bytes.
        """
        pass

    # TODO: реализуйте функцию проверки
    def verify(self, msg: str, signature: bytes) -> bool:
        """
        Verify message signature with HMAC algorithm.

        :param msg: Message for verify.
        :param signature: Signature for verify.
        :return: True if signature for message valid, else False.
        """
        pass


def hmac_service() -> HMACSigner:
    """
    Fabric for signer.

    :return: Initialized HMACSigner object.
    """
    return HMACSigner()
