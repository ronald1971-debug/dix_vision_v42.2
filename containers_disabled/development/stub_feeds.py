import re

with open("ui/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the _build_live_feeds method and replace it
# We'll use regex to find the method boundaries
pattern = r"(    def _build_live_feeds\(self\) -> None:.*?)(    def _build_learning_evolution_loops\(self\) -> None:)"
match = re.search(pattern, content, re.DOTALL)

if match:
    old_method = match.group(1)
    new_method = '''    def _build_live_feeds(self) -> None:
        """P1.2 — ``_State.__init__`` section: live_feeds."""

        # STUB: Skip live feed initialization to prevent hanging during boot
        # Create empty deque buffers for compatibility
        self.recent_launches: deque[dict[str, Any]] = deque(maxlen=200)
        self.recent_pool_snapshots: deque[dict[str, Any]] = deque(maxlen=500)

        # Stub feed runners as None - feeds disabled
        self.binance_feed = None
        self.news_index = None
        self.opennews_server = None
        self.coindesk_feed = None
        self.pumpfun_feed = None
        self.raydium_feed = None

        # Bind empty feed runners dict to plugin registry
        self.plugin_registry.feed_runners = {}

'''
    content = content.replace(old_method, new_method)
    with open("ui/server.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Successfully replaced _build_live_feeds method")
else:
    print("Pattern not found")
