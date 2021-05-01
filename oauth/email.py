from commons.mail.message import BaseEmailMessage


class DigitsEmail(BaseEmailMessage):
    template_name = 'email/digits.html'

    def get_context_data(self):
        context = super().get_context_data()
        return context


class DestroyUserEmail(BaseEmailMessage):
    template_name = 'email/destroy_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context
