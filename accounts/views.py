from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm


class SignupView(CreateView):
    """Self-service registration.

    New users inherit `role='public'` from the model's default — the form does
    not expose `role`, so the field can't be tampered with via POST.
    """

    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("catalog:product_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self._redirect_to_home()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login after successful registration — `self.object` was just
        # created via `form.save()` and needs an explicit backend.
        login(
            self.request,
            self.object,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        return response

    def _redirect_to_home(self):
        from django.shortcuts import redirect
        return redirect(self.success_url)


signup_view = SignupView.as_view()
