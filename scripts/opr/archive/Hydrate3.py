import mysql.connector

# --- 1. CONFIGURATION (Update your password here) ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Warhammer40K!", 
    "database": "wargaming_erp"
}

def hydrate_core_opr_rules():
    core_rules = {
        "Aircraft": "May only use Advance actions (+30”). Ignore units/terrain when moving. Can't seize objectives or be charged. Units targeting get -12” to range.",
        "Ambush": "Set aside before deployment. Start of any round after the first, deploy anywhere over 9” from enemies. Can't seize objectives on the round they deploy.",
        "AP": "Targets get -X to Defense rolls when blocking hits from weapons with this special rule.",
        "Artillery": "May only use Hold actions. Over 9\" away: +1 to hit rolls. Enemies shooting at this model from over 9\" away get -2 to hit rolls.",
        "Bane": "Ignores Regeneration. Target must re-roll unmodified Defense results of 6.",
        "Blast": "Ignores cover. Each hit is multiplied by X, up to as many hits as models in the target unit.",
        "Caster": "Gets X spell tokens per round. Spend tokens to cast spells on 4+. Models within 18” can spend tokens to give caster +1/-1 to the roll.",
        "Counter": "Strikes first when charged. Charging unit gets -1 total Impact rolls per model with Counter.",
        "Deadly": "Assign each wound to one model and multiply it by X. Resolved first; wounds don't carry over.",
        "Fast": "Move +2” when using Advance and +4” when using Rush/Charge.",
        "Fear": "Counts as having dealt +X wounds when checking who won melee.",
        "Fearless": "When failing a morale test, roll a die. On a 4+ it counts as passed instead.",
        "Flying": "May move through units and terrain, and ignore terrain effects whilst moving.",
        "Furious": "When charging, unmodified results of 6 to hit in melee deal 1 extra hit.",
        "Hero": "May deploy as part of a multi-model unit. May take morale tests for the unit. Use unit's Defense until all other models are killed.",
        "Immobile": "May only use Hold actions.",
        "Impact": "Roll X dice when charging (unless fatigued). For each 2+ the target takes one hit.",
        "Indirect": "-1 to hit when shooting after moving. May target enemies not in line of sight; ignores cover from sight obstructions.",
        "Limited": "Weapon may only be used once per game.",
        "Regeneration": "When taking wounds, roll a die for each. On a 5+ it is ignored.",
        "Relentless": "Shooting over 9\" away: unmodified results of 6 to hit deal 1 extra hit.",
        "Reliable": "Models attacks at Quality 2+ with this weapon. Still affected by modifiers/fatigue.",
        "Rending": "Ignores Regeneration. Unmodified results of 6 to hit get AP(+4).",
        "Scout": "After all others deploy, may deploy anywhere fully within 12” of their deployment zone.",
        "Slow": "Move -2” when using Advance, and -4” when using Rush/Charge.",
        "Stealth": "When shot from over 9\" away, enemy units get -1 to hit rolls.",
        "Strider": "May ignore the effects of difficult terrain when moving.",
        "Surge": "Unmodified results of 6 to hit deal 1 extra hit.",
        "Takedown": "May pick any model in target unit as individual target. Resolved as unit of before other weapons.",
        "Thrust": "When charging, gets +1 to hit rolls and AP(+1) in melee.",
        "Tough": "Must take X wounds before being killed. Wounds are assigned to Tough models first in mixed units. Heroes assigned wounds last.",
        "Transport": "May transport X models. Heroes/Models up to Tough(6) occupy 1 space; non-Heroes Tough(3) occupy 3 spaces. Units may enter/exit via move actions (within 6\"). If destroyed, units take Dangerous Terrain test and are Shaken.",
        "Unstoppable": "Ignores Regeneration, and ignores all negative modifiers to this weapon."
    }

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Modern SQL Alias Syntax
        sql = """
            INSERT INTO opr_specialrules (rule_id, name, description) 
            VALUES (%s, %s, %s)
            AS alias
            ON DUPLICATE KEY UPDATE description = alias.description
        """

        count = 0
        for name, desc in core_rules.items():
            rule_id = f"core_{name.lower()}"
            cursor.execute(sql, (rule_id, name, desc))
            count += 1

        conn.commit()
        print(f"✅ Successfully hydrated {count} Core OPR rules!")
        
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    hydrate_core_opr_rules()

