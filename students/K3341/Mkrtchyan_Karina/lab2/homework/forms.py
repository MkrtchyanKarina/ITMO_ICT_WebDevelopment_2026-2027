from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 8, "cols": 60}),
        }
        labels = {
            "text": "Ваш ответ",
        }