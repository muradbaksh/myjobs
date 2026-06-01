import hashlib


class AnonymizationService:

    @staticmethod
    def anonymize_email(email):

        return hashlib.sha256(
            email.encode()
        ).hexdigest()

    @staticmethod
    def mask_name(name):

        if len(name) <= 2:
            return "**"

        return (
            name[0]
            + "*" * (len(name) - 2)
            + name[-1]
        )