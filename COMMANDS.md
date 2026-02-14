# Memory Commands

Nova supports natural language memory management commands.

These are implemented in `mem/memory_commands.py`. fileciteturn1file1

## List
Examples:
- `List my memories`
- `Show all memories`
- `What do you remember about me?`

Output is grouped by category with dates. fileciteturn1file11

## Search
Examples:
- `Search for memories about coffee`
- `Find memories about my projects`

Returns matches with similarity score. fileciteturn1file11

## Count
Examples:
- `How many memories do you have?`
- `Memory count`

Returns total + breakdown by category. fileciteturn1file11

## Forget (semantic delete)
Examples:
- `Forget that I like pizza`
- `Delete the memory about my job`

Uses semantic matching and deletes any above threshold (default 0.85). fileciteturn1file5

## Clear all
Examples:
- `Forget everything`
- `Delete all my memories`

Deletes all memories for the user. fileciteturn1file5
