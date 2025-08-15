"""
Financial Domain

Handles payments, subscriptions, revenue tracking, and financial compliance
as defined in ADR-001 Domain-Driven Design implementation.

This domain manages:
- Payment processing for subscriptions and one-time purchases
- Revenue tracking and analytics across the 4 revenue streams
- Subscription management for premium tiers
- Financial compliance and audit trails
- Integration with payment processors and blockchain

Domain Structure:
- value_objects.py: Money, PaymentMethod, SubscriptionTier, etc.
- entities.py: Account, Subscription, Payment, Invoice
- services.py: PaymentService, SubscriptionService, RevenueService
- events.py: Domain events for financial operations

Integration Points:
- User Domain: Connects to user verification tiers and premium features
- Trading Domain: Enables real money trading for verified users
- NFT Domain: Handles marketplace transactions and NFT purchases
"""

__version__ = "1.0.0"
__domain__ = "financial"