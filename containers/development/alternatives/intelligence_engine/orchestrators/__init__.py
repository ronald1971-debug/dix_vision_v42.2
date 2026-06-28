"""Agent orchestration layer — peer coordination for AGT-XX agents.

The orchestrators live *above* the meta-controller: they decide which
agents participate, fan signals to them, and fuse their decisions.
The meta-controller still owns sizing / timing / fallback.
"""
