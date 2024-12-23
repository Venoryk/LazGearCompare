# config/constraints.py

# Available character classes
CLASSES = [
    "Bard", "Beastlord", "Berserker", "Cleric", "Druid", "Enchanter",
    "Magician", "Monk", "Necromancer", "Paladin", "Ranger", "Rogue",
    "Shadow Knight", "Shaman", "Warrior", "Wizard"
]

# Equipment slots
SLOTS = [
    "Charm", "Left Ear", "Head", "Face", "Right Ear", "Neck", "Shoulder",
    "Arms", "Back", "Left Wrist", "Right Wrist", "Range", "Hands",
    "Primary", "Secondary", "Fingers", "Chest", "Legs", "Feet", "Waist"
]

# Augmentation slots
AUGMENTATION_SLOTS = ['SLOT 1', 'SLOT 2', 'SLOT 3', 'SLOT 4', 'SLOT 5']

AUGMENTATION_TYPES = {
    '1': 'Type 1',
    '2': 'Type 2',
    '3': 'Type 3',
    '4': 'Type 4',
    '5': 'Type 5',
    '6': 'Type 6',
    '7': 'Type 7',
    '8': 'Type 8',
    '9': 'Type 9',
    '10': 'Type 10',
    '11': 'Type 11',
    '12': 'Type 12',
    '20': 'Type 20',
    '30': 'Type 30'
}

# Stat categories for item parsing and display
STAT_CATEGORIES = {
    # Core information
    'basic_info': ['Name', 'ID', 'URL', 'Type'] + AUGMENTATION_SLOTS,

    # Base stats
    'primary_stats': ['AC', 'HP', 'MANA', 'ENDURANCE'],
    'attributes': ['STR', 'STA', 'AGI', 'DEX', 'WIS', 'INT', 'CHA'],
    'resists': ['POISON', 'MAGIC', 'DISEASE', 'FIRE', 'COLD', 'CORRUPT'],
    
    # Weapon related
    'weapon_stats': ['DAMAGE', 'DELAY', 'BONUS', 'RANGE'],
    'weapon_types': [
        '1H BLUNT', '1H PIERCING', '1H SLASHING',
        '2H BLUNT', '2H PIERCING', '2H SLASHING',
        'HAND TO HAND', 'THROWING'
    ],
    'weapon_skills': [
        '1H BLUNT', '1H PIERCING', '1H SLASHING',
        '2H BLUNT', '2H PIERCING', '2H SLASHING',
        'HAND TO HAND', 'THROWING'
    ],
    
    # Combat related
    'offensive_stats': [
        'ACCURACY', 'ATTACK', 'BACKSTAB',
        'COMBAT EFFECTS', 'HASTE', 'SPELL DAMAGE', 
        'STRIKETHROUGH'
    ],
    'defensive_stats': [
        'AVOIDANCE', 'DAMAGE SHIELD MITIG', 'DEFENSE',
        'DODGE', 'DOT SHIELDING', 'PARRY', 'RIPOSTE',
        'SHIELDING', 'SPELL SHIELDING', 'STUN RESIST'
    ],
    
    # Recovery and Regen
    'regeneration': [
        'ENDURANCE REGEN', 'HP REGEN', 'MANA REGEN',
        'MEDITATE'
    ],
    
    # Combat abilities
    'combat_abilities': [
        'BASH DAMAGE', 'DAMAGE SHIELD', 'DOUBLE ATTACK',
        'DRAGON PUNCH', 'EAGLE STRIKE', 'FLYING KICK',
        'FRENZY', 'INTIMIDATION', 'KICK', 'KICK DAMAGE',
        'ROUND KICK', 'TIGER CLAW', 'TRIPLE ATTACK'
    ],
    
    # Magic skills
    'magic_skills': [
        'ABJURATION', 'ALTERATION', 'CHANNELING',
        'CONJURATION', 'DIVINATION', 'EVOCATION'
    ],
    'spell_specializations': [
        'SPECIALIZE ABJURATION', 'SPECIALIZE ALTERATION',
        'SPECIALIZE CONJURATION', 'SPECIALIZE DIVINATION',
        'SPECIALIZE EVOCATION'
    ],
    
    # Tradeskills
    'tradeskills': [
        'ALCHEMY', 'BAKING', 'BLACKSMITHING', 'BREWING',
        'FISHING', 'FLETCHING', 'JEWELRY MAKING', 'MAKE POISON',
        'POTTERY', 'RESEARCH', 'TAILORING', 'TINKERING'
    ],
    
    # Non-combat abilities
    'utility_skills': [
        'BEGGING', 'FORAGE', 'PICK LOCK', 'SAFE FALL',
        'SNEAK', 'TRACKING'
    ],
    
    # Bard specific
    'bard_skills': [
        'ALL INSTRUMENTS', 'BRASS INSTRUMENTS',
        'PERCUSSION INSTRUMENTS', 'STRINGS INSTRUMENTS',
        'UNKNOWN (50)', 'WIND INSTRUMENTS'
    ],
    
    # Effects
    'effects': ['FOCUS EFFECT', 'WORN EFFECT', 'CLICK EFFECT', 'PROC EFFECT']
}

# Display organization for grouping stats in UI and CSV output
DISPLAY_ORGANIZATION = {
    'basic_info': {
        'display_name': 'BASIC INFORMATION',
        'categories': ['basic_info']
    },
    'weapon_stats': {
        'display_name': 'WEAPON STATS',
        'categories': ['weapon_stats']
    },
    'primary_stats': {
        'display_name': 'PRIMARY STATS',
        'categories': ['primary_stats']
    },
    'attributes': {
        'display_name': 'ATTRIBUTES',
        'categories': ['attributes']
    },
    'resists': {
        'display_name': 'RESISTS',
        'categories': ['resists']
    },
    'secondary_stats': {
        'display_name': 'SECONDARY STATS',
        'categories': ['offensive_stats', 'defensive_stats', 'regeneration']
    },
    'skill_modifiers': {
        'display_name': 'SKILL MODIFIERS',
        'categories': [
            'weapon_skills',
            'combat_abilities',
            'magic_skills',
            'spell_specializations',
            'bard_skills',
            'utility_skills',
            'tradeskills'
        ]
    },
    'effects': {
        'display_name': 'EFFECTS',
        'categories': ['effects']
    }
}

# Stat name normalizations
STAT_REPLACEMENTS = {
    'ARMOR CLASS': 'AC',
    'HEALTH': 'HP',
    'STRENGTH': 'STR',
    'STAMINA': 'STA',
    'AGILITY': 'AGI',
    'DEXTERITY': 'DEX',
    'WISDOM': 'WIS',
    'INTELLIGENCE': 'INT',
    'CHARISMA': 'CHA',
    'ENDURANCE': 'END',
    'UNKNOWN (50)': 'SINGING RESONANCE'
}