-- Roster-level STL choices: which STL(s) to use for each roster entry (supports kitbashing from multiple sources).
-- entry_id = play_armylist_entries.entry_id; sort_order for display order.

CREATE TABLE IF NOT EXISTS play_armylist_stl_choices (
  id INT NOT NULL AUTO_INCREMENT,
  entry_id INT NOT NULL,
  mmf_id VARCHAR(50) NOT NULL,
  sort_order INT DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY unique_entry_mmf (entry_id, mmf_id),
  CONSTRAINT play_armylist_stl_choices_entry_fk
    FOREIGN KEY (entry_id) REFERENCES play_armylist_entries (entry_id) ON DELETE CASCADE,
  CONSTRAINT play_armylist_stl_choices_mmf_fk
    FOREIGN KEY (mmf_id) REFERENCES stl_library (mmf_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
