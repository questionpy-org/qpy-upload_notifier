import base64
import json

from time import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from questionpy import get_qpy_environment, Attempt, Question, ResponseNotScorableError, NeedsManualScoringError, BaseScoringState

from .form import UploadNotifierModel


class UploadNotifierScoringState(BaseScoringState):
    webhook_response_code: int | None = None
    user_message: str | None = None
    internal_message: str | None = None


class UploadNotifierAttempt(Attempt):
    scoring_state: UploadNotifierScoringState

    def _send_to_webhook(self, data: dict) -> None:
        token = self.question.options.username + ":" + self.question.options.password
        token = base64.b64encode(token.encode()).decode()

        request = Request(
            self.question.options.webhook_url,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {token}"
            },
            data=json.dumps(data).encode(),
        )

        try:
            with urlopen(request) as response:
                pass
            self.scoring_state = UploadNotifierScoringState(
                webhook_response_code=response.getcode(),
            )
        except HTTPError as error:
            self.scoring_state = UploadNotifierScoringState(
                webhook_response_code=error.getcode(),
                user_message="Der Server konnte nicht erreicht werden. Bitte versuchen Sie es zu einem späteren Zeitpunkt noch einmal.",
                internal_message=str(error),
            )
            raise ResponseNotScorableError from error
        except URLError as error:
            self.scoring_state = UploadNotifierScoringState(
                user_message="Der Server konnte nicht erreicht werden. Bitte versuchen Sie es zu einem späteren Zeitpunkt noch einmal.",
                internal_message=str(error),
            )
            raise ResponseNotScorableError from error


    def _compute_score(self) -> float:
        attributes = get_qpy_environment().request_info.lms_provided_attributes.model_dump()
        if submission_id := attributes["lms"].pop("lms_moodle_assignment_submission_id", None):
            attributes["lms"]["submission_id"] = submission_id

        self._send_to_webhook(attributes)

        raise NeedsManualScoringError


    @property
    def specific_feedback(self) -> str | None:
        if self.scoring_state and self.scoring_state.user_message:
            return self.jinja2.get_template("feedback.xhtml.j2").render({
                "message": self.scoring_state.user_message,
            })
        return None


    @property
    def formulation(self) -> str:
        return self.jinja2.get_template("formulation.xhtml.j2").render({"timestamp": time()})


class UploadNotifierQuestion(Question):
    attempt_class = UploadNotifierAttempt

    options: UploadNotifierModel
