with open('ui/cockpit_routes.py') as f:
    lines = f.readlines()

# Insert at line 113 (index 112 in 0-indexed)
insert_index = 112

new_models = '''    # Phase 11.1 Pydantic models
    class OrderSubmitIn(BaseModel):
        symbol: str
        side: str
        quantity: float
        order_type: str
        price: float | None = None
        time_in_force: str = "GTC"
        operator_id: str = "operator"
        reason: str = ""

    class OrderCancelIn(BaseModel):
        order_id: str
        operator_id: str = "operator"
        reason: str = ""

    class OrderCancelAllIn(BaseModel):
        symbol: str | None = None
        operator_id: str = "operator"
        reason: str = ""

    class StrategyActionIn(BaseModel):
        strategy_id: str
        operator_id: str = "operator"
        reason: str = ""

    class PositionCloseIn(BaseModel):
        position_id: str
        operator_id: str = "operator"
        reason: str = ""

    class LedgerReplayIn(BaseModel):
        from_sequence: int
        to_sequence: int | None = None
        stream: str = ""

'''

lines.insert(insert_index, new_models)

with open('ui/cockpit_routes.py', 'w') as f:
    f.writelines(lines)

print('Models inserted at line', insert_index + 1)
