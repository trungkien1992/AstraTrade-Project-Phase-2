"""
Financial Domain Services

Domain services for the Financial Domain implementing complex business operations
that span multiple entities or integrate with external systems.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Protocol
from abc import ABC, abstractmethod

from entities import Account, Subscription, Payment, Invoice, DomainEvent
from value_objects import (
    Money, PaymentMethod, SubscriptionTier, TransactionRecord, BillingPeriod,
    PaymentStatus, Currency, SubscriptionTierType, BillingCycle, RevenueStream,
    PaymentMethodType, PaymentProcessor, ComplianceRecord
)


# Repository Interfaces (following Dependency Inversion Principle)
class AccountRepositoryInterface(ABC):
    """Interface for account persistence operations"""
    
    @abstractmethod
    def save(self, account: Account) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, account_id: str) -> Optional[Account]:
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> Optional[Account]:
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Account]:
        pass


class SubscriptionRepositoryInterface(ABC):
    """Interface for subscription persistence operations"""
    
    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, subscription_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    def find_expiring_soon(self, days: int) -> List[Subscription]:
        pass


class PaymentRepositoryInterface(ABC):
    """Interface for payment persistence operations"""
    
    @abstractmethod
    def save(self, payment: Payment) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, payment_id: str) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def find_by_account_id(self, account_id: str) -> List[Payment]:
        pass
    
    @abstractmethod
    def find_by_status(self, status: PaymentStatus) -> List[Payment]:
        pass


class InvoiceRepositoryInterface(ABC):
    """Interface for invoice persistence operations"""
    
    @abstractmethod
    def save(self, invoice: Invoice) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, invoice_id: str) -> Optional[Invoice]:
        pass
    
    @abstractmethod
    def find_overdue(self) -> List[Invoice]:
        pass


class PaymentProcessorInterface(ABC):
    """Interface for external payment processor integration"""
    
    @abstractmethod
    def process_payment(self, payment: Payment) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def refund_payment(self, processor_transaction_id: str, amount: Money) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_payment_status(self, processor_transaction_id: str) -> str:
        pass


class NotificationServiceInterface(ABC):
    """Interface for sending notifications"""
    
    @abstractmethod
    def send_invoice(self, user_id: int, invoice: Invoice) -> None:
        pass
    
    @abstractmethod
    def send_payment_confirmation(self, user_id: int, payment: Payment) -> None:
        pass
    
    @abstractmethod
    def send_subscription_renewal_reminder(self, user_id: int, subscription: Subscription) -> None:
        pass


# Domain Services
class PaymentService:
    """
    Domain service for payment processing operations
    
    Handles payment creation, processing, and lifecycle management.
    Coordinates between Payment entities and external payment processors.
    """
    
    def __init__(
        self,
        payment_repository: PaymentRepositoryInterface,
        account_repository: AccountRepositoryInterface,
        payment_processor: PaymentProcessorInterface,
        notification_service: NotificationServiceInterface
    ):
        self.payment_repository = payment_repository
        self.account_repository = account_repository
        self.payment_processor = payment_processor
        self.notification_service = notification_service
    
    def create_payment(
        self,
        account_id: str,
        amount: Money,
        payment_method: PaymentMethod,
        payment_type: str = "subscription",
        reference_id: Optional[str] = None
    ) -> Payment:
        """Create a new payment"""
        
        # Validate account exists and is active
        account = self.account_repository.find_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if not account.is_active():
            raise ValueError("Cannot create payment for inactive account")
        
        # Validate payment method
        if payment_method.is_expired():
            raise ValueError("Cannot use expired payment method")
        
        # Create payment entity
        payment = Payment(
            account_id=account_id,
            amount=amount,
            payment_method=payment_method,
            payment_type=payment_type,
            reference_id=reference_id
        )
        
        # Generate unique payment ID
        payment_id = f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{account_id[-6:]}"
        payment.set_payment_id(payment_id)
        
        # Save payment
        self.payment_repository.save(payment)
        
        return payment
    
    def process_payment(self, payment_id: str) -> bool:
        """Process a pending payment"""
        
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if not payment.is_pending():
            raise ValueError("Can only process pending payments")
        
        try:
            # Process with external payment processor
            result = self.payment_processor.process_payment(payment)
            
            if result.get("success"):
                # Mark as processing
                payment.process_payment(result["transaction_id"])
                self.payment_repository.save(payment)
                
                # Complete payment
                payment.complete_payment()
                self.payment_repository.save(payment)
                
                # Update account balance if it's a deposit
                if payment.payment_type.startswith("deposit"):
                    account = self.account_repository.find_by_id(payment.account_id)
                    if account:
                        account.add_funds(payment.amount, payment_id, "payment")
                        self.account_repository.save(account)
                
                # Send confirmation
                account = self.account_repository.find_by_id(payment.account_id)
                if account:
                    self.notification_service.send_payment_confirmation(account.user_id, payment)
                
                return True
            else:
                # Mark as failed
                payment.fail_payment(result.get("error", "Payment processing failed"))
                self.payment_repository.save(payment)
                return False
                
        except Exception as e:
            # Mark as failed
            payment.fail_payment(str(e))
            self.payment_repository.save(payment)
            return False
    
    def refund_payment(self, payment_id: str, refund_amount: Optional[Money] = None) -> bool:
        """Refund a completed payment"""
        
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if not payment.can_be_refunded():
            raise ValueError("Payment cannot be refunded")
        
        if refund_amount is None:
            refund_amount = payment.amount
        
        try:
            # Process refund with payment processor
            if payment.processor_transaction_id:
                result = self.payment_processor.refund_payment(
                    payment.processor_transaction_id, 
                    refund_amount
                )
                
                if result.get("success"):
                    # Mark as refunded
                    payment.refund_payment(refund_amount)
                    self.payment_repository.save(payment)
                    
                    # Update account balance
                    account = self.account_repository.find_by_id(payment.account_id)
                    if account and payment.payment_type.startswith("deposit"):
                        account.withdraw_funds(refund_amount, f"refund_{payment_id}", "refund")
                        self.account_repository.save(account)
                    
                    return True
            
            return False
            
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")
    
    def get_payment_history(self, account_id: str) -> List[Payment]:
        """Get payment history for account"""
        return self.payment_repository.find_by_account_id(account_id)
    
    def retry_failed_payments(self) -> int:
        """Retry failed payments that can be retried"""
        failed_payments = self.payment_repository.find_by_status(PaymentStatus.FAILED)
        retry_count = 0
        
        for payment in failed_payments:
            # Only retry recent failures (within 24 hours)
            if payment.created_at > datetime.now() - timedelta(hours=24):
                try:
                    # Reset status to pending
                    payment.status = PaymentStatus.PENDING
                    payment.failure_reason = None
                    self.payment_repository.save(payment)
                    
                    # Attempt to process again
                    if self.process_payment(payment.payment_id):
                        retry_count += 1
                except Exception:
                    continue  # Skip if retry fails
        
        return retry_count


class SubscriptionService:
    """
    Domain service for subscription management operations
    
    Handles subscription lifecycle, billing, upgrades, and renewals.
    Coordinates between Subscription entities and payment processing.
    """
    
    def __init__(
        self,
        subscription_repository: SubscriptionRepositoryInterface,
        account_repository: AccountRepositoryInterface,
        payment_service: PaymentService,
        notification_service: NotificationServiceInterface
    ):
        self.subscription_repository = subscription_repository
        self.account_repository = account_repository
        self.payment_service = payment_service
        self.notification_service = notification_service
    
    def create_subscription(
        self,
        user_id: int,
        account_id: str,
        tier: SubscriptionTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> Subscription:
        """Create a new subscription"""
        
        # Check if user already has a subscription
        existing_subscription = self.subscription_repository.find_by_user_id(user_id)
        if existing_subscription and existing_subscription.is_active():
            raise ValueError("User already has an active subscription")
        
        # Validate account
        account = self.account_repository.find_by_id(account_id)
        if not account or not account.is_active():
            raise ValueError("Invalid or inactive account")
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            account_id=account_id,
            current_tier=tier,
            billing_cycle=billing_cycle
        )
        
        # Generate unique subscription ID
        subscription_id = f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        subscription.set_subscription_id(subscription_id)
        
        # Create first billing period
        if tier.tier_type != SubscriptionTierType.FREE:
            subscription.renew_subscription()
        
        # Save subscription
        self.subscription_repository.save(subscription)
        
        return subscription
    
    def upgrade_subscription(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier,
        payment_method: PaymentMethod
    ) -> bool:
        """Upgrade subscription to higher tier"""
        
        subscription = self.subscription_repository.find_by_user_id(
            self._get_user_id_from_subscription(subscription_id)
        )
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if not subscription.is_active():
            raise ValueError("Cannot upgrade inactive subscription")
        
        # Calculate prorated amount for upgrade
        current_price = subscription.current_tier.monthly_price if subscription.billing_cycle == BillingCycle.MONTHLY else subscription.current_tier.yearly_price
        new_price = new_tier.monthly_price if subscription.billing_cycle == BillingCycle.MONTHLY else new_tier.yearly_price
        
        price_difference = new_price.subtract(current_price)
        
        if price_difference.is_zero():
            # No payment needed, just upgrade
            subscription.upgrade_tier(new_tier)
            self.subscription_repository.save(subscription)
            return True
        
        # Calculate prorated amount based on remaining period
        if subscription.current_period:
            remaining_ratio = Decimal(subscription.current_period.days_remaining()) / Decimal(30 if subscription.billing_cycle == BillingCycle.MONTHLY else 365)
            prorated_amount = price_difference.multiply(remaining_ratio)
        else:
            prorated_amount = price_difference
        
        # Create payment for upgrade
        try:
            payment = self.payment_service.create_payment(
                account_id=subscription.account_id,
                amount=prorated_amount,
                payment_method=payment_method,
                payment_type="subscription_upgrade",
                reference_id=subscription_id
            )
            
            # Process payment
            if self.payment_service.process_payment(payment.payment_id):
                # Upgrade subscription
                subscription.upgrade_tier(new_tier)
                self.subscription_repository.save(subscription)
                return True
            else:
                return False
                
        except Exception as e:
            raise ValueError(f"Upgrade payment failed: {str(e)}")
    
    def cancel_subscription(self, subscription_id: str, reason: str = "user_request") -> None:
        """Cancel subscription"""
        
        subscription = self.subscription_repository.find_by_user_id(
            self._get_user_id_from_subscription(subscription_id)
        )
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription.cancel_subscription(reason)
        self.subscription_repository.save(subscription)
    
    def process_renewals(self) -> int:
        """Process subscription renewals for expiring subscriptions"""
        
        # Find subscriptions expiring in next 3 days
        expiring_subscriptions = self.subscription_repository.find_expiring_soon(3)
        renewal_count = 0
        
        for subscription in expiring_subscriptions:
            if not subscription.auto_renew or subscription.status != "active":
                continue
            
            try:
                # Get account and primary payment method
                account = self.account_repository.find_by_id(subscription.account_id)
                if not account or not account.is_active():
                    continue
                
                primary_payment_method = account.get_primary_payment_method()
                if not primary_payment_method or primary_payment_method.is_expired():
                    # Send notification about payment method issue
                    self.notification_service.send_subscription_renewal_reminder(
                        subscription.user_id, subscription
                    )
                    continue
                
                # Determine renewal amount
                if subscription.billing_cycle == BillingCycle.MONTHLY:
                    renewal_amount = subscription.current_tier.monthly_price
                elif subscription.billing_cycle == BillingCycle.YEARLY:
                    renewal_amount = subscription.current_tier.yearly_price
                else:
                    renewal_amount = subscription.current_tier.yearly_price
                
                # Create renewal payment
                payment = self.payment_service.create_payment(
                    account_id=subscription.account_id,
                    amount=renewal_amount,
                    payment_method=primary_payment_method,
                    payment_type="subscription_renewal",
                    reference_id=subscription.subscription_id
                )
                
                # Process payment
                if self.payment_service.process_payment(payment.payment_id):
                    # Renew subscription
                    subscription.renew_subscription()
                    self.subscription_repository.save(subscription)
                    renewal_count += 1
                
            except Exception as e:
                # Log error but continue processing other subscriptions
                continue
        
        return renewal_count
    
    def get_subscription_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get subscription analytics for date range"""
        # This would typically query the repository for analytics data
        # For now, return a basic structure
        return {
            "total_subscriptions": 0,
            "new_subscriptions": 0,
            "cancelled_subscriptions": 0,
            "upgrade_count": 0,
            "downgrade_count": 0,
            "revenue_by_tier": {},
            "churn_rate": 0.0
        }
    
    def _get_user_id_from_subscription(self, subscription_id: str) -> int:
        """Helper to extract user ID from subscription ID"""
        # This is a simplified version - in reality, you'd query the repository
        return int(subscription_id.split('_')[-1]) if '_' in subscription_id else 0


class RevenueService:
    """
    Domain service for revenue tracking and analytics
    
    Handles revenue calculations, reporting, and analytics across
    the 4 revenue streams defined in the roadmap.
    """
    
    def __init__(
        self,
        account_repository: AccountRepositoryInterface,
        subscription_repository: SubscriptionRepositoryInterface,
        payment_repository: PaymentRepositoryInterface
    ):
        self.account_repository = account_repository
        self.subscription_repository = subscription_repository
        self.payment_repository = payment_repository
    
    def calculate_monthly_recurring_revenue(self, date: datetime = None) -> Dict[Currency, Money]:
        """Calculate Monthly Recurring Revenue (MRR) by currency"""
        if date is None:
            date = datetime.now()
        
        # This would typically query active subscriptions and sum monthly values
        # For now, return a basic structure
        return {
            Currency.USD: Money(Decimal('0'), Currency.USD),
            Currency.EUR: Money(Decimal('0'), Currency.EUR)
        }
    
    def calculate_annual_recurring_revenue(self, date: datetime = None) -> Dict[Currency, Money]:
        """Calculate Annual Recurring Revenue (ARR) by currency"""
        mrr = self.calculate_monthly_recurring_revenue(date)
        arr = {}
        
        for currency, amount in mrr.items():
            arr[currency] = amount.multiply(Decimal('12'))
        
        return arr
    
    def get_revenue_by_stream(self, start_date: datetime, end_date: datetime) -> Dict[RevenueStream, Money]:
        """Get revenue breakdown by revenue stream"""
        revenue_by_stream = {}
        
        for stream in RevenueStream:
            # Query transactions for this revenue stream
            # For now, return zeros
            revenue_by_stream[stream] = Money(Decimal('0'), Currency.USD)
        
        return revenue_by_stream
    
    def calculate_customer_lifetime_value(self, user_id: int) -> Money:
        """Calculate Customer Lifetime Value (CLV) for a user"""
        account = self.account_repository.find_by_user_id(user_id)
        if not account:
            return Money(Decimal('0'), Currency.USD)
        
        # Sum all revenue-generating transactions
        total_revenue = Money(Decimal('0'), Currency.USD)
        
        for transaction in account.transaction_history:
            if transaction.revenue_stream in [RevenueStream.SUBSCRIPTIONS, RevenueStream.PREMIUM_FEATURES]:
                if transaction.amount.currency == Currency.USD:
                    total_revenue = total_revenue.add(transaction.amount)
        
        return total_revenue
    
    def get_revenue_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""
        return {
            "total_revenue": self._calculate_total_revenue(start_date, end_date),
            "revenue_by_stream": self.get_revenue_by_stream(start_date, end_date),
            "mrr": self.calculate_monthly_recurring_revenue(),
            "arr": self.calculate_annual_recurring_revenue(),
            "average_revenue_per_user": self._calculate_arpu(start_date, end_date),
            "customer_acquisition_cost": self._calculate_cac(),
            "churn_rate": self._calculate_churn_rate(start_date, end_date)
        }
    
    def _calculate_total_revenue(self, start_date: datetime, end_date: datetime) -> Money:
        """Calculate total revenue for period"""
        return Money(Decimal('0'), Currency.USD)
    
    def _calculate_arpu(self, start_date: datetime, end_date: datetime) -> Money:
        """Calculate Average Revenue Per User"""
        return Money(Decimal('0'), Currency.USD)
    
    def _calculate_cac(self) -> Money:
        """Calculate Customer Acquisition Cost"""
        return Money(Decimal('0'), Currency.USD)
    
    def _calculate_churn_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate churn rate for period"""
        return 0.0


class ComplianceService:
    """
    Domain service for financial compliance and regulatory requirements
    
    Handles KYC, AML, tax reporting, and other compliance operations.
    """
    
    def __init__(
        self,
        account_repository: AccountRepositoryInterface
    ):
        self.account_repository = account_repository
    
    def verify_kyc(self, user_id: int, kyc_data: Dict[str, Any]) -> ComplianceRecord:
        """Verify KYC (Know Your Customer) compliance"""
        
        account = self.account_repository.find_by_user_id(user_id)
        if not account:
            raise ValueError(f"Account for user {user_id} not found")
        
        # Create KYC compliance record
        compliance_record = ComplianceRecord(
            record_id=f"kyc_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            compliance_type="KYC",
            status="approved",  # Simplified - in reality this would be more complex
            created_at=datetime.now(),
            details=kyc_data,
            expiry_date=datetime.now() + timedelta(days=365)  # KYC valid for 1 year
        )
        
        account.add_compliance_record(compliance_record)
        self.account_repository.save(account)
        
        return compliance_record
    
    def check_aml_compliance(self, transaction: TransactionRecord) -> bool:
        """Check Anti-Money Laundering (AML) compliance for transaction"""
        
        # Simplified AML checks
        if transaction.amount.amount > Decimal('10000'):
            # Large transaction - requires enhanced due diligence
            return False
        
        # Check for suspicious patterns
        # This would typically involve more sophisticated analysis
        
        return True
    
    def generate_tax_report(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Generate tax report for user"""
        
        account = self.account_repository.find_by_user_id(user_id)
        if not account:
            raise ValueError(f"Account for user {user_id} not found")
        
        # Calculate tax-relevant transactions
        year_start = datetime(tax_year, 1, 1)
        year_end = datetime(tax_year, 12, 31)
        
        tax_data = {
            "user_id": user_id,
            "tax_year": tax_year,
            "total_income": Money(Decimal('0'), Currency.USD),
            "total_expenses": Money(Decimal('0'), Currency.USD),
            "transaction_count": 0,
            "transactions": []
        }
        
        for transaction in account.transaction_history:
            # Check if transaction is in tax year
            transaction_date = getattr(transaction, 'timestamp', datetime.now())
            if year_start <= transaction_date <= year_end:
                tax_data["transaction_count"] += 1
                tax_data["transactions"].append({
                    "id": transaction.transaction_id,
                    "amount": str(transaction.amount.amount),
                    "currency": transaction.amount.currency.value,
                    "type": transaction.transaction_type,
                    "date": transaction_date.isoformat()
                })
        
        return tax_data
    
    def audit_account(self, account_id: str) -> Dict[str, Any]:
        """Perform compliance audit on account"""
        
        account = self.account_repository.find_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        audit_result = {
            "account_id": account_id,
            "audit_date": datetime.now().isoformat(),
            "compliance_status": "compliant",
            "issues": [],
            "recommendations": []
        }
        
        # Check KYC compliance
        valid_kyc = any(
            record.compliance_type == "KYC" and record.is_valid()
            for record in account.compliance_records
        )
        
        if not valid_kyc:
            audit_result["compliance_status"] = "non_compliant"
            audit_result["issues"].append("Missing or expired KYC verification")
            audit_result["recommendations"].append("Complete KYC verification")
        
        # Check for suspicious transaction patterns
        large_transactions = [
            t for t in account.transaction_history
            if t.amount.amount > Decimal('5000')
        ]
        
        if len(large_transactions) > 10:
            audit_result["issues"].append("High volume of large transactions")
            audit_result["recommendations"].append("Enhanced monitoring recommended")
        
        return audit_result