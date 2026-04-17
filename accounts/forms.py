from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


TAILWIND_INPUT = (
    "w-full rounded-lg border border-gray-300 bg-white py-2.5 px-4 text-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-2 "
    "focus:ring-brand-500 focus:border-brand-500 transition"
)


class _TailwindStyledMixin:
    """Inject consistent Tailwind classes on every field's widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {TAILWIND_INPUT}".strip()


class LoginForm(_TailwindStyledMixin, AuthenticationForm):
    pass


class SignupForm(_TailwindStyledMixin, UserCreationForm):
    company_name = forms.CharField(
        required=False,
        max_length=200,
        label=_("Company name"),
        widget=forms.TextInput(
            attrs={"placeholder": _("e.g. Al Asadi Contracting (optional)")}
        ),
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        label=_("Phone"),
        widget=forms.TextInput(attrs={"placeholder": "+964 7XX XXX XXXX"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "company_name", "phone", "password1", "password2")
