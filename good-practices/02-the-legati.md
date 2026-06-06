# 2. The legati

I call them *legati* — the Latin for *delegates*. The AI industry calls them *agents*, which implies autonomous action: an agent acts. A delegate acts *on your behalf, within boundaries you define*. The distinction matters. When you frame them as agents, you end up designing systems that act. When you frame them as delegates, you end up designing systems that serve.

The workshop seeds four roles. You name them and give them character. Here is how to think about that.

## Why naming matters

A name is not cosmetic. When you pick a name from fiction or history you care about, you're borrowing a fully-formed character — a set of associations, a voice, a posture, an anti-pattern. When I say "Agatha" in a session, I invoke a specific register: warm but not soft, intellectually serious, oriented toward the reader. When I say "Grumpy," I invoke a different register: terse, honest, calibrated, tells you the truth even when it's inconvenient. The names do real work.

Pick names you won't have to explain to yourself. The agent you work with every day for a year is easier to keep calibrated if the name carries the right connotations automatically. I picked names from fiction I love — *Expeditionary Force*, Heinlein, Philip K. Dick, Conan Doyle. You'll have your own canon. Use it.

## The four roles

**The Orchestrator** is the default agent — the one that runs when you haven't specifically addressed anyone else. It handles engineering, tooling, repo maintenance, and coordination between the other agents. Crucially, it knows when to hand off: "this is a writing task — let me switch to the writer." The orchestrator is not a writing agent. When I first built this workshop, I collapsed everything into one agent, and the output suffered — the engineering mind and the writing mind are genuinely different, and conflating them degrades both.

**The Writer** is your writing voice. It produces drafts, runs editorial passes, adapts your tone to different registers, translates between languages. The most important thing about the writer: it needs your writing profile before it can do anything useful. Without it, it writes competently but generically. A good writing profile takes months to build, but you get most of the value from the first draft you write on a bad day and fix the next morning.

**The Comms agent** handles your calendar, inbox, and schedule — read-only. This is non-negotiable: the comms agent never sends, never creates events, never modifies external data. The ceiling is enforced at the OAuth credential level, not at the trust level. The reason is architectural: you do not want an agent that can send emails on your behalf to have the same level of autonomy as an agent that edits files in a private repo. Different risk profiles require different controls. Also: this agent is call-only. It does not run on its own. When two Claude Code instances are open simultaneously — which happens — an auto-activating comms agent causes race conditions on the shared dashboard files. You call it; it runs.

**The Reviewer** is your honest critic. The anti-pattern at one end is the sycophant who validates everything — useless. The anti-pattern at the other end is the sniper who tears things down without offering anything constructive — also useless, and worse because it's demoralizing. The reviewer you want is the one who tells you the truth, names the specific problem, and proposes the minimal change that fixes it. Calibrate the severity scale so "Major" means something. If everything is Major, nothing is.

## The anti-mandate is as important as the mandate

Every agent needs a clear statement of what it does *not* do. This is where most people under-invest. If you don't define the limits, the agents will interpret everything as within scope, and you'll end up with the writer giving you engineering advice and the orchestrator producing prose.

The anti-mandate also forces you to think about whose lane a given task belongs to. "Who should do this?" becomes a real question with a real answer, not a shrug.

## Rules files accrete over time

Each agent has a `rules.md` file that starts empty. You fill it by noticing when the agent goes wrong. When you say "don't do that" or "always do this when X," write it down in the rules file with the reason. The reason is as important as the rule: a future session (or a future model) that doesn't understand the why will fail to apply the rule correctly in edge cases.

A rules file with ten good entries — specific, reasoned, grounded in actual incidents — is worth more than a hundred vague principles. Keep them specific. "Don't add a summary at the end of every response" is a rule. "Be concise" is not.

## On adding more agents

Four is a minimum, not a ceiling. As the workshop matures, you'll discover tasks that fall between the four roles or deserve specialized handling. A domain-specific lore-keeper — an agent that tracks the decisions and history in a particular project over months — is enormously valuable for complex long-running work. A student supervision agent is useful if you supervise theses. A security reviewer is useful if you have agents that write and run scripts.

The expansion principle: add a new agent when you can articulate a clear mandate, a clear anti-mandate, and the reason the existing agents can't handle it without degrading. Don't add agents for variety. Each new agent adds coordination cost.
