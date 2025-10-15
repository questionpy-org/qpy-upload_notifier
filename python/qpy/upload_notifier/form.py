from pydantic import field_validator, HttpUrl, ValidationError

from questionpy.form import (
    FormModel,
    text_area,
    text_input,
)

class UploadNotifierModel(FormModel):
    webhook_url = text_input(
        "Webhook-Url",
        required=True,
        help="Die Daten werden an diese URL gesendet. Bitte geben Sie auch das URL-Schemata an.",
    )
    username = text_input(
        "Username",
        required=True,
        help="Der Username welcher für die Basic Authentication benutzt wird."
    )
    password = text_input(
        "Password",
        required=True,
        help="Das Password welches für die Basic Authentication benutzt wird."
    )

    information = text_area(
        "Information",
        required=True,
        default="Bitte klicken Sie nach dem Upload auf den 'Check'-Button.",
        help="Diese Information wird den Nutzern angezeigt.",
    )

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if ":" in value:
            raise ValueError("Der Username darf keine Doppelpunkte enthalten.")
        return value

    @field_validator("webhook_url")
    def validate_webhook_url(cls, value: str) -> str:
        try:
            HttpUrl(value)
            return value
        except ValidationError:
            raise ValueError("Fehlerhafte URL.")
