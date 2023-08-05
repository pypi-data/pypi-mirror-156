from typing import Dict

from NEMO.decorators import customization
from NEMO.views.customization import CustomizationBase
from django.core.exceptions import ValidationError


@customization(key="invoices", title="Invoices")
class InvoiceCustomization(CustomizationBase):
    variables = {"invoice_number_format": "{:04d}"}
    files = [
        ("email_send_invoice_subject", ".txt"),
        ("email_send_invoice_message", ".html"),
        ("email_send_invoice_reminder_subject", ".txt"),
        ("email_send_invoice_reminder_message", ".html"),
    ]

    def context(self) -> Dict:
        # Adding invoice number formatted to the template
        customization_context = super().context()
        try:
            customization_context["invoice_number_formatted"] = self.get("invoice_number_format").format(
                int(self.get("invoice_number_current"))
            )
        except:
            pass
        return customization_context

    def validate(self, name, value):
        if name == "invoice_number_format":
            try:
                value.format(123)
            except Exception as e:
                raise ValidationError(str(e))
