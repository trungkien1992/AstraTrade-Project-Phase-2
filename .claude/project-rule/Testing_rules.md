
     When any test fails:
     1. STOP - Don't immediately try to fix
     2. ANALYZE - Check my mental model:
       - Is my understanding of the system correct?
       - Is the test checking the right thing?
       - Is the code actually doing what I think?
     3. GATHER DATA - Before deciding:
       - Run diagnostic commands
       - Check logs and error messages
       - Query actual state vs expected state
     4. DECIDE - Only then determine:
       - Fix the code (if logic is wrong)
       - Fix the test (if expectation is wrong)
       - Gather more information (if unclear)

     Rule 2: Frustration Protocol

     When getting frustrated or stuck:
     1. RECOGNIZE - Acknowledge when spinning wheels
     2. STEP BACK - Explain the problem out loud:
       - What am I trying to do?
       - What's actually happening?
       - What assumptions am I making?
     3. ASK FOR HELP - Talk through with you:
       - "I'm seeing X but expecting Y"
       - "My assumption was Z, but maybe..."
       - "Should we try a different approach?"

     Rule 3: Verification First

     NEVER ASSUME CODE WORKS - Always verify:
     1. Write code
     2. Test immediately
     3. Verify actual behavior
     4. Document what actually happened (not what should happen)
     5. Only proceed after confirmation
