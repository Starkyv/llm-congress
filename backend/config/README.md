# Agent Configuration System

## Overview
The debate system uses a JSON configuration file to dynamically create agents. This allows you to:
- Add/remove agents without changing code
- Customize agent personalities and behaviors
- Create different debate scenarios
- Easily test different agent compositions

## Configuration File Structure

### File Location
`config/agent_config.json`

### Structure
```json
{
  "debate_config": {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "streaming": true,
    "max_tokens": 1000
  },
  "proposition_agents": [ /* array of agent configs */ ],
  "opposition_agent": { /* single agent config */ },
  "moderator_agent": { /* single agent config */ }
}
```

### Agent Configuration Fields

Each agent must have:
- **id**: Unique identifier (string, no spaces)
- **name**: Display name for the agent
- **personality_type**: Short descriptor of personality
- **behavior**: Detailed behavioral instructions (system prompt)
- **temperature**: (optional) Override default temperature

## Creating Custom Agents

### Step 1: Define Agent Personality
Think about:
- What's their arguing style?
- What do they value?
- How do they present arguments?
- What makes them unique?

### Step 2: Write Behavior Description
Be specific about:
- Argument structure
- Language style
- Types of evidence they use
- How they respond to opponents

### Step 3: Add to Config
```json
{
  "id": "prop_creative",
  "name": "Creative Debater",
  "personality_type": "creative",
  "behavior": "Your detailed behavioral description here...",
  "temperature": 0.8
}
```

## Example Configurations

### Minimal (3 Agents)
See: `agent_config.example_3agents.json`
- Good for: Quick tests, simple debates
- Pros: Faster, clearer roles
- Cons: Less variety

### Standard (5 Agents)
See: `agent_config.json`
- Good for: Most debates, balanced variety
- Pros: Good variety without overwhelm
- Cons: May still feel repetitive

### Large (10+ Agents)
See: `agent_config.example_10agents.json`
- Good for: Long debates, exploring many angles
- Pros: Maximum variety, comprehensive coverage
- Cons: Longer debates, more complex to manage

## Switching Configurations

### Method 1: Manual
```bash
cp config/agent_config.example_3agents.json config/agent_config.json
```

### Method 2: Using Utility
```bash
python switch_config.py
```

## Validation

Always validate after creating/modifying config:
```bash
python validate_config.py
```

This checks:
- JSON syntax
- Required fields
- Agent structure
- Displays summary

## Tips for Good Agent Configurations

1. **Distinct Personalities**: Make each agent clearly different
2. **Balanced Temperature**: 0.5-0.6 for consistent, 0.8-0.9 for creative
3. **Clear Behaviors**: Be explicit about style and approach
4. **Reasonable Count**: 3-7 proposition agents is usually optimal
5. **Test Individually**: Use `test_agent.py` to verify each agent
6. **Diverse Perspectives**: Include different reasoning styles

## Troubleshooting

**"Missing required field" error**
- Check all agents have: id, name, personality_type, behavior

**Agents sound too similar**
- Make behaviors more specific and distinct
- Adjust temperatures more dramatically

**Debate too long**
- Reduce number of proposition agents
- Decrease exchanges_per_round in workflow

**Votes always tied**
- Ensure even number of proposition agents
- Make agent personalities more opinionated

