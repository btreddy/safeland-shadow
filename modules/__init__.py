class Brain:
    def __init__(self, role_id="1"):
        # ... (Your API Key Setup stays the same) ...

        # Load Persona and the SPECIFIC Memory for that role
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        self.memory = SmartMemory(role_id=role_id) # Pass role_id here

        # ... (Your Model Priority stays the same) ...