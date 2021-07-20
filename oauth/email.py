from commons.mail.message import BaseEmailMessage


class CaptchaEmail(BaseEmailMessage):
    template_name = 'email/captcha.html'

    def get_context_data(self):
        context = super().get_context_data()
        return context


class UserDestroyEmail(BaseEmailMessage):
    template_name = 'email/user_destroy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context
