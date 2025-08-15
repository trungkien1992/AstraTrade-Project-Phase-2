"""
Financial Domain Entities

Rich domain entities for the Financial Domain following DDD patterns.
These entities contain business logic and maintain domain invariants.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import uuid

from value_objects import (
    Money, PaymentMethod, SubscriptionTier, TransactionRecord, BillingPeriod,
    PaymentStatus, Currency, SubscriptionTierType, BillingCycle, RevenueStream,
    PaymentMethodType, ComplianceRecord
)


@dataclass
class DomainEvent:
    """Base class for domain events"""
    event_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Account:
    """
    Financial Account Entity (Aggregate Root)
    
    Manages user's financial account including balance, payment methods,
    and transaction history. Enforces business rules around account limits,
    compliance requirements, and financial operations.
    """
    
    account_id: Optional[str] = None
    user_id: int = 0
    balance: Money = field(default_factory=lambda: Money(Decimal('0'), Currency.USD))
    payment_methods: List[PaymentMethod] = field(default_factory=list)
    transaction_history: List[TransactionRecord] = field(default_factory=list)
    compliance_records: List[ComplianceRecord] = field(default_factory=list)
    account_status: str = "active"  # active, suspended, closed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_account_id(self, account_id: str) -> None:
        """Set account ID (can only be set once)"""
        if self.account_id is not None:
            raise ValueError("Account ID cannot be changed once set")
        self.account_id = account_id
        self._emit_event("account_created", {
            "account_id": account_id,
            "user_id": self.user_id,
            "initial_balance": str(self.balance.amount),
            "currency": self.balance.currency.value
        })
    
    def add_funds(self, amount: Money, transaction_id: str, source: str = "deposit") -> None:
        """Add funds to account balance"""
        if amount.currency != self.balance.currency:
            raise ValueError(f"Cannot add {amount.currency} to {self.balance.currency} account")
        
        if amount.is_zero() or amount.amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.balance = self.balance.add(amount)
        self.updated_at = datetime.now()
        
        # Record transaction
        transaction = TransactionRecord(
            transaction_id=transaction_id,
            amount=amount,
            transaction_type=f"deposit_{source}",
            revenue_stream=RevenueStream.PREMIUM_FEATURES,  # Default classification
            metadata={"source": source, "balance_after": str(self.balance.amount)}
        )
        self.transaction_history.append(transaction)
        
        self._emit_event("funds_added", {
            "amount": str(amount.amount),
            "currency": amount.currency.value,
            "new_balance": str(self.balance.amount),
            "transaction_id": transaction_id,
            "source": source
        })
    
    def withdraw_funds(self, amount: Money, transaction_id: str, destination: str = "withdrawal") -> None:
        """Withdraw funds from account balance"""
        if amount.currency != self.balance.currency:
            raise ValueError(f"Cannot withdraw {amount.currency} from {self.balance.currency} account")
        
        if amount.is_zero() or amount.amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if self.balance.amount < amount.amount:
            raise ValueError("Insufficient funds for withdrawal")
        
        if not self.is_withdrawal_allowed(amount):
            raise ValueError("Withdrawal not allowed due to compliance restrictions")
        
        self.balance = self.balance.subtract(amount)
        self.updated_at = datetime.now()
        
        # Record transaction
        transaction = TransactionRecord(
            transaction_id=transaction_id,
            amount=amount,
            transaction_type=f"withdrawal_{destination}",
            revenue_stream=RevenueStream.PREMIUM_FEATURES,
            metadata={"destination": destination, "balance_after": str(self.balance.amount)}
        )
        self.transaction_history.append(transaction)
        
        self._emit_event("funds_withdrawn", {
            "amount": str(amount.amount),
            "currency": amount.currency.value,
            "new_balance": str(self.balance.amount),
            "transaction_id": transaction_id,
            "destination": destination
        })
    
    def add_payment_method(self, payment_method: PaymentMethod) -> None:
        """Add a new payment method"""
        # Remove primary status from other methods if this one is primary
        if payment_method.is_primary:
            for method in self.payment_methods:
                if method.is_primary:
                    # Create new method without primary status
                    updated_method = PaymentMethod(
                        method_type=method.method_type,
                        identifier=method.identifier,
                        display_name=method.display_name,
                        is_primary=False,
                        expiry_date=method.expiry_date,
                        metadata=method.metadata
                    )
                    # Replace in list
                    index = self.payment_methods.index(method)
                    self.payment_methods[index] = updated_method
        
        self.payment_methods.append(payment_method)
        self.updated_at = datetime.now()
        
        self._emit_event("payment_method_added", {
            "method_type": payment_method.method_type.value,
            "identifier": payment_method.identifier,
            "is_primary": payment_method.is_primary
        })
    
    def remove_payment_method(self, identifier: str) -> None:
        """Remove a payment method by identifier"""
        method = self.get_payment_method(identifier)
        if not method:
            raise ValueError(f"Payment method {identifier} not found")
        
        self.payment_methods.remove(method)
        self.updated_at = datetime.now()
        
        self._emit_event("payment_method_removed", {
            "identifier": identifier,
            "method_type": method.method_type.value
        })
    
    def get_payment_method(self, identifier: str) -> Optional[PaymentMethod]:
        """Get payment method by identifier"""
        for method in self.payment_methods:
            if method.identifier == identifier:
                return method
        return None
    
    def get_primary_payment_method(self) -> Optional[PaymentMethod]:
        """Get the primary payment method"""
        for method in self.payment_methods:
            if method.is_primary:
                return method
        return None
    
    def record_transaction(self, transaction: TransactionRecord) -> None:
        """Record a financial transaction"""
        self.transaction_history.append(transaction)
        self.updated_at = datetime.now()
        
        self._emit_event("transaction_recorded", {
            "transaction_id": transaction.transaction_id,
            "amount": str(transaction.amount.amount),
            "currency": transaction.amount.currency.value,
            "type": transaction.transaction_type,
            "revenue_stream": transaction.revenue_stream.value
        })
    
    def add_compliance_record(self, compliance_record: ComplianceRecord) -> None:
        """Add compliance record for audit trail"""
        self.compliance_records.append(compliance_record)
        self.updated_at = datetime.now()
        
        self._emit_event("compliance_record_added", {
            "record_id": compliance_record.record_id,
            "type": compliance_record.compliance_type,
            "status": compliance_record.status
        })
    
    def suspend_account(self, reason: str) -> None:
        """Suspend account for compliance or security reasons"""
        if self.account_status == "closed":
            raise ValueError("Cannot suspend closed account")
        
        self.account_status = "suspended"
        self.updated_at = datetime.now()
        
        self._emit_event("account_suspended", {
            "reason": reason,
            "suspended_at": self.updated_at.isoformat()
        })
    
    def reactivate_account(self) -> None:
        """Reactivate suspended account"""
        if self.account_status != "suspended":
            raise ValueError("Can only reactivate suspended accounts")
        
        self.account_status = "active"
        self.updated_at = datetime.now()
        
        self._emit_event("account_reactivated", {
            "reactivated_at": self.updated_at.isoformat()
        })
    
    def is_active(self) -> bool:
        """Check if account is active"""
        return self.account_status == "active"
    
    def is_withdrawal_allowed(self, amount: Money) -> bool:
        """Check if withdrawal is allowed based on compliance rules"""
        if not self.is_active():
            return False
        
        # Check compliance records
        valid_kyc = any(
            record.compliance_type == "KYC" and record.is_valid()
            for record in self.compliance_records
        )
        
        # Large withdrawals require KYC
        if amount.amount > Decimal('1000') and not valid_kyc:
            return False
        
        return True
    
    def get_transaction_total(self, transaction_type: str) -> Money:
        """Get total amount for specific transaction type"""
        total = Decimal('0')
        for transaction in self.transaction_history:
            if transaction.transaction_type == transaction_type:
                if transaction.amount.currency == self.balance.currency:
                    total += transaction.amount.amount
        
        return Money(total, self.balance.currency)
    
    def get_monthly_revenue(self, revenue_stream: RevenueStream) -> Money:
        """Get monthly revenue for specific stream"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total = Decimal('0')
        for transaction in self.transaction_history:
            if (transaction.revenue_stream == revenue_stream and 
                hasattr(transaction, 'timestamp') and 
                getattr(transaction, 'timestamp', now) >= month_start):
                if transaction.amount.currency == self.balance.currency:
                    total += transaction.amount.amount
        
        return Money(total, self.balance.currency)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.account_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class Subscription:
    """
    Subscription Entity
    
    Manages user subscriptions including tier, billing, and lifecycle.
    Handles subscription upgrades, downgrades, and cancellations.
    """
    
    subscription_id: Optional[str] = None
    user_id: int = 0
    account_id: str = ""
    current_tier: SubscriptionTier = field(default_factory=lambda: SubscriptionTier(
        tier_type=SubscriptionTierType.FREE,
        name="Free",
        description="Basic features",
        monthly_price=Money(Decimal('0'), Currency.USD),
        yearly_price=Money(Decimal('0'), Currency.USD),
        features=frozenset(["limited_trades"])
    ))
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    current_period: Optional[BillingPeriod] = None
    status: str = "active"  # active, cancelled, expired, suspended
    auto_renew: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_subscription_id(self, subscription_id: str) -> None:
        """Set subscription ID (can only be set once)"""
        if self.subscription_id is not None:
            raise ValueError("Subscription ID cannot be changed once set")
        self.subscription_id = subscription_id
        self._emit_event("subscription_created", {
            "subscription_id": subscription_id,
            "user_id": self.user_id,
            "tier": self.current_tier.tier_type.value,
            "billing_cycle": self.billing_cycle.value
        })
    
    def upgrade_tier(self, new_tier: SubscriptionTier, effective_date: datetime = None) -> None:
        """Upgrade to a higher subscription tier"""
        if effective_date is None:
            effective_date = datetime.now()
        
        if new_tier.tier_type.value <= self.current_tier.tier_type.value:
            raise ValueError("Can only upgrade to higher tier")
        
        old_tier = self.current_tier
        self.current_tier = new_tier
        self.updated_at = datetime.now()
        
        # Create new billing period if needed
        if self.billing_cycle == BillingCycle.MONTHLY:
            price = new_tier.monthly_price
            end_date = effective_date + timedelta(days=30)
        elif self.billing_cycle == BillingCycle.YEARLY:
            price = new_tier.yearly_price
            end_date = effective_date + timedelta(days=365)
        else:
            price = new_tier.yearly_price
            end_date = effective_date + timedelta(days=90)
        
        self.current_period = BillingPeriod(
            cycle=self.billing_cycle,
            start_date=effective_date,
            end_date=end_date,
            amount_due=price
        )
        
        self._emit_event("subscription_upgraded", {
            "old_tier": old_tier.tier_type.value,
            "new_tier": new_tier.tier_type.value,
            "effective_date": effective_date.isoformat(),
            "new_price": str(price.amount),
            "currency": price.currency.value
        })
    
    def downgrade_tier(self, new_tier: SubscriptionTier, effective_date: datetime = None) -> None:
        """Downgrade to a lower subscription tier"""
        if effective_date is None:
            effective_date = datetime.now()
        
        if new_tier.tier_type.value >= self.current_tier.tier_type.value:
            raise ValueError("Can only downgrade to lower tier")
        
        old_tier = self.current_tier
        self.current_tier = new_tier
        self.updated_at = datetime.now()
        
        self._emit_event("subscription_downgraded", {
            "old_tier": old_tier.tier_type.value,
            "new_tier": new_tier.tier_type.value,
            "effective_date": effective_date.isoformat()
        })
    
    def cancel_subscription(self, cancellation_reason: str = "user_request") -> None:
        """Cancel subscription (remains active until period end)"""
        if self.status == "cancelled":
            raise ValueError("Subscription already cancelled")
        
        self.status = "cancelled"
        self.auto_renew = False
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        
        self._emit_event("subscription_cancelled", {
            "reason": cancellation_reason,
            "cancelled_at": self.cancelled_at.isoformat(),
            "expires_at": self.current_period.end_date.isoformat() if self.current_period else None
        })
    
    def renew_subscription(self) -> BillingPeriod:
        """Renew subscription for next billing period"""
        if not self.auto_renew:
            raise ValueError("Auto-renewal is disabled")
        
        if self.status != "active":
            raise ValueError("Can only renew active subscriptions")
        
        # Calculate next billing period
        if self.current_period:
            start_date = self.current_period.end_date
        else:
            start_date = datetime.now()
        
        if self.billing_cycle == BillingCycle.MONTHLY:
            end_date = start_date + timedelta(days=30)
            amount = self.current_tier.monthly_price
        elif self.billing_cycle == BillingCycle.YEARLY:
            end_date = start_date + timedelta(days=365)
            amount = self.current_tier.yearly_price
        else:
            end_date = start_date + timedelta(days=90)
            amount = self.current_tier.yearly_price  # Fallback
        
        new_period = BillingPeriod(
            cycle=self.billing_cycle,
            start_date=start_date,
            end_date=end_date,
            amount_due=amount
        )
        
        self.current_period = new_period
        self.updated_at = datetime.now()
        
        self._emit_event("subscription_renewed", {
            "new_period_start": start_date.isoformat(),
            "new_period_end": end_date.isoformat(),
            "amount_due": str(amount.amount),
            "currency": amount.currency.value
        })
        
        return new_period
    
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != "active":
            return False
        
        if self.current_period:
            return self.current_period.is_current()
        
        return True
    
    def is_expired(self) -> bool:
        """Check if subscription has expired"""
        if not self.current_period:
            return True
        
        return datetime.now() > self.current_period.end_date
    
    def days_until_renewal(self) -> int:
        """Get days until next renewal"""
        if not self.current_period:
            return 0
        
        return self.current_period.days_remaining()
    
    def allows_real_trading(self) -> bool:
        """Check if current tier allows real trading"""
        return self.is_active() and self.current_tier.allows_real_trading()
    
    def get_trade_limit(self) -> Optional[int]:
        """Get daily trade limit for current tier"""
        if not self.is_active():
            return 0
        
        return self.current_tier.get_trade_limit()
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.subscription_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class Payment:
    """
    Payment Entity
    
    Represents a single payment transaction with full lifecycle management.
    Handles payment processing, status updates, and failure handling.
    """
    
    payment_id: Optional[str] = None
    account_id: str = ""
    amount: Money = field(default_factory=lambda: Money(Decimal('0'), Currency.USD))
    payment_method: Optional[PaymentMethod] = None
    status: PaymentStatus = PaymentStatus.PENDING
    payment_type: str = "subscription"  # subscription, one_time, refund
    reference_id: Optional[str] = None  # subscription_id, invoice_id, etc.
    processor_transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_payment_id(self, payment_id: str) -> None:
        """Set payment ID (can only be set once)"""
        if self.payment_id is not None:
            raise ValueError("Payment ID cannot be changed once set")
        self.payment_id = payment_id
        self._emit_event("payment_created", {
            "payment_id": payment_id,
            "amount": str(self.amount.amount),
            "currency": self.amount.currency.value,
            "type": self.payment_type
        })
    
    def process_payment(self, processor_transaction_id: str) -> None:
        """Mark payment as processing"""
        if self.status != PaymentStatus.PENDING:
            raise ValueError(f"Cannot process payment with status {self.status}")
        
        self.status = PaymentStatus.PROCESSING
        self.processor_transaction_id = processor_transaction_id
        self.processed_at = datetime.now()
        
        self._emit_event("payment_processing", {
            "processor_transaction_id": processor_transaction_id,
            "processed_at": self.processed_at.isoformat()
        })
    
    def complete_payment(self) -> None:
        """Mark payment as completed successfully"""
        if self.status != PaymentStatus.PROCESSING:
            raise ValueError("Can only complete processing payments")
        
        self.status = PaymentStatus.COMPLETED
        
        self._emit_event("payment_completed", {
            "completed_at": datetime.now().isoformat(),
            "amount": str(self.amount.amount),
            "currency": self.amount.currency.value
        })
    
    def fail_payment(self, reason: str) -> None:
        """Mark payment as failed"""
        if self.status in [PaymentStatus.COMPLETED, PaymentStatus.REFUNDED]:
            raise ValueError(f"Cannot fail payment with status {self.status}")
        
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        
        self._emit_event("payment_failed", {
            "failure_reason": reason,
            "failed_at": datetime.now().isoformat()
        })
    
    def cancel_payment(self) -> None:
        """Cancel pending payment"""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Can only cancel pending payments")
        
        self.status = PaymentStatus.CANCELLED
        
        self._emit_event("payment_cancelled", {
            "cancelled_at": datetime.now().isoformat()
        })
    
    def refund_payment(self, refund_amount: Optional[Money] = None) -> None:
        """Process refund for completed payment"""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")
        
        if refund_amount is None:
            refund_amount = self.amount
        
        if refund_amount.amount > self.amount.amount:
            raise ValueError("Refund amount cannot exceed original payment")
        
        self.status = PaymentStatus.REFUNDED
        
        self._emit_event("payment_refunded", {
            "refund_amount": str(refund_amount.amount),
            "currency": refund_amount.currency.value,
            "refunded_at": datetime.now().isoformat()
        })
    
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.COMPLETED
    
    def is_pending(self) -> bool:
        """Check if payment is still pending"""
        return self.status == PaymentStatus.PENDING
    
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED
    
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded"""
        return self.status == PaymentStatus.COMPLETED
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.payment_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass
class Invoice:
    """
    Invoice Entity
    
    Represents billing invoice with line items and payment tracking.
    Handles invoice generation, payment application, and status management.
    """
    
    invoice_id: Optional[str] = None
    account_id: str = ""
    subscription_id: Optional[str] = None
    amount_due: Money = field(default_factory=lambda: Money(Decimal('0'), Currency.USD))
    amount_paid: Money = field(default_factory=lambda: Money(Decimal('0'), Currency.USD))
    status: str = "draft"  # draft, sent, paid, overdue, cancelled
    due_date: Optional[datetime] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    payments: List[str] = field(default_factory=list)  # payment_ids
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Domain event storage
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def set_invoice_id(self, invoice_id: str) -> None:
        """Set invoice ID (can only be set once)"""
        if self.invoice_id is not None:
            raise ValueError("Invoice ID cannot be changed once set")
        self.invoice_id = invoice_id
        self._emit_event("invoice_created", {
            "invoice_id": invoice_id,
            "amount_due": str(self.amount_due.amount),
            "currency": self.amount_due.currency.value
        })
    
    def add_line_item(self, description: str, amount: Money, quantity: int = 1) -> None:
        """Add line item to invoice"""
        if self.status != "draft":
            raise ValueError("Can only add line items to draft invoices")
        
        line_item = {
            "description": description,
            "amount": amount,
            "quantity": quantity,
            "total": amount.multiply(Decimal(quantity))
        }
        
        self.line_items.append(line_item)
        
        # Recalculate total
        total = Money(Decimal('0'), self.amount_due.currency)
        for item in self.line_items:
            total = total.add(item["total"])
        self.amount_due = total
    
    def send_invoice(self) -> None:
        """Send invoice to customer"""
        if self.status != "draft":
            raise ValueError("Can only send draft invoices")
        
        if self.amount_due.is_zero():
            raise ValueError("Cannot send invoice with zero amount")
        
        self.status = "sent"
        self.sent_at = datetime.now()
        
        if not self.due_date:
            self.due_date = datetime.now() + timedelta(days=30)
        
        self._emit_event("invoice_sent", {
            "sent_at": self.sent_at.isoformat(),
            "due_date": self.due_date.isoformat(),
            "amount_due": str(self.amount_due.amount)
        })
    
    def apply_payment(self, payment_id: str, payment_amount: Money) -> None:
        """Apply payment to invoice"""
        if self.status not in ["sent", "overdue"]:
            raise ValueError("Can only apply payments to sent or overdue invoices")
        
        if payment_amount.currency != self.amount_due.currency:
            raise ValueError("Payment currency must match invoice currency")
        
        # Add payment
        self.payments.append(payment_id)
        self.amount_paid = self.amount_paid.add(payment_amount)
        
        # Update status if fully paid
        if self.amount_paid.amount >= self.amount_due.amount:
            self.status = "paid"
            self.paid_at = datetime.now()
            
            self._emit_event("invoice_paid", {
                "paid_at": self.paid_at.isoformat(),
                "total_paid": str(self.amount_paid.amount)
            })
        else:
            self._emit_event("payment_applied", {
                "payment_id": payment_id,
                "payment_amount": str(payment_amount.amount),
                "remaining_balance": str(self.get_balance_due().amount)
            })
    
    def mark_overdue(self) -> None:
        """Mark invoice as overdue"""
        if self.status != "sent":
            raise ValueError("Can only mark sent invoices as overdue")
        
        if not self.is_overdue():
            raise ValueError("Invoice is not past due date")
        
        self.status = "overdue"
        
        self._emit_event("invoice_overdue", {
            "due_date": self.due_date.isoformat(),
            "amount_overdue": str(self.get_balance_due().amount)
        })
    
    def cancel_invoice(self) -> None:
        """Cancel invoice"""
        if self.status == "paid":
            raise ValueError("Cannot cancel paid invoice")
        
        self.status = "cancelled"
        
        self._emit_event("invoice_cancelled", {
            "cancelled_at": datetime.now().isoformat()
        })
    
    def get_balance_due(self) -> Money:
        """Get remaining balance due"""
        return self.amount_due.subtract(self.amount_paid)
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if not self.due_date or self.status == "paid":
            return False
        return datetime.now() > self.due_date
    
    def is_paid(self) -> bool:
        """Check if invoice is fully paid"""
        return self.status == "paid"
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit domain event"""
        event = DomainEvent(
            event_type=event_type,
            entity_id=self.invoice_id or "unknown",
            data=data
        )
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events