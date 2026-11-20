# Security policy

## Supported versions

Only the latest release gets fixes.

## Reporting a vulnerability

Please report it privately through
[GitHub's private vulnerability reporting](https://github.com/jpcunhadias/typeup/security/advisories/new),
not in a public issue. Include the smallest note or `.tex` file that shows
it and the command you ran.

You should get an answer within a week. Once a fix is released, the
advisory is published with credit to you, unless you prefer otherwise.

## Scope

typeup runs pandoc and LaTeX on files you give it. Treat notes and `.tex`
files from other people like code: LaTeX can read files, and `typeup tex`
turns on `-shell-escape` for documents that use `minted`, which lets the
document run commands.
