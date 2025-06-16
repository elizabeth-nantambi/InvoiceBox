from django.core.management.base import BaseCommand
from InvoiceBoxApp.models import CustomUser, Invoice, Payment
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate dummy data for InvoiceBox'

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write("Creating users...")

        # Create providers
        providers = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='Test@123',
                role='provider'
            )
            providers.append(user)

        # Create purchasers
        purchasers = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='Test@123',
                role='purchaser'
            )
            purchasers.append(user)

        self.stdout.write("Creating invoices and payments...")

        # Create invoices 
        for i in range(15):
            provider = random.choice(providers)
            purchaser = random.choice(purchasers)
            amount = round(random.uniform(100, 10000), 2)
            currency = random.choice(['UGX', 'USD', 'LYD'])

            invoice = Invoice.objects.create(
                provider=provider,
                purchaser=purchaser,
                description=fake.sentence(),
                amount=amount,
                currency=currency,
                date_due=timezone.now() + timezone.timedelta(days=15),
            )

            # Randomly mark as paid
            if random.choice([True, False]):
                Payment.objects.create(
                    invoice=invoice,
                    amount_paid=amount,
                )
                invoice.status = 'paid'
                invoice.date_paid = timezone.now()
                invoice.save()

        self.stdout.write(self.style.SUCCESS("Dummy data created successfully!"))
