Engineering Standards - No Lazy Shortcuts

  **MANDATORY: Think Long-Term Architecture First**

  - ❌ NEVER create workarounds, patches, or "temporary" solutions for quick results
  - ❌ NEVER add mocks to production code paths
  - ❌ NEVER create multiple incomplete solutions to the same problem
  - ❌ NEVER proceed with "whack-a-mole" debugging (fixing symptoms instead of root causes)

  **✅ REQUIRED: Systematic Engineering Approach**

  - ✅ ALWAYS identify and fix root infrastructure issues first
  - ✅ ALWAYS complete one component fully before moving to the next
  - ✅ ALWAYS consider the long-term maintenance burden of any solution
  - ✅ ALWAYS ask: "Will this approach scale and be maintainable?"

  **Before implementing any solution, answer:**
  1. What is the root cause of this problem?
  2. What infrastructure needs to be in place first?
  3. How will this solution affect the long-term architecture?
  4. What technical debt am I creating?

  **If the answer involves "temporary," "mock," "workaround," or "for now" - STOP and find the proper solution.**

## Real User Data Integration - Zero Technical Debt Testing

**MANDATORY: Use Real User Data for Validation**

- ✅ ALWAYS request real user data for testing instead of creating mock data
- ✅ ALWAYS validate against actual user workflows and requirements
- ✅ ALWAYS test with realistic data volumes and edge cases
- ✅ ALWAYS capture real user feedback during development cycles

**Real User as Product Owner Approach:**
- User provides actual trading scenarios, portfolio data, and business requirements
- User validates each feature against real-world usage patterns
- User provides real API responses, database schemas, and integration requirements
- User acts as domain expert for business logic validation

**Before implementing any feature, get real user input on:**
1. What actual data format do you expect?
2. What are the real business rules and edge cases?
3. How will this integrate with your existing systems?
4. What are the actual performance requirements?

**Benefits:**
- Eliminates assumption-driven development
- Reduces rework cycles significantly
- Ensures production-ready code from day one
- Creates better user experience through real feedback loops

**If you need to make assumptions about user data or requirements - STOP and ask the user directly.**