Build A v0 Gamified Perps Trading App, Using The Extended API

by
StarkWare


Bounty

Submissions Open

Details
Gamified perps mobile app

RFP by Starkware



Introduction

Starkware is looking for mobile-first developers wanting to build a gamified mobile app for trading perpetuals, built on Starknet, using Extended's API in the backend, with the goal of creating a sustainable business. The goal is to make trading accessible to everyone, not just crypto-native traders but anyone with a phone. The app makes trading fast, fun, and intuitive by combining Pokémon GO/Duolingo-type gaming mechanics (e.g., scheduled rewards, levels, streak-based XP, leaderboard, smooth UI components, building a collection of earned rewards, social and competitive features, etc.) and perpetual trading. The app is not just another gamified DeFi app with confetti and bright colors. It brings perps trading to everyone.



This RFP is structured as a time-bound open bounty, available to all. After the submission deadline, we will evaluate the submitted v0s and select the team whose prototype best meets the outlined requirements. The selected team will be rewarded for their work and invited to continue the project beyond the initial scope. While only one team will be formally chosen to advance, we remain eager to collaborate with other motivated teams who demonstrate strong potential and a desire to work closely with StarkWare.




We look for:

A basic v0 that showcases your skills as a team. 

Design proposals for the frontend. How gamified can this app be (e.g., streak-based XP, leaderboard, levels, daily reminders, scheduled rewards, etc.)? 

A dedicated team that wants to take full ownership of this idea.

Extended API integration for running perpetuals in the backend.



What we offer:

Financial support is provided if proven motivated and successful.

Support for integrating the Extended API.

Idea advisorship.

Full ownership of the idea.



User archetype:

TikTok Generation (18-28): Gen-Z crypto-curious users who are reward-driven, mobile-first, and care more about vibes and status than reading charts.

Degens and Casual Traders: Want quick hits of excitement, and love bragging rights.



Feature ideas/notes/wishlist:
View the following bullet points as features that will make the app UX friendly and potentially go viral. Not all features must be added to the v0/POC, but these give you an idea of the app’s vision.

Use native iOS and Android features (e.g., widgets, push notifications, shortcuts, Haptic Feedback Engine, present real-time information on the lock screen, etc.).

Remove 80% of UI complexity,  make it feel like Snapchat or BeReal. Make the UX feel alive, instant XP, haptics, and visual feedback. Not cluttered by charts or noise. Simple actions that feel like a snap or locket. Implement a reward loop for users to come back.

Simplify the trading experience and come up with creative trading actions. The goal is to make the UX as smooth as possible. Users should not feel the burden of trading but rather the excitement of placing bets. 

Each user has a castle, a garden, or a mini-planet. Each trade helps cultivate this ecosystem. Worse trades harm the user’s ecosystem. Bad traders don’t completely lose their ecosystem; it rebuilds over time, encouraging them to stay. Provide basic (NFA) trading strategies and tips to support less successful traders.

Users should be able to meme about their wins/losses online and share their performance with online communities. Each unique trade, which can be set based on the trade amount (i.e., X traded +$50), number of trades in a day, cumulative wins, streaks, etc., is collected as an NFT, representing a milestone. This NFT can be added to their ecosystem (castle/garden/mini-planet) to enrich it. Users compare their ecosystems online, which gives the user a shareable reputation as a trader.

Every action (trade, copy-trade, invite, streak) gives XP. Leveling up is a flex and unlocks visual graphics. Leveling up increases the user’s position in the leaderboard. It also grants them NFTs that can be added to their ecosystem (castle/garden/mini-planet).

Users can join clans/alliances and challenge their friends in trades. Users must stay consistent with trading against their friends, or else they lose the battle. 

Free-to-play/mock trading for the first trades, which earns users rare NFTs (similar to how users earn rare Pokémon cards when they first start playing Pokémon TCG pocket). Users can only continue playing/trading/growing their ecosystem if they use real currencies. 

Onboarding includes a simple step-by-step gamified tutorial when the user opens the app. Users don’t trade real money. They win XP, grow their ecosystem, and get a taste of the app.



Tech stack:

Extended API to trade the perpetuals. Note: given Extended’s migration from StarkEx to public Starknet starting the first half of July 2025, the API will remain the same, apart from the signed payloads.

Starknet.dart mobile SDK.

Cairo-lang for writing NFT contracts and for the points system leaderboard. Contracts are deployed on Starknet.

No gas fees, the Starknet paymaster is integrated to sponsor the user’s fees. 



v0/POC includes:

A frontend design proposal.

A mobile-first frontend built with Starknet.dart.

Basic integration with the Extended API (place one real trade).

XP tracking for trades and streaks.

A basic leaderboard.

Free-to-play mode/mock trades (optional).

Paymaster integration to remove gas fees.



Funding and revenue potential:

Fast track access to the Starkware and the Starknet Foundation’s grants programs. Up to $25k for seed grants and up to $1m for growth grants (if the app has high potential). 

As Extended perpetual is used in the backend, the building team and Extended can agree upon a revenue-sharing model.

We’ll support long-term builders to go from MVP to a full product.



IP and Ownership:

You retain full ownership of the frontend and design you create.

Code can be open or closed source, up to you.

Starkware will provide design feedback and technical support, but won't claim rights to the app.

