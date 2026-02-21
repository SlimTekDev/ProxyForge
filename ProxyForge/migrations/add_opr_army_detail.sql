-- Army-specific lore, rules and spells for the Army Book view.
-- Run once: execute this file in MySQL Workbench or:
--   mysql -u <user> -p <database> < ProxyForge/migrations/add_opr_army_detail.sql

CREATE TABLE IF NOT EXISTS opr_army_detail (
  army_name VARCHAR(150) NOT NULL,
  game_system VARCHAR(80) NOT NULL,
  background TEXT NULL COMMENT 'Army lore / background text',
  army_wide_rules TEXT NULL COMMENT 'Army-wide special rules (name + description)',
  special_rules TEXT NULL COMMENT 'Special rules (name + description)',
  aura_rules TEXT NULL COMMENT 'Aura special rules (name + description)',
  spells TEXT NULL COMMENT 'Spells (name, threshold, effect)',
  updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (army_name, game_system)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
