-- Leader–unit attachment for 40K: when set, this entry (leader) is attached to that unit (bodyguard).
-- Run: mysql -u <user> -p <database> < add_play_armylist_leader_attachment.sql

-- Add column (run once; omit if column already exists)
ALTER TABLE play_armylist_entries
  ADD COLUMN attached_to_entry_id INT NULL DEFAULT NULL;

ALTER TABLE play_armylist_entries
  ADD CONSTRAINT play_armylist_entries_attached_fk
  FOREIGN KEY (attached_to_entry_id) REFERENCES play_armylist_entries (entry_id) ON DELETE SET NULL;
