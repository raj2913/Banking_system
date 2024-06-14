from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from .forms import UserRegistrationForm, UserAddressForm, CustomAuthenticationForm

User = get_user_model()

class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:transaction_report')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            login(self.request, user)
            messages.success(
                self.request,
                (
                    f'Thank You For Creating A Bank Account. '
                    f'Your Account Number is {user.account.account_no}.'
                )
            )
            return HttpResponseRedirect(
                reverse_lazy('transactions:deposit_money')
            )

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()
        return super().get_context_data(**kwargs)

class UserLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/user_login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error(None, 'This email is not registered.')
            context = self.get_context_data(form=form)
            return self.render_to_response(context)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)
