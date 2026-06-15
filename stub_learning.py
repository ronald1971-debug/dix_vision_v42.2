import re

with open('ui/server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the _build_learning_evolution_loops method and replace it
pattern = r'(    def _build_learning_evolution_loops\(self\) -> None:.*?)(    def _live_freeze_policy\(self\) -> LearningEvolutionFreezePolicy:)'
match = re.search(pattern, content, re.DOTALL)

if match:
    old_method = match.group(1)
    new_method = '''    def _build_learning_evolution_loops(self) -> None:
        """P1.2 — ``_State.__init__`` section: learning_evolution_loops."""

        # STUB: Skip learning/evolution loops to prevent hanging during boot
        self.slow_loop_learner = None
        self.update_emitter = None
        self._closed_loop_sample_builder = None
        self._closed_loop_update_builder = None
        self.closed_learning_loop = None
        self.patch_outcome_feedback = None
        self.mutation_proposer = None
        self.patch_pipeline = None
        self.patch_approval_bridge = None
        self.patch_pipeline_orchestrator = None
        self.structural_evolution_loop = None

        # Skip background tickers
        # Skip cognitive telemetry

'''
    content = content.replace(old_method, new_method)
    with open('ui/server.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Successfully replaced _build_learning_evolution_loops method')
else:
    print('Pattern not found')
