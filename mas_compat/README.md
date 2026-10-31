# AUTO-MAS compatible MFABD2 releases

Upstream: https://github.com/sunyink/MFABD2

This fork republishes upstream Windows x64 release ZIPs for AUTO-MAS. Game logic, assets and dependencies are retained. Only the PC pretask interpreter path, GitHub update source, MirrorChyan resource ID and version string are adjusted. The packaged provenance records the original release and SHA256.

Actions checks every 30 minutes and publishes the upstream Latest stable release and newest supported beta. The upstream-main branch tracks source separately; main keeps compatibility automation. No upstream PRs, writes or notifications are made. Inherited workflows are disabled in this fork.

If package layout changes or validation fails, publication stops and the previous release remains available. GitHub may suspend scheduled workflows after prolonged inactivity; re-enable Actions if needed.

AUTO-MAS: use GitHub as download source and beta channel for PC support.

Initial fork commit: 9d7dc75af483ecdf67680b16f446541204489d58.
