from typing import Optional, Dict

from pygsuite.forms.base_object import BaseFormItem
from pygsuite.forms.generated.quiz_settings import QuizSettings


class FormSettings(BaseFormItem):
    """
    A form's settings.
    """

    def __init__(
        self, quiz_settings: Optional["QuizSettings"] = None, object_info: Optional[Dict] = None
    ):
        generated: Dict = {}

        if quiz_settings is not None:

            generated["quizSettings"] = quiz_settings._info
        object_info = object_info or generated
        super().__init__(object_info=object_info)

    @property
    def quiz_settings(self) -> "QuizSettings":
        return QuizSettings(object_info=self._info.get("quizSettings"))

    @quiz_settings.setter
    def quiz_settings(self, value: "QuizSettings"):
        if self._info.get("quizSettings", None) == value:
            return
        self._info["quizSettings"] = value
