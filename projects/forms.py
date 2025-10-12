from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    technologies = forms.CharField(
        label="Technologies",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., Django, React, Docker, ...",
            }
        ),
    )

    is_public = forms.ChoiceField(
        choices=(
            (True, "Public - Everyone can see"),
            (False, "Private - Only you can see"),
        ),
        label="Visibility",
        initial=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "overview",
            "description",
            "video_url",
            "github_url",
            "image",
            "objectives",
            "key_learning",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Personal Portfolio Website",
                }
            ),
            "overview": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "A short summary that will appear in the project feed",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your project in detail. What was your motivation? What features does it have?",
                }
            ),
            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.youtube.com/embed/your_video_id",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username/repository",
                }
            ),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "objectives": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "What goals does this project achieve? (one per line)",
                }
            ),
            "key_learning": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "What were the most important skills or concepts you learned? List one per line.",
                }
            ),
        }
