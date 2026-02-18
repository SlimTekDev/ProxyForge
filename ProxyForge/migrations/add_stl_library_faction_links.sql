-- Associate MMF records with army roster level: 40K faction or OPR army.
-- faction_key: for 40K = waha_factions.id (e.g. Orks, AE); for OPR = opr_units.army (e.g. Alien Hives).
-- Enables filtering "STLs for this faction" and tag-matched proxy suggestions (Feature #5).

CREATE TABLE IF NOT EXISTS stl_library_faction_links (
  id INT NOT NULL AUTO_INCREMENT,
  mmf_id VARCHAR(50) NOT NULL,
  game_system VARCHAR(50) NOT NULL,
  faction_key VARCHAR(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY unique_stl_faction (mmf_id, game_system, faction_key),
  CONSTRAINT stl_library_faction_links_fk
    FOREIGN KEY (mmf_id) REFERENCES stl_library (mmf_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
