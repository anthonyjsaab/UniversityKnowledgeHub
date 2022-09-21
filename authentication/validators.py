import re
from django.core.exceptions import ValidationError
from UniversityKnowledgeHub.settings import ALLOWED_USER_FQDNS, RESTRICT_FQDN


class FQDNValidator:
    def __init__(self, email):
        allowed = False
        for fqdn in ALLOWED_USER_FQDNS:
            if re.search(rf'^\w+@{fqdn}$', email):
                allowed = True
                break
        if RESTRICT_FQDN and not allowed:
            raise ValidationError("Your email domain is not allowed")
