from commons import utils
from commons.mail.message import BaseEmailMessage

class DigitsEmail(BaseEmailMessage):
    template_name = 'email/digits.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['digits'] = utils.get_random_number()
        return context
