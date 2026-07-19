# Code Review Rules

## Security
- All DB queries must use parameterised inputs. Never concatenate user input into SQL.
- Never log request bodies that may contain PII.

## Error Handling
- All external API calls must have explicit timeout values.
- Never catch bare Exception silently.

## Style
- All functions must have a docstring.