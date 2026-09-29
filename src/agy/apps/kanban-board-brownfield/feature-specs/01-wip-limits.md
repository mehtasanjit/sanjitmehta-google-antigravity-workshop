Hey, can you add WIP limits to the board?

Our team keeps piling things into "In Progress" and nothing actually gets finished. I'd like each column to have an optional limit on how many cards it can hold.

What I have in mind:

- I can set a limit on a column, or clear it. No limit means the column works exactly like today.
- The column header shows how full it is, something like "In Progress 3 / 3".
- If a column is full, moving a card into it or creating a card in it should be blocked, with a clear message saying why. Nothing should change on the board when that happens.
- Moving a card *out* of a full column, or reordering cards inside it, should still work.
- Cards hidden by the search box still count toward the limit.
- If I set a limit lower than the number of cards already in the column, don't delete or move anything. Just show that it's over the limit and block new cards until it's back under.

Please make sure the rule is enforced on the backend, not only in the UI, and add tests for it. Everything that works today should keep working.
