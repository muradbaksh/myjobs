from rest_framework.throttling import (
    UserRateThrottle,
    AnonRateThrottle
)


class ReviewSubmissionThrottle(
    UserRateThrottle
):

    scope = "review_submission"


class CompensationSubmissionThrottle(
    UserRateThrottle
):

    scope = "compensation_submission"


class AnalyticsThrottle(
    UserRateThrottle
):

    scope = "analytics"


class AnonymousThrottle(
    AnonRateThrottle
):

    scope = "anonymous"