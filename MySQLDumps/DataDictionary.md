📚 Data Dictionary: Wargaming ERP
Database: wargaming_erp | Engine: InnoDB | Charset: utf8mb4
🛡️ 1. List Management (Core App Logic)
These tables store the lists you create and the units you add to them.
Table	Column	Type	Description
play_armylists	list_id	INT (AI)	Primary Key. Unique ID for each army list.
list_name	VARCHAR(100)	The user-defined name of the roster.
game_system	ENUM	'OPR' or '40K_10E'. Controls UI logic.
point_limit	INT	The points ceiling for the roster.
faction_primary	VARCHAR(100)	Main army book/faction.
faction_secondary	VARCHAR(100)	Allied army book/faction (Optional).
waha_detachment_id	VARCHAR(50)	FK to waha_detachments. Sets 40K ruleset.
play_armylist_entries	entry_id	INT (AI)	Primary Key. Represents a unit "instance" in a list.
list_id	INT	FK to play_armylists.
unit_id	VARCHAR(50)	Links to waha_datasheet_id or opr_unit_id.
quantity	INT	Number of models/units in this entry.
🎲 2. OPR Data Structures
Populated via the OPR_JSON_analyzer.py deep-dive.
Table	Column	Type	Description
opr_units	opr_unit_id	VARCHAR(50)	PK. Unique ID from OPR JSON.
name	VARCHAR(100)	Unit name (e.g., "Hive Lord").
army	VARCHAR(100)	Army book name.
base_cost	INT	Points before upgrades.
quality	INT	Quality stat (e.g., 3 means 3+).
defense	INT	Defense stat (e.g., 2 means 2+).
wounds	INT	Health of the unit.
opr_unit_upgrades	id	INT (AI)	PK. Unique ID for the upgrade option.
unit_id	VARCHAR(50)	FK to opr_units.
section_label	VARCHAR(255)	Category (e.g., "Replace Shredder Cannon").
option_label	VARCHAR(255)	The choice (e.g., "Acid Cannon").
cost	INT	Point cost of this upgrade.
🦅 3. 40K 10th Edition Data
Standardized Wahapedia architecture.
Table	Column	Type	Description
waha_datasheets	waha_datasheet_id	VARCHAR(50)	PK. Unique Wahapedia ID.
name	VARCHAR(100)	Unit name.
faction_id	VARCHAR(50)	FK to waha_factions (e.g., 'ORK').
points_cost	INT	Current 10E points per model/unit.
movement	VARCHAR(10)	M stat (e.g., '6"').
toughness	INT	T stat.
waha_detachments	id	VARCHAR(50)	PK. Unique ID for the sub-faction rules.
faction_id	VARCHAR(50)	Links to the parent faction.
name	VARCHAR(100)	Detachment name (e.g., "War Horde").
🛠️ 4. Upgrade & Enhancement Junctions
Tracks what the user "bought" for their units.
Table	Column	Type	Description
play_armylist_upgrades	selection_id	INT (AI)	PK. Tracks OPR gear swaps.
entry_id	INT	FK to play_armylist_entries.
upgrade_id	INT	FK to opr_unit_upgrades.
play_armylist_enhancements	selection_id	INT (AI)	PK. Tracks 40K Character relics.
entry_id	INT	FK to play_armylist_entries.
enhancement_id	VARCHAR(50)	FK to waha_enhancements.

💡 Pro-Tip for your README:
You can keep your schema documented and up-to-date automatically by running this SQL query anytime you make changes:
sql
SELECT 
    TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = 'wargaming_erp'
ORDER BY 
    TABLE_NAME, ORDINAL_POSITION;
	
	inv_creators	creator_id	int	NO	
inv_creators	name	varchar	NO	
inv_creators	platform	varchar	YES	
inv_paint_inventory	paint_id	int	NO	
inv_paint_inventory	brand	varchar	YES	
inv_paint_inventory	paint_name	varchar	YES	
inv_paint_inventory	paint_type	enum	YES	
inv_paint_inventory	purchase_price	decimal	YES	4.50
inv_paint_inventory	estimated_uses	int	YES	50
inv_paint_inventory	current_bottles	int	YES	1
inv_paint_inventory	min_bottles	int	YES	1
inv_paint_inventory	is_in_stock	tinyint	YES	1
inv_paint_recipes	recipe_id	int	NO	
inv_paint_recipes	recipe_name	varchar	YES	
inv_paint_recipes	notes	text	YES	
inv_physical_models	model_id	int	NO	
inv_physical_models	stl_id	int	YES	
inv_physical_models	is_painted	tinyint	YES	0
inv_physical_models	is_magnetized	tinyint	YES	0
inv_physical_models	applied_recipe_id	int	YES	
inv_physical_models	material_cost_est	decimal	YES	2.50
inv_physical_models	current_status	enum	YES	Available
inv_proxy_bridge	proxy_id	int	NO	
inv_proxy_bridge	stl_id	int	YES	
inv_proxy_bridge	opr_unit_id	varchar	YES	
inv_proxy_bridge	waha_datasheet_id	varchar	YES	
inv_proxy_bridge	is_preferred	tinyint	YES	0
inv_recipe_steps	step_id	int	NO	
inv_recipe_steps	recipe_id	int	YES	
inv_recipe_steps	paint_id	int	YES	
inv_recipe_steps	step_order	int	YES	
inv_recipe_steps	application_method	varchar	YES	
inv_resin_inventory	resin_id	int	NO	
inv_resin_inventory	brand	varchar	YES	
inv_resin_inventory	type	varchar	YES	
inv_resin_inventory	purchase_price_usd	decimal	YES	
inv_resin_inventory	bottle_size_ml	int	YES	1000
inv_resin_inventory	current_stock_ml	decimal	YES	
inv_resin_inventory	min_inventory_ml	decimal	YES	500.00
inv_resin_inventory	is_active	tinyint	YES	1
inv_stl_bits	bit_id	int	NO	
inv_stl_bits	stl_id	int	YES	
inv_stl_bits	bit_name	varchar	YES	
inv_stl_bits	estimated_resin_ml	decimal	YES	1.00
inv_stl_library	stl_id	int	NO	
inv_stl_library	creator_id	int	YES	
inv_stl_library	product_name	varchar	YES	
inv_stl_library	render_url	varchar	YES	
inv_stl_library	source_url	varchar	YES	
inv_stl_library	model_height_mm	int	YES	32
inv_stl_library	resin_vol_ml	decimal	YES	5.00
opr_army_settings	army_name	varchar	NO	
opr_army_settings	setting_name	varchar	YES	
opr_specialrules	rule_id	varchar	NO	
opr_specialrules	name	varchar	YES	
opr_specialrules	description	text	YES	
opr_unit_upgrades	id	int	NO	
opr_unit_upgrades	unit_id	varchar	YES	
opr_unit_upgrades	section_label	varchar	YES	
opr_unit_upgrades	option_label	varchar	YES	
opr_unit_upgrades	cost	int	YES	
opr_unitrules	unit_id	varchar	NO	
opr_unitrules	rule_id	varchar	NO	
opr_unitrules	rating	int	YES	
opr_unitrules	label	varchar	YES	
opr_units	opr_unit_id	varchar	NO	
opr_units	name	varchar	YES	
opr_units	army	varchar	YES	
opr_units	base_cost	int	YES	
opr_units	round_base_mm	int	YES	
opr_units	is_hero	tinyint	YES	0
opr_units	is_aircraft	tinyint	YES	0
opr_units	quality	int	YES	
opr_units	defense	int	YES	
opr_units	wounds	int	YES	
opr_units	image_url	varchar	YES	
opr_unitweapons	unit_id	varchar	NO	
opr_unitweapons	weapon_label	varchar	NO	
opr_unitweapons	attacks	int	YES	
opr_unitweapons	ap	int	YES	
opr_unitweapons	special_rules	varchar	YES	
opr_unitweapons	count	int	YES	1
play_armylist_enhancements	selection_id	int	NO	
play_armylist_enhancements	entry_id	int	YES	
play_armylist_enhancements	enhancement_id	varchar	YES	
play_armylist_enhancements	cost	int	YES	
play_armylist_entries	entry_id	int	NO	
play_armylist_entries	list_id	int	YES	
play_armylist_entries	unit_id	varchar	YES	
play_armylist_entries	quantity	int	YES	1
play_armylist_upgrades	id	int	NO	
play_armylist_upgrades	entry_id	int	YES	
play_armylist_upgrades	upgrade_id	int	YES	
play_armylists	list_id	int	NO	
play_armylists	list_name	varchar	YES	
play_armylists	game_system	enum	YES	
play_armylists	point_limit	int	YES	2000
play_armylists	waha_detachment_id	varchar	YES	
play_armylists	primary_recipe_id	int	YES	
play_armylists	is_boarding_action	tinyint	YES	0
play_armylists	faction_primary	varchar	YES	
play_armylists	faction_secondary	varchar	YES	
play_listunits	instance_id	int	NO	
play_listunits	list_id	int	YES	
play_listunits	opr_unit_id	varchar	YES	
play_listunits	waha_datasheet_id	varchar	YES	
play_listunits	custom_name	varchar	YES	
play_listunits	is_combined	tinyint	YES	0
play_listunits	attached_to_id	int	YES	
play_listunits	current_wounds	int	YES	
play_listunits	is_destroyed	tinyint	YES	0
play_match_tracking	match_id	int	NO	
play_match_tracking	list_id	int	YES	
play_match_tracking	current_round	int	YES	1
play_match_tracking	current_cp	int	YES	0
play_match_tracking	primary_vp	int	YES	0
play_match_tracking	secondary_vp	int	YES	0
play_mission_cards	card_id	int	NO	
play_mission_cards	game_system	enum	YES	
play_mission_cards	card_title	varchar	YES	
play_mission_cards	rules_text	text	YES	
play_mission_cards	vp_reward	int	YES	
play_mission_cards	is_fixed_eligible	tinyint	YES	0
retail_comparison	comparison_id	int	NO	
retail_comparison	opr_unit_id	varchar	YES	
retail_comparison	waha_datasheet_id	varchar	YES	
retail_comparison	equivalent_retail_name	varchar	YES	
retail_comparison	retail_price_usd	decimal	YES	
system_alerts	alert_id	int	NO	
system_alerts	alert_date	timestamp	YES	CURRENT_TIMESTAMP
system_alerts	alert_type	varchar	YES	
system_alerts	message	text	YES	
system_alerts	severity	enum	YES	
view_40k_datasheet_complete	ID	varchar	YES	
view_40k_datasheet_complete	Unit_Name	varchar	YES	
view_40k_datasheet_complete	Faction	varchar	YES	
view_40k_datasheet_complete	Points	int	YES	
view_40k_datasheet_complete	M	varchar	YES	
view_40k_datasheet_complete	T	int	YES	
view_40k_datasheet_complete	Sv	varchar	YES	
view_40k_datasheet_complete	W	int	YES	
view_40k_datasheet_complete	Ld	varchar	YES	
view_40k_datasheet_complete	OC	int	YES	
view_40k_datasheet_complete	Base	varchar	YES	
view_40k_datasheet_complete	Image	varchar	YES	
view_40k_datasheet_complete	Keywords	text	YES	
view_40k_enhancement_picker	enhancement_id	varchar	NO	
view_40k_enhancement_picker	enhancement_name	varchar	YES	
view_40k_enhancement_picker	cost	int	YES	
view_40k_enhancement_picker	description	text	YES	
view_40k_enhancement_picker	detachment_name	varchar	YES	
view_40k_enhancement_picker	detachment_id	varchar	NO	
view_40k_enhancement_picker	faction_id	varchar	YES	
view_active_list_options	list_name	varchar	YES	
view_active_list_options	unit_name	varchar	YES	
view_active_list_options	swap_option	text	YES	
view_list_validation	list_name	varchar	YES	
view_list_validation	Unit_Name	varchar	YES	
view_list_validation	quantity	int	YES	1
view_list_validation	Status	varchar	NO	
view_master_army_command	Project	varchar	YES	
view_master_army_command	System	enum	YES	
view_master_army_command	Unit Count	bigint	NO	0
view_master_army_command	Points Total	decimal	YES	
view_master_army_command	Physical Ready	bigint	YES	
view_master_picker	system	varchar	NO	
view_master_picker	setting	varchar	YES	
view_master_picker	faction	varchar	YES	
view_master_picker	id	varchar	NO	
view_master_picker	name	varchar	YES	
view_master_picker	points	int	YES	
view_opr_unit_complete	ID	varchar	YES	
view_opr_unit_complete	Unit_Name	varchar	YES	
view_opr_unit_complete	Army_Book	varchar	YES	
view_opr_unit_complete	Points	int	YES	
view_opr_unit_complete	Base_Size	int	YES	
view_opr_unit_complete	Special_Rules	text	YES	
view_unit_selector	unit_id	varchar	NO	
view_unit_selector	unit_name	varchar	YES	
view_unit_selector	faction_name	varchar	YES	
view_unit_selector	faction_id	varchar	YES	
view_unit_selector	points_cost	int	YES	
view_unit_selector	image_url	varchar	YES	
waha_abilities	id	text	YES	
waha_abilities	name	text	YES	
waha_abilities	legend	text	YES	
waha_abilities	faction_id	text	YES	
waha_abilities	description	text	YES	
waha_datasheet_unit_composition	datasheet_id	varchar	YES	
waha_datasheet_unit_composition	line_id	int	YES	
waha_datasheet_unit_composition	description	text	YES	
waha_datasheets	waha_datasheet_id	varchar	NO	
waha_datasheets	name	varchar	YES	
waha_datasheets	faction_id	varchar	YES	
waha_datasheets	base_size_text	varchar	YES	
waha_datasheets	points_cost	int	YES	
waha_datasheets	is_character	tinyint	YES	0
waha_datasheets	is_aircraft	tinyint	YES	0
waha_datasheets	movement	varchar	YES	
waha_datasheets	toughness	int	YES	
waha_datasheets	save_value	varchar	YES	
waha_datasheets	wounds	int	YES	
waha_datasheets	leadership	int	YES	
waha_datasheets	oc	int	YES	
waha_datasheets	image_url	varchar	YES	
waha_datasheets_abilities	datasheet_id	varchar	YES	
waha_datasheets_abilities	line_id	int	YES	
waha_datasheets_abilities	ability_id	varchar	YES	
waha_datasheets_abilities	model_name	varchar	YES	
waha_datasheets_abilities	name	varchar	YES	
waha_datasheets_abilities	description	text	YES	
waha_datasheets_abilities	type	varchar	YES	
waha_datasheets_detachment_abilities	datasheet_id	varchar	YES	
waha_datasheets_detachment_abilities	detachment_ability_id	varchar	YES	
waha_datasheets_keywords	datasheet_id	varchar	YES	
waha_datasheets_keywords	keyword	varchar	YES	
waha_datasheets_keywords	model	varchar	YES	
waha_datasheets_keywords	is_faction_keyword	tinyint	YES	
waha_datasheets_leader	leader_id	varchar	YES	
waha_datasheets_leader	attached_id	varchar	YES	
waha_datasheets_models	datasheet_id	varchar	YES	
waha_datasheets_models	line_id	int	YES	
waha_datasheets_models	name	varchar	YES	
waha_datasheets_models	movement	varchar	YES	
waha_datasheets_models	toughness	int	YES	
waha_datasheets_models	save_value	varchar	YES	
waha_datasheets_models	inv_sv	varchar	YES	
waha_datasheets_models	inv_sv_descr	text	YES	
waha_datasheets_models	wounds	int	YES	
waha_datasheets_models	leadership	varchar	YES	
waha_datasheets_models	oc	int	YES	
waha_datasheets_models	base_size	varchar	YES	
waha_datasheets_models	base_size_descr	text	YES	
waha_datasheets_options	datasheet_id	varchar	YES	
waha_datasheets_options	line_id	int	YES	
waha_datasheets_options	button_text	varchar	YES	
waha_datasheets_options	description	text	YES	
waha_datasheets_stratagems	datasheet_id	varchar	YES	
waha_datasheets_stratagems	stratagem_id	varchar	YES	
waha_datasheets_wargear	datasheet_id	varchar	YES	
waha_datasheets_wargear	line_id	int	YES	
waha_datasheets_wargear	line_in_wargear	int	YES	
waha_datasheets_wargear	dice	varchar	YES	
waha_datasheets_wargear	name	varchar	YES	
waha_datasheets_wargear	description	text	YES	
waha_datasheets_wargear	range_val	varchar	YES	
waha_datasheets_wargear	type	varchar	YES	
waha_datasheets_wargear	attacks	varchar	YES	
waha_datasheets_wargear	bs_ws	varchar	YES	
waha_datasheets_wargear	strength	varchar	YES	
waha_datasheets_wargear	ap	varchar	YES	
waha_datasheets_wargear	damage	varchar	YES	
waha_detachment_abilities	id	varchar	NO	
waha_detachment_abilities	faction_id	varchar	YES	
waha_detachment_abilities	name	varchar	YES	
waha_detachment_abilities	legend	text	YES	
waha_detachment_abilities	description	text	YES	
waha_detachment_abilities	detachment_name	varchar	YES	
waha_detachment_abilities	detachment_id	varchar	YES	
waha_detachments	id	varchar	NO	
waha_detachments	faction_id	varchar	YES	
waha_detachments	name	varchar	YES	
waha_detachments	legend	text	YES	
waha_detachments	type	varchar	YES	
waha_detachments	rules_summary	text	YES	
waha_enhancements	faction_id	varchar	YES	
waha_enhancements	id	varchar	NO	
waha_enhancements	name	varchar	YES	
waha_enhancements	cost	int	YES	
waha_enhancements	detachment	varchar	YES	
waha_enhancements	detachment_id	varchar	YES	
waha_enhancements	legend	text	YES	
waha_enhancements	description	text	YES	
waha_factions	id	varchar	NO	
waha_factions	name	varchar	YES	
waha_factions	link	varchar	YES	
waha_factions	parent_id	varchar	YES	
waha_keywords	id	varchar	NO	
waha_keywords	name	varchar	YES	
waha_stratagems	faction_id	varchar	YES	
waha_stratagems	name	varchar	YES	
waha_stratagems	id	varchar	NO	
waha_stratagems	type	varchar	YES	
waha_stratagems	cp_cost	int	YES	
waha_stratagems	legend	text	YES	
waha_stratagems	turn	varchar	YES	
waha_stratagems	phase	varchar	YES	
waha_stratagems	detachment	varchar	YES	
waha_stratagems	detachment_id	varchar	YES	
waha_stratagems	description	text	YES	
waha_weapons	weapon_id	varchar	NO	
waha_weapons	name	varchar	YES	
waha_weapons	range_val	varchar	YES	
waha_weapons	attacks_val	varchar	YES	
waha_weapons	strength_val	int	YES	
waha_weapons	ap_val	int	YES	
waha_weapons	damage_val	varchar	YES	