extends Node2D

const CustomerActor = preload("res://scripts/customer_actor.gd")
const SAVE_PATH := "user://robledo_bistro_save.json"
const WORLD_SIZE := Vector2(2700, 1700)
const SHIFT_SECONDS := 135.0
const MAX_LIVES := 3

var recipes := {}
var questions := []
var game := {}
var player: CharacterBody2D
var camera: Camera2D
var hud_layer: CanvasLayer
var ui := {}
var tables := []
var stations := {}
var groups := []
var orders := []
var ready_dishes := []
var employee_nodes := {}
var pressed := {}
var next_group_id := 1
var next_order_id := 1
var spawn_timer := 2.5
var staff_timers := {"cook": 6.0, "waiter": 3.0, "cleaner": 4.0}
var action: Variant = null
var current_quiz: Variant = null
var pending_life_reason := ""
var world_root: Node2D
var decor_root: Node2D
var actors_root: Node2D
var style_palette := {
	"classic": {"floor": Color("#d9c8a9"), "hall": Color("#e9dcc3"), "accent": Color("#8a5b3d")},
	"garden": {"floor": Color("#d3dec6"), "hall": Color("#e8f0df"), "accent": Color("#4f7c58")},
	"neon": {"floor": Color("#25283a"), "hall": Color("#31344c"), "accent": Color("#a44cff")}
}

func _ready() -> void:
	randomize()
	_load_data()
	_reset_game_state()
	_build_world()
	_build_player()
	_build_hud()
	_build_overlays()
	_refresh_all_ui()
	_show_start_overlay()

func _load_data() -> void:
	var recipe_text := FileAccess.get_file_as_string("res://data/recipes.json")
	var parsed_recipes = JSON.parse_string(recipe_text)
	if typeof(parsed_recipes) == TYPE_DICTIONARY:
		recipes = parsed_recipes
	var question_text := FileAccess.get_file_as_string("res://data/questions.json")
	var parsed_questions = JSON.parse_string(question_text)
	if typeof(parsed_questions) == TYPE_ARRAY:
		questions = parsed_questions

func _reset_game_state() -> void:
	game = {
		"day": 1,
		"max_days": 7,
		"cash": 220.0,
		"rep": 72.0,
		"lives": 3,
		"time_left": SHIFT_SECONDS,
		"running": false,
		"paused": true,
		"served_today": 0,
		"earned_today": 0.0,
		"walkouts_today": 0,
		"walkout_meter": 0,
		"target": 6,
		"inventory": {"greens":22,"bread":20,"beef":14,"cheese":16,"tomato":24,"pasta":18,"chicken":14,"flour":20,"egg":18,"milk":16,"sauce":20,"broth":16},
		"menu": {"salad":true,"burger":true,"pasta":true,"soup":true,"toast":false,"pizza":false,"chicken":false,"waffle":false},
		"prices": {"salad":14,"burger":22,"pasta":20,"soup":17,"toast":16,"pizza":26,"chicken":25,"waffle":18},
		"unlocked_recipes": ["salad","burger","pasta","soup"],
		"staff": {"host":0,"cook":0,"waiter":0,"cleaner":0},
		"upgrades": {"prep":1,"stove":1,"oven":1},
		"expansions": {"hall_b":false,"terrace":false,"kitchen_wing":false},
		"styles_owned": ["classic"],
		"style": "classic",
		"stats": {"total_tables":0,"total_revenue":0.0,"quiz_right":0,"quiz_total":0,"walkouts":0},
		"best": 0
	}

func _build_world() -> void:
	world_root = Node2D.new()
	world_root.name = "World"
	add_child(world_root)
	decor_root = Node2D.new()
	decor_root.name = "Decor"
	world_root.add_child(decor_root)
	actors_root = Node2D.new()
	actors_root.name = "Actors"
	world_root.add_child(actors_root)
	_build_floor_and_zones()
	_build_stations()
	_build_tables()
	_build_environment_props()

func _build_floor_and_zones() -> void:
	var p = style_palette[game["style"]]
	_add_rect("WholeFloor", Rect2(20,20,WORLD_SIZE.x-40,WORLD_SIZE.y-40), Color("#b8b2a8"), -100)
	_add_zone("KITCHEN", Rect2(80,90,840,600), Color("#ccd5db"))
	_add_zone("LOBBY", Rect2(980,90,520,320), Color("#ece5d8"))
	_add_zone("MAIN DINING HALL", Rect2(980,450,1050,690), p["hall"])
	_add_zone("HALL B", Rect2(2070,450,550,690), Color("#d4d7df"), true, "hall_b")
	_add_zone("GARDEN TERRACE", Rect2(980,1190,1640,400), Color("#cfe4ca"), true, "terrace")
	_add_zone("KITCHEN WING", Rect2(80,740,840,470), Color("#c7d2d8"), true, "kitchen_wing")
	_add_zone("STORAGE", Rect2(80,1260,840,330), Color("#d9c9af"))
	_add_wall(Rect2(50,50,WORLD_SIZE.x-100,18))
	_add_wall(Rect2(50,WORLD_SIZE.y-68,WORLD_SIZE.x-100,18))
	_add_wall(Rect2(50,50,18,WORLD_SIZE.y-100))
	_add_wall(Rect2(WORLD_SIZE.x-68,50,18,WORLD_SIZE.y-100))

func _add_zone(title: String, rect: Rect2, color: Color, locked := false, expansion := "") -> void:
	var node := Node2D.new()
	node.name = title.replace(" ", "_")
	node.set_meta("expansion", expansion)
	node.set_meta("locked_zone", locked)
	world_root.add_child(node)
	var poly := Polygon2D.new()
	poly.polygon = PackedVector2Array([Vector2.ZERO,Vector2(rect.size.x,0),rect.size,Vector2(0,rect.size.y)])
	poly.color = color
	poly.position = rect.position
	poly.z_index = -90
	node.add_child(poly)
	var border := Line2D.new()
	border.width = 6
	border.default_color = Color(0.2,0.22,0.28,0.35)
	border.points = PackedVector2Array([rect.position,Vector2(rect.end.x,rect.position.y),rect.end,Vector2(rect.position.x,rect.end.y),rect.position])
	border.z_index = -80
	node.add_child(border)
	var label := Label.new()
	label.text = title
	label.position = rect.position + Vector2(18,12)
	label.add_theme_font_size_override("font_size", 24)
	label.add_theme_color_override("font_color", Color(0.12,0.15,0.2,0.55))
	node.add_child(label)
	if locked:
		var lock := Label.new()
		lock.name = "LockLabel"
		lock.text = "🔒 LOCKED · BUY BETWEEN DAYS"
		lock.position = rect.position + rect.size * 0.5 - Vector2(180,18)
		lock.add_theme_font_size_override("font_size", 26)
		lock.add_theme_color_override("font_color", Color("#723a3a"))
		node.add_child(lock)

func _add_rect(name: String, rect: Rect2, color: Color, z := 0) -> Polygon2D:
	var poly := Polygon2D.new()
	poly.name = name
	poly.polygon = PackedVector2Array([Vector2.ZERO,Vector2(rect.size.x,0),rect.size,Vector2(0,rect.size.y)])
	poly.position = rect.position
	poly.color = color
	poly.z_index = z
	world_root.add_child(poly)
	return poly

func _add_wall(rect: Rect2) -> void:
	var wall = _add_rect("Wall", rect, Color("#59616d"), -70)
	var body := StaticBody2D.new()
	body.position = rect.position + rect.size/2
	var shape := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = rect.size
	shape.shape = rs
	body.add_child(shape)
	world_root.add_child(body)

func _build_stations() -> void:
	var defs := [
		["fridge","FRIDGE",Vector2(160,170),Vector2(120,150),"res://assets/props/fridge.svg"],
		["prep","PREP",Vector2(350,170),Vector2(190,90),"res://assets/props/prep.svg"],
		["stove","STOVE",Vector2(610,170),Vector2(150,100),"res://assets/props/stove.svg"],
		["pass","SERVICE PASS",Vector2(830,420),Vector2(90,220),"res://assets/props/pass.svg"],
		["stock","STORAGE",Vector2(240,1400),Vector2(170,120),"res://assets/props/crate.svg"],
		["oven","OVEN",Vector2(410,860),Vector2(130,130),"res://assets/props/oven.svg"]
	]
	for d in defs:
		var station := Node2D.new()
		station.name = d[0]
		station.position = d[2]
		station.set_meta("id", d[0])
		station.set_meta("label", d[1])
		station.set_meta("size", d[3])
		world_root.add_child(station)
		var sprite := Sprite2D.new()
		sprite.texture = load(d[4])
		sprite.scale = Vector2(0.95,0.95)
		station.add_child(sprite)
		var label := Label.new()
		label.text = d[1]
		label.position = Vector2(-70,65)
		label.size = Vector2(140,25)
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.add_theme_font_size_override("font_size", 14)
		label.add_theme_color_override("font_color", Color("#182033"))
		station.add_child(label)
		stations[d[0]] = station
		if d[0] != "pass":
			_add_station_collision(d[2], d[3])
	stations["oven"].visible = game["expansions"]["kitchen_wing"]

func _add_station_collision(pos: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = pos
	var collision := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	collision.shape = rs
	body.add_child(collision)
	world_root.add_child(body)

func _build_tables() -> void:
	var defs := [
		[1,Vector2(1110,560),4,"main"],[2,Vector2(1360,560),4,"main"],[3,Vector2(1610,560),4,"main"],[4,Vector2(1860,560),4,"main"],
		[5,Vector2(1110,810),4,"main"],[6,Vector2(1360,810),4,"main"],[7,Vector2(1610,810),4,"main"],[8,Vector2(1860,810),4,"main"],
		[9,Vector2(1110,1030),2,"main"],[10,Vector2(1430,1030),2,"main"],[11,Vector2(1750,1030),2,"main"],
		[12,Vector2(2190,580),4,"hall_b"],[13,Vector2(2440,580),4,"hall_b"],[14,Vector2(2190,870),4,"hall_b"],[15,Vector2(2440,870),4,"hall_b"],
		[16,Vector2(1130,1320),4,"terrace"],[17,Vector2(1430,1320),4,"terrace"],[18,Vector2(1730,1320),4,"terrace"],[19,Vector2(2030,1320),4,"terrace"],[20,Vector2(2330,1320),4,"terrace"]
	]
	for d in defs:
		var table_node := Node2D.new()
		table_node.position = d[1]
		table_node.name = "Table_%d" % d[0]
		world_root.add_child(table_node)
		var sprite := Sprite2D.new()
		sprite.texture = load("res://assets/props/table.svg")
		sprite.scale = Vector2(0.86,0.86)
		table_node.add_child(sprite)
		var tag := Label.new()
		tag.text = "T%d" % d[0]
		tag.position = Vector2(-20,-15)
		tag.size = Vector2(40,24)
		tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		tag.add_theme_font_size_override("font_size", 16)
		tag.add_theme_color_override("font_color", Color.WHITE)
		table_node.add_child(tag)
		var seats := _seat_positions(d[1], d[2])
		tables.append({"id":d[0],"node":table_node,"pos":d[1],"capacity":d[2],"zone":d[3],"occupied":false,"dirty":false,"group_id":-1,"seats":seats})

func _seat_positions(center: Vector2, capacity: int) -> Array:
	var all := [center+Vector2(-72,0),center+Vector2(72,0),center+Vector2(0,-72),center+Vector2(0,72)]
	if capacity == 2:
		return [all[0],all[1]]
	return all

func _build_environment_props() -> void:
	for pos in [Vector2(1030,500),Vector2(1990,500),Vector2(1060,1110),Vector2(1960,1110)]:
		_spawn_prop("res://assets/props/plant.svg", pos, 0.8)
	for pos in [Vector2(1090,1220),Vector2(1520,1220),Vector2(1950,1220),Vector2(2380,1220)]:
		var plant := _spawn_prop("res://assets/props/plant.svg", pos, 0.72)
		plant.set_meta("expansion", "terrace")
	var sign := _spawn_prop("res://assets/ui/restaurant_sign.svg", Vector2(1210,165), 0.95)
	sign.z_index = 200

func _spawn_prop(path: String, pos: Vector2, scale_value: float) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.position = pos
	sprite.scale = Vector2(scale_value,scale_value)
	sprite.z_index = int(pos.y)
	decor_root.add_child(sprite)
	return sprite

func _build_player() -> void:
	player = CharacterBody2D.new()
	player.name = "ChefPlayer"
	player.position = Vector2(650,520)
	actors_root.add_child(player)
	var sprite := Sprite2D.new()
	sprite.texture = load("res://assets/characters/chef_player.svg")
	sprite.scale = Vector2(0.82,0.82)
	player.add_child(sprite)
	var collision := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 23
	collision.shape = circle
	player.add_child(collision)
	camera = Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.5
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = int(WORLD_SIZE.x)
	camera.limit_bottom = int(WORLD_SIZE.y)
	camera.zoom = Vector2(0.76,0.76)
	player.add_child(camera)

func _build_hud() -> void:
	hud_layer = CanvasLayer.new()
	hud_layer.layer = 20
	add_child(hud_layer)
	var top := PanelContainer.new()
	top.position = Vector2(16,14)
	top.size = Vector2(1248,76)
	_style_panel(top, Color(0.05,0.07,0.12,0.92))
	hud_layer.add_child(top)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	top.add_child(row)
	var logo := TextureRect.new()
	logo.texture = load("res://assets/ui/school_logo.webp")
	logo.custom_minimum_size = Vector2(58,58)
	logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	row.add_child(logo)
	var title := Label.new()
	title.text = "ROBLEDO BISTRO SENIOR"
	title.custom_minimum_size = Vector2(270,58)
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 22)
	title.add_theme_color_override("font_color", Color("#f5f7ff"))
	row.add_child(title)
	for item in [["day","DAY"],["time","TIME"],["cash","CASH"],["rep","REP"],["lives","LIVES"],["served","TABLES"]]:
		var box := VBoxContainer.new()
		box.custom_minimum_size = Vector2(110,58)
		var cap := Label.new()
		cap.text=item[1]
		cap.add_theme_font_size_override("font_size",12)
		cap.add_theme_color_override("font_color",Color("#9da9bd"))
		box.add_child(cap)
		var val := Label.new()
		val.text="--"
		val.add_theme_font_size_override("font_size",20)
		val.add_theme_color_override("font_color",Color.WHITE)
		box.add_child(val)
		ui[item[0]] = val
		row.add_child(box)
	var left := PanelContainer.new()
	left.position = Vector2(16,104)
	left.size = Vector2(330,390)
	_style_panel(left, Color(0.04,0.06,0.1,0.86))
	hud_layer.add_child(left)
	var lv := VBoxContainer.new()
	lv.add_theme_constant_override("separation",8)
	left.add_child(lv)
	var head := _label("ACTIVE ORDERS",20,Color("#ffdd82"))
	lv.add_child(head)
	ui["orders_box"] = VBoxContainer.new()
	ui["orders_box"].add_theme_constant_override("separation",6)
	lv.add_child(ui["orders_box"])
	var right := PanelContainer.new()
	right.position = Vector2(970,104)
	right.size = Vector2(294,300)
	_style_panel(right, Color(0.04,0.06,0.1,0.86))
	hud_layer.add_child(right)
	var rv := VBoxContainer.new()
	rv.add_theme_constant_override("separation",7)
	right.add_child(rv)
	rv.add_child(_label("SERVICE STATUS",18,Color("#8fe1c1")))
	ui["carried"] = _label("Tray: empty",16,Color.WHITE)
	ui["carried"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	rv.add_child(ui["carried"])
	ui["hint"] = _label("WASD move · E interact · M menu · TAB map",14,Color("#b8c0d0"))
	ui["hint"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	rv.add_child(ui["hint"])
	ui["status"] = _label("Restaurant closed.",16,Color("#f7cf75"))
	ui["status"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	rv.add_child(ui["status"])
	ui["inventory"] = _label("",13,Color("#cfd6e5"))
	ui["inventory"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	rv.add_child(ui["inventory"])
	var bottom := PanelContainer.new()
	bottom.position = Vector2(390,640)
	bottom.size = Vector2(500,62)
	_style_panel(bottom, Color(0.04,0.06,0.1,0.86))
	hud_layer.add_child(bottom)
	ui["prompt"] = _label("",18,Color.WHITE)
	ui["prompt"].horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	ui["prompt"].vertical_alignment=VERTICAL_ALIGNMENT_CENTER
	bottom.add_child(ui["prompt"])
	var menu_btn := Button.new()
	menu_btn.text="MENU [M]"
	menu_btn.position=Vector2(910,650)
	menu_btn.size=Vector2(150,42)
	menu_btn.pressed.connect(_toggle_menu_overlay)
	hud_layer.add_child(menu_btn)
	var map_btn := Button.new()
	map_btn.text="MAP [TAB]"
	map_btn.position=Vector2(1080,650)
	map_btn.size=Vector2(150,42)
	map_btn.pressed.connect(_toggle_map_overlay)
	hud_layer.add_child(map_btn)

func _build_overlays() -> void:
	ui["start_overlay"] = _make_overlay("start")
	var start_panel := _make_center_panel(ui["start_overlay"], Vector2(860,560))
	var sv := VBoxContainer.new()
	sv.add_theme_constant_override("separation",12)
	start_panel.add_child(sv)
	var brand := HBoxContainer.new()
	brand.add_theme_constant_override("separation",18)
	sv.add_child(brand)
	var logo := TextureRect.new()
	logo.texture=load("res://assets/ui/school_logo.webp")
	logo.custom_minimum_size=Vector2(100,100)
	logo.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	logo.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	brand.add_child(logo)
	var bt := VBoxContainer.new()
	bt.add_child(_label("ROBLEDO BISTRO SENIOR",34,Color.WHITE))
	bt.add_child(_label("FULL LOCAL GODOT EDITION",17,Color("#7ce1c3")))
	brand.add_child(bt)
	sv.add_child(_label("Manage a large restaurant where parties enter, sit, browse your menu, order, eat, pay and leave. Operate the kitchen yourself or build a trained staff.",18,Color("#d7deea")))
	var features := GridContainer.new()
	features.columns=2
	features.add_theme_constant_override("h_separation",12)
	features.add_theme_constant_override("v_separation",8)
	sv.add_child(features)
	for text in ["🪑 Seated customer groups & table lifecycle","📖 Configurable menu, prices and 8 recipes","👨‍🍳 Host · cook · waiter · cleaner","🏗️ Hall B · terrace · kitchen expansion","📦 Ingredient inventory & restocking","📐 Geometry Rescue only after life loss"]:
		var l := _label(text,16,Color("#eef2f8"))
		l.custom_minimum_size=Vector2(390,48)
		l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
		features.add_child(l)
	var btns := HBoxContainer.new()
	btns.alignment=BoxContainer.ALIGNMENT_CENTER
	btns.add_theme_constant_override("separation",16)
	sv.add_child(btns)
	var new_btn := Button.new()
	new_btn.text="NEW CAMPAIGN"
	new_btn.custom_minimum_size=Vector2(220,48)
	new_btn.pressed.connect(_new_campaign)
	btns.add_child(new_btn)
	ui["continue_btn"] = Button.new()
	ui["continue_btn"].text="CONTINUE"
	ui["continue_btn"].custom_minimum_size=Vector2(220,48)
	ui["continue_btn"].pressed.connect(_continue_campaign)
	btns.add_child(ui["continue_btn"])

	ui["menu_overlay"] = _make_overlay("menu")
	ui["menu_overlay"].visible=false
	var mp := _make_center_panel(ui["menu_overlay"], Vector2(920,570))
	var mv:=VBoxContainer.new()
	mv.add_theme_constant_override("separation",8)
	mp.add_child(mv)
	var mh := HBoxContainer.new()
	mh.add_child(_label("CURRENT MENU",30,Color.WHITE))
	var closem:=Button.new()
	closem.text="CLOSE"
	closem.pressed.connect(_toggle_menu_overlay)
	mh.add_child(closem)
	mv.add_child(mh)
	ui["menu_grid"] = GridContainer.new()
	ui["menu_grid"].columns=2
	ui["menu_grid"].add_theme_constant_override("h_separation",14)
	ui["menu_grid"].add_theme_constant_override("v_separation",10)
	mv.add_child(ui["menu_grid"])

	ui["map_overlay"] = _make_overlay("map")
	ui["map_overlay"].visible=false
	var map_p:=_make_center_panel(ui["map_overlay"],Vector2(760,520))
	var map_v:=VBoxContainer.new()
	map_p.add_child(map_v)
	map_v.add_child(_label("RESTAURANT MAP",30,Color.WHITE))
	ui["map_text"]=_label("",18,Color("#dbe3f1"))
	ui["map_text"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	map_v.add_child(ui["map_text"])
	var cmap:=Button.new()
	cmap.text="CLOSE"
	cmap.pressed.connect(_toggle_map_overlay)
	map_v.add_child(cmap)

	ui["management_overlay"] = _make_overlay("management")
	ui["management_overlay"].visible=false
	var mg := _make_center_panel(ui["management_overlay"],Vector2(1110,650))
	var rootv:=VBoxContainer.new()
	rootv.add_theme_constant_override("separation",8)
	mg.add_child(rootv)
	var mhead:=HBoxContainer.new()
	mhead.add_child(_label("RESTAURANT MANAGEMENT",28,Color.WHITE))
	ui["mg_cash"]=_label("Cash $0",22,Color("#8fe1c1"))
	mhead.add_child(ui["mg_cash"])
	rootv.add_child(mhead)
	ui["mg_tabs"] = TabContainer.new()
	ui["mg_tabs"].custom_minimum_size=Vector2(1060,520)
	rootv.add_child(ui["mg_tabs"])
	_build_management_tabs()
	var next_btn:=Button.new()
	next_btn.text="START NEXT DAY"
	next_btn.custom_minimum_size=Vector2(220,44)
	next_btn.pressed.connect(_start_next_day)
	rootv.add_child(next_btn)

	ui["quiz_overlay"] = _make_overlay("quiz")
	ui["quiz_overlay"].visible=false
	var qp:=_make_center_panel(ui["quiz_overlay"],Vector2(760,500))
	var qv:=VBoxContainer.new()
	qv.add_theme_constant_override("separation",10)
	qp.add_child(qv)
	qv.add_child(_label("GEOMETRY RESCUE",30,Color("#ffcf72")))
	ui["quiz_reason"]=_label("",16,Color("#ffc0c0"))
	qv.add_child(ui["quiz_reason"])
	ui["quiz_q"]=_label("",20,Color.WHITE)
	ui["quiz_q"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	qv.add_child(ui["quiz_q"])
	ui["quiz_answers"]=VBoxContainer.new()
	ui["quiz_answers"].add_theme_constant_override("separation",8)
	qv.add_child(ui["quiz_answers"])
	ui["quiz_feedback"]=_label("",16,Color("#b9c5d8"))
	qv.add_child(ui["quiz_feedback"])

	ui["end_overlay"] = _make_overlay("end")
	ui["end_overlay"].visible=false
	var ep:=_make_center_panel(ui["end_overlay"],Vector2(720,430))
	var ev:=VBoxContainer.new()
	ev.add_theme_constant_override("separation",12)
	ep.add_child(ev)
	ev.add_child(_label("CAMPAIGN COMPLETE",32,Color("#ffdc83")))
	ui["end_text"]=_label("",19,Color.WHITE)
	ui["end_text"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	ev.add_child(ui["end_text"])
	var again:=Button.new()
	again.text="NEW CAMPAIGN"
	again.pressed.connect(_new_campaign)
	ev.add_child(again)

func _build_management_tabs() -> void:
	var tabs: TabContainer = ui["mg_tabs"]
	var overview:=VBoxContainer.new()
	overview.name="Overview"
	overview.add_theme_constant_override("separation",8)
	tabs.add_child(overview)
	ui["day_report"]=_label("",17,Color("#e5e9f1"))
	ui["day_report"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	overview.add_child(ui["day_report"])
	var ops:=GridContainer.new()
	ops.columns=3
	overview.add_child(ops)
	for id in ["prep","stove","oven"]:
		var b:=Button.new()
		b.name=id
		b.custom_minimum_size=Vector2(250,86)
		b.pressed.connect(func(): _buy_kitchen_upgrade(id))
		ui["upgrade_"+id]=b
		ops.add_child(b)
	var restock:=Button.new()
	restock.text="RESTOCK ALL · $65"
	restock.pressed.connect(_restock_all)
	overview.add_child(restock)
	ui["mg_inventory"]=_label("",15,Color("#cbd4e4"))
	ui["mg_inventory"].autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	overview.add_child(ui["mg_inventory"])

	var menu:=ScrollContainer.new()
	menu.name="Menu & Recipes"
	tabs.add_child(menu)
	ui["mg_menu_box"]=VBoxContainer.new()
	ui["mg_menu_box"].add_theme_constant_override("separation",8)
	menu.add_child(ui["mg_menu_box"])
	var team:=VBoxContainer.new()
	team.name="Staff"
	team.add_theme_constant_override("separation",10)
	tabs.add_child(team)
	ui["mg_staff_box"]=VBoxContainer.new()
	ui["mg_staff_box"].add_theme_constant_override("separation",10)
	team.add_child(ui["mg_staff_box"])
	var expansions:=VBoxContainer.new()
	expansions.name="Expansion"
	expansions.add_theme_constant_override("separation",10)
	tabs.add_child(expansions)
	ui["mg_expansion_box"]=VBoxContainer.new()
	ui["mg_expansion_box"].add_theme_constant_override("separation",10)
	expansions.add_child(ui["mg_expansion_box"])
	var style:=VBoxContainer.new()
	style.name="Style"
	style.add_theme_constant_override("separation",10)
	tabs.add_child(style)
	ui["mg_style_box"]=VBoxContainer.new()
	ui["mg_style_box"].add_theme_constant_override("separation",10)
	style.add_child(ui["mg_style_box"])

func _make_overlay(_name: String) -> ColorRect:
	var overlay:=ColorRect.new()
	overlay.color=Color(0.015,0.02,0.04,0.94)
	overlay.position=Vector2.ZERO
	overlay.size=Vector2(1280,720)
	hud_layer.add_child(overlay)
	return overlay

func _make_center_panel(parent: Control, size: Vector2) -> PanelContainer:
	var p:=PanelContainer.new()
	p.size=size
	p.position=Vector2((1280-size.x)/2,(720-size.y)/2)
	_style_panel(p,Color("#121827"))
	parent.add_child(p)
	return p

func _style_panel(panel: PanelContainer, color: Color) -> void:
	var sb:=StyleBoxFlat.new()
	sb.bg_color=color
	sb.corner_radius_top_left=14
	sb.corner_radius_top_right=14
	sb.corner_radius_bottom_left=14
	sb.corner_radius_bottom_right=14
	sb.border_width_left=1
	sb.border_width_top=1
	sb.border_width_right=1
	sb.border_width_bottom=1
	sb.border_color=Color(0.45,0.55,0.7,0.35)
	sb.content_margin_left=18
	sb.content_margin_right=18
	sb.content_margin_top=14
	sb.content_margin_bottom=14
	panel.add_theme_stylebox_override("panel",sb)

func _label(text: String, size: int, color: Color) -> Label:
	var l:=Label.new()
	l.text=text
	l.add_theme_font_size_override("font_size",size)
	l.add_theme_color_override("font_color",color)
	return l

func _show_start_overlay() -> void:
	game["paused"] = true
	ui["start_overlay"].visible=true
	ui["continue_btn"].visible=FileAccess.file_exists(SAVE_PATH)

func _new_campaign() -> void:
	_reset_game_state()
	_clear_simulation()
	_apply_expansion_visibility()
	ui["start_overlay"].visible=false
	_start_day()

func _continue_campaign() -> void:
	if not _load_save():
		_new_campaign()
		return
	_clear_simulation()
	_apply_expansion_visibility()
	ui["start_overlay"].visible=false
	_start_day()

func _start_day() -> void:
	game["time_left"] = SHIFT_SECONDS + (game["day"]-1)*4.0
	game["served_today"] = 0
	game["earned_today"] = 0.0
	game["walkouts_today"] = 0
	game["walkout_meter"] = 0
	game["target"] = 5 + game["day"] * 2
	game["running"] = true
	game["paused"] = false
	spawn_timer = 2.0
	staff_timers = {"cook":5.0,"waiter":2.5,"cleaner":3.0}
	ui["management_overlay"].visible=false
	_status("Day %d is open. Seat guests, cook, deliver and keep tables moving." % game["day"])
	_refresh_all_ui()

func _start_next_day() -> void:
	if game["day"] >= game["max_days"]:
		_finish_campaign()
		return
	game["day"] += 1
	_save_game()
	_start_day()

func _physics_process(delta: float) -> void:
	_move_player(delta)
	_update_interaction_prompt()
	if not game["running"] or game["paused"]:
		return
	_update_action(delta)
	game["time_left"] = max(0.0, game["time_left"] - delta)
	spawn_timer -= delta
	if spawn_timer <= 0.0 and game["time_left"] > 12.0:
		_spawn_group()
		spawn_timer = max(3.8, 9.5 - game["day"]*0.55 + randf_range(-1.2,1.5))
	_update_groups(delta)
	_update_staff(delta)
	if game["time_left"] <= 0.0:
		_end_day()
	_refresh_hud()

func _move_player(delta: float) -> void:
	if player == null or game["paused"]:
		return
	var dir:=Vector2.ZERO
	if pressed.get(KEY_W,false) or pressed.get(KEY_UP,false):
		dir.y-=1
	if pressed.get(KEY_S,false) or pressed.get(KEY_DOWN,false):
		dir.y+=1
	if pressed.get(KEY_A,false) or pressed.get(KEY_LEFT,false):
		dir.x-=1
	if pressed.get(KEY_D,false) or pressed.get(KEY_RIGHT,false):
		dir.x+=1
	var speed:=250.0
	if pressed.get(KEY_SHIFT,false):
		speed=365.0
	player.velocity = dir.normalized()*speed
	player.move_and_slide()
	player.position.x=clamp(player.position.x,78.0,WORLD_SIZE.x-78.0)
	player.position.y=clamp(player.position.y,78.0,WORLD_SIZE.y-78.0)
	player.z_index=int(player.position.y)
	if delta > 0 and dir.length() > 0:
		var spr:Sprite2D=player.get_child(0)
		spr.flip_h = dir.x < 0

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey:
		pressed[event.keycode] = event.pressed
		if event.pressed and not event.echo:
			if event.keycode == KEY_E:
				_interact()
			elif event.keycode == KEY_Q:
				_discard_carried()
			elif event.keycode == KEY_M:
				_toggle_menu_overlay()
			elif event.keycode == KEY_TAB:
				_toggle_map_overlay()
			elif event.keycode == KEY_ESCAPE:
				_close_soft_overlays()

func _interact() -> void:
	if game["paused"] or action != null:
		return
	var nearest = _nearest_interactable()
	if nearest == null:
		_status("Nothing to interact with nearby.")
		return
	if nearest["type"] == "station":
		_interact_station(nearest["id"])
	else:
		_interact_table(nearest["table"])

func _nearest_interactable():
	var best = null
	var best_d:=105.0
	for id in stations.keys():
		var s:Node2D=stations[id]
		if not s.visible:
			continue
		var d:=player.position.distance_to(s.position)
		if d<best_d:
			best_d=d
			best={"type":"station","id":id}
	for t in tables:
		if not _table_zone_unlocked(t):
			continue
		var d:=player.position.distance_to(t["pos"])
		if d<best_d:
			best_d=d
			best={"type":"table","table":t}
	return best

func _update_interaction_prompt() -> void:
	if game["paused"]:
		ui["prompt"].text=""
		return
	var n=_nearest_interactable()
	if n==null:
		ui["prompt"].text="Move near a station or table"
	elif n["type"]=="station":
		ui["prompt"].text="[E] %s" % stations[n["id"]].get_meta("label")
	else:
		var t=n["table"]
		ui["prompt"].text="[E] Table %d%s" % [t["id"], " · DIRTY" if t["dirty"] else ""]

func _interact_station(id: String) -> void:
	if id=="stock":
		if game["cash"]>=25:
			game["cash"]-=25
			_add_stock(5)
			_status("Quick stock run: +5 to every ingredient for $25.")
		else:
			_status("Not enough cash for quick stock.")
		return
	if id=="pass":
		if game.get("carried",null)==null:
			_pick_ready_dish()
		else:
			_advance_carried_at_station("pass")
		return
	if id=="fridge":
		if game.get("carried",null)!=null:
			_status("Your tray is occupied.")
			return
		_claim_oldest_order()
		return
	if game.get("carried",null)==null:
		_status("Take a pending order at the fridge first.")
		return
	_advance_carried_at_station(id)

func _claim_oldest_order() -> void:
	var candidate=null
	for o in orders:
		if o["state"]=="pending":
			candidate=o
			break
	if candidate==null:
		_status("No pending orders.")
		return
	var r=recipes[candidate["recipe_id"]]
	if not _has_ingredients(r["ingredients"]):
		_status("Out of ingredients for %s. Restock at storage." % r["name"])
		return
	_consume_ingredients(r["ingredients"])
	candidate["state"]="claimed"
	game["carried"]={"order_id":candidate["id"],"recipe_id":candidate["recipe_id"],"route_index":1,"mode":"raw","table_id":candidate["table_id"]}
	_status("Claimed %s for Table %d." % [r["name"],candidate["table_id"]])
	_refresh_carried()

func _advance_carried_at_station(id: String) -> void:
	var c=game.get("carried",null)
	if c==null:
		return
	if c["mode"]=="ready":
		_status("Ready dish must be delivered to its table.")
		return
	var r=recipes[c["recipe_id"]]
	var route:Array=r["route"]
	if c["route_index"]>=route.size():
		_status("Dish route already complete.")
		return
	var expected:String=route[c["route_index"]]
	if expected!=id:
		_status("Wrong station. Next: %s" % expected.to_upper())
		return
	var base_time:=1.0
	if id=="prep":
		base_time=3.1/max(1.0,1.0+(game["upgrades"]["prep"]-1)*0.18)
	elif id=="stove":
		base_time=4.1/max(1.0,1.0+(game["upgrades"]["stove"]-1)*0.18)
	elif id=="oven":
		base_time=5.0/max(1.0,1.0+(game["upgrades"]["oven"]-1)*0.18)
	elif id=="pass":
		base_time=0.55
	_start_action("%s · %s" % [id.to_upper(),r["name"]],base_time,func(): _finish_station_stage(id))

func _finish_station_stage(id: String) -> void:
	var c=game.get("carried",null)
	if c==null:
		return
	var r=recipes[c["recipe_id"]]
	c["route_index"]+=1
	if id=="pass":
		ready_dishes.append({"order_id":c["order_id"],"recipe_id":c["recipe_id"],"table_id":c["table_id"],"age":0.0})
		var o=_order_by_id(c["order_id"])
		if o!=null:
			o["state"]="ready"
		game["carried"]=null
		_status("%s is ready at the pass." % r["name"])
	else:
		_status("Stage complete. Next: %s" % str(r["route"][c["route_index"]]).to_upper())
	_refresh_carried()

func _pick_ready_dish() -> void:
	if ready_dishes.is_empty():
		_status("No plated dishes are waiting.")
		return
	var d=ready_dishes.pop_front()
	game["carried"]={"order_id":d["order_id"],"recipe_id":d["recipe_id"],"route_index":999,"mode":"ready","table_id":d["table_id"]}
	_status("Picked up %s for Table %d." % [recipes[d["recipe_id"]]["name"],d["table_id"]])
	_refresh_carried()

func _interact_table(table: Dictionary) -> void:
	var c=game.get("carried",null)
	if c!=null and c["mode"]=="ready":
		if c["table_id"]!=table["id"]:
			_status("That dish belongs to Table %d." % c["table_id"])
			return
		_deliver_order(c["order_id"],false)
		game["carried"]=null
		_refresh_carried()
		return
	if table["dirty"]:
		_start_action("Cleaning Table %d" % table["id"],2.4,func(): _clean_table(table))
		return
	_status("Table %d is %s." % [table["id"],"occupied" if table["occupied"] else "available"])

func _deliver_order(order_id: int, automated: bool) -> void:
	var o=_order_by_id(order_id)
	if o==null:
		return
	var g=_group_by_id(o["group_id"])
	if g==null:
		return
	o["state"]="served"
	g["served_count"]+=1
	if not automated:
		_status("Delivered %s to Table %d." % [recipes[o["recipe_id"]]["name"],o["table_id"]])
	for a in g["actors"]:
		a.show_bubble("🍽️")
	if g["served_count"]>=g["order_ids"].size():
		g["state"]="eating"
		g["eat_timer"]=randf_range(9.0,14.0)
		for a in g["actors"]:
			a.show_bubble("😋")

func _start_action(label: String, duration: float, callback: Callable) -> void:
	action={"label":label,"remaining":duration,"total":duration,"callback":callback}
	_status(label+"...")

func _update_action(delta: float) -> void:
	if action==null:
		return
	action["remaining"]-=delta
	if action["remaining"]<=0:
		var cb:Callable=action["callback"]
		action=null
		cb.call()

func _discard_carried() -> void:
	var c=game.get("carried",null)
	if c==null:
		return
	var o=_order_by_id(c["order_id"])
	if o!=null and o["state"]!="served":
		o["state"]="pending"
	game["carried"]=null
	_status("Dish discarded. Order returned to queue.")
	_refresh_carried()

func _spawn_group() -> void:
	if _queue_count()>=4:
		return
	var size:=randi_range(1,4)
	var id:=next_group_id
	next_group_id+=1
	var actors:=[]
	var customer_paths=["res://assets/characters/customer_01.svg","res://assets/characters/customer_02.svg","res://assets/characters/customer_03.svg","res://assets/characters/customer_04.svg","res://assets/characters/customer_05.svg","res://assets/characters/customer_06.svg"]
	for i in size:
		var a:CustomerActor=CustomerActor.new()
		actors_root.add_child(a)
		a.position=Vector2(1280+i*34,60-randi_range(0,20))
		a.setup(customer_paths[randi()%customer_paths.size()],id,i,randf_range(-8,10))
		actors.append(a)
	var g={"id":id,"size":size,"actors":actors,"state":"queue","table_id":-1,"patience":100.0+_patience_bonus(),"browse":0.0,"eat_timer":0.0,"served_count":0,"order_ids":[],"seat_delay":4.2/(1.0+game["staff"]["host"]*0.8),"queue_age":0.0}
	groups.append(g)
	_reflow_queue()
	_status("A party of %d arrived." % size)

func _update_groups(delta: float) -> void:
	for d in ready_dishes:
		d["age"]+=delta
	for g in groups.duplicate():
		if g["state"] in ["queue","browsing","waiting"]:
			var drain:=delta*(1.0 if g["state"]=="waiting" else 0.55)
			g["patience"]-=drain
		if g["patience"]<=0 and g["state"] not in ["eating","leaving"]:
			_walkout_group(g,"patience")
			continue
		if g["state"]=="queue":
			g["queue_age"]+=delta
			g["seat_delay"]-=delta
			if g["seat_delay"]<=0:
				_try_seat_group(g)
		elif g["state"]=="walking_to_table":
			var arrived:=true
			for a in g["actors"]:
				if a.moving:
					arrived=false
			if arrived:
				g["state"]="browsing"
				g["browse"]=randf_range(3.0,6.5)
				for a in g["actors"]:
					a.set_seated(true)
					a.show_bubble("📖")
		elif g["state"]=="browsing":
			g["browse"]-=delta
			if g["browse"]<=0:
				_create_group_orders(g)
		elif g["state"]=="eating":
			g["eat_timer"]-=delta
			if g["eat_timer"]<=0:
				_finish_meal(g)
		elif g["state"]=="leaving":
			var done:=true
			for a in g["actors"]:
				if a.moving:
					done=false
			if done:
				_remove_group(g)

func _try_seat_group(g: Dictionary) -> void:
	var table=_find_table_for(g["size"])
	if table==null:
		g["seat_delay"]=1.2
		return
	table["occupied"]=true
	table["group_id"]=g["id"]
	g["table_id"]=table["id"]
	g["state"]="walking_to_table"
	for i in g["actors"].size():
		var a=g["actors"][i]
		a.table_id=table["id"]
		a.go_to(table["seats"][i])
	_reflow_queue()

func _find_table_for(size: int):
	for t in tables:
		if _table_zone_unlocked(t) and not t["occupied"] and not t["dirty"] and t["capacity"]>=size:
			return t
	return null

func _table_zone_unlocked(t: Dictionary) -> bool:
	if t["zone"]=="main":
		return true
	return game["expansions"].get(t["zone"],false)

func _create_group_orders(g: Dictionary) -> void:
	var active:=_active_menu_ids()
	if active.is_empty():
		_walkout_group(g,"empty menu")
		return
	g["state"]="waiting"
	for i in g["size"]:
		var rid:=_choose_recipe(active)
		var id:=next_order_id
		next_order_id+=1
		var o={"id":id,"group_id":g["id"],"table_id":g["table_id"],"recipe_id":rid,"state":"pending","created":Time.get_ticks_msec()/1000.0}
		orders.append(o)
		g["order_ids"].append(id)
	for a in g["actors"]:
		a.show_bubble("🧾")
	_refresh_orders_ui()

func _choose_recipe(active: Array) -> String:
	var candidates:=[]
	for rid in active:
		if _has_ingredients(recipes[rid]["ingredients"]):
			candidates.append(rid)
	if candidates.is_empty():
		candidates=active
	return candidates[randi()%candidates.size()]

func _finish_meal(g: Dictionary) -> void:
	var subtotal:=0.0
	for oid in g["order_ids"]:
		var o=_order_by_id(oid)
		if o!=null:
			subtotal+=float(game["prices"][o["recipe_id"]])
	var tip_rate: float = float(clamp((float(g["patience"])-20.0)/220.0,0.02,0.28)) + float(game["rep"])/1000.0
	var total: float = subtotal * (1.0 + tip_rate)
	game["cash"]+=total
	game["earned_today"]+=total
	game["served_today"]+=1
	game["stats"]["total_tables"]+=1
	game["stats"]["total_revenue"]+=total
	game["rep"]=clamp(game["rep"]+1.2,0.0,100.0)
	var t=_table_by_id(g["table_id"])
	if t!=null:
		t["occupied"]=false
		t["dirty"]=true
		t["group_id"]=-1
	g["state"]="leaving"
	for i in g["actors"].size():
		var a=g["actors"][i]
		a.set_seated(false)
		a.show_bubble("😊")
		a.go_to(Vector2(1290+i*34,50))
	_status("Table %d paid $%.0f including tip." % [g["table_id"],total])
	_refresh_orders_ui()

func _walkout_group(g: Dictionary, reason: String) -> void:
	if g["state"]=="leaving":
		return
	game["walkouts_today"]+=1
	game["walkout_meter"]+=1
	game["stats"]["walkouts"]+=1
	game["rep"]=max(0.0,game["rep"]-3.5)
	for oid in g["order_ids"]:
		_remove_order(oid)
	var t=_table_by_id(g["table_id"])
	if t!=null:
		t["occupied"]=false
		t["dirty"]=true
		t["group_id"]=-1
	g["state"]="leaving"
	for i in g["actors"].size():
		var a=g["actors"][i]
		a.set_seated(false)
		a.show_bubble("😠")
		a.go_to(Vector2(1290+i*34,50))
	_status("A party left unhappy (%s)." % reason)
	if game["walkout_meter"]>=3:
		game["walkout_meter"]=0
		_lose_life("Three customer parties left unhappy.")
	_refresh_orders_ui()

func _remove_group(g: Dictionary) -> void:
	for a in g["actors"]:
		if is_instance_valid(a):
			a.queue_free()
	groups.erase(g)
	_reflow_queue()

func _reflow_queue() -> void:
	var idx:=0
	for g in groups:
		if g["state"]=="queue":
			for j in g["actors"].size():
				g["actors"][j].go_to(Vector2(1120+idx*95+j*26,255))
				idx+=1

func _queue_count() -> int:
	var c:=0
	for g in groups:
		if g["state"]=="queue":
			c+=1
	return c

func _update_staff(delta: float) -> void:
	for role in staff_timers.keys():
		staff_timers[role]-=delta
	if game["staff"]["cook"]>0 and staff_timers["cook"]<=0:
		staff_timers["cook"]=max(4.0,11.0-game["staff"]["cook"]*1.8)
		_cook_auto()
	if game["staff"]["waiter"]>0 and staff_timers["waiter"]<=0:
		staff_timers["waiter"]=max(2.0,5.5-game["staff"]["waiter"]*0.8)
		_waiter_auto()
	if game["staff"]["cleaner"]>0 and staff_timers["cleaner"]<=0:
		staff_timers["cleaner"]=max(2.2,6.2-game["staff"]["cleaner"]*0.9)
		_cleaner_auto()

func _cook_auto() -> void:
	var pending=null
	for o in orders:
		if o["state"]=="pending" and _has_ingredients(recipes[o["recipe_id"]]["ingredients"]):
			pending=o
			break
	if pending==null:
		return
	_consume_ingredients(recipes[pending["recipe_id"]]["ingredients"])
	pending["state"]="ready"
	ready_dishes.append({"order_id":pending["id"],"recipe_id":pending["recipe_id"],"table_id":pending["table_id"],"age":0.0})
	_status("Cook prepared %s." % recipes[pending["recipe_id"]]["name"])

func _waiter_auto() -> void:
	if ready_dishes.is_empty():
		return
	var d=ready_dishes.pop_front()
	_deliver_order(d["order_id"],true)
	_status("Waiter delivered a dish to Table %d." % d["table_id"])

func _cleaner_auto() -> void:
	for t in tables:
		if t["dirty"] and _table_zone_unlocked(t):
			_clean_table(t)
			_status("Cleaner reset Table %d." % t["id"])
			return

func _clean_table(t: Dictionary) -> void:
	t["dirty"]=false

func _end_day() -> void:
	if not game["running"]:
		return
	game["running"]=false
	game["paused"]=true
	var wages:=0
	for role in game["staff"].keys():
		var lvl=int(game["staff"][role])
		wages+=lvl*_staff_wage(role)
	game["cash"]-=wages
	var hit_target=game["served_today"]>=game["target"]
	if not hit_target:
		_lose_life("Daily target missed: %d / %d tables served." % [game["served_today"],game["target"]],true)
		return
	_show_management(wages,true)

func _show_management(wages: int, hit_target: bool) -> void:
	game["paused"]=true
	ui["management_overlay"].visible=true
	ui["day_report"].text="DAY %d REPORT\nTables served: %d / %d · Revenue: $%.0f · Walkouts: %d · Wages: $%d · Reputation: %.0f\nTarget: %s" % [game["day"],game["served_today"],game["target"],game["earned_today"],game["walkouts_today"],wages,game["rep"],"MET" if hit_target else "MISSED"]
	_refresh_management_ui()
	_save_game()

func _lose_life(reason: String, end_day_after := false) -> void:
	if game["paused"] and ui.get("quiz_overlay",null)!=null and ui["quiz_overlay"].visible:
		return
	game["lives"]-=1
	pending_life_reason=reason
	game["paused"]=true
	if questions.is_empty():
		_after_quiz(false,end_day_after)
		return
	current_quiz=questions[randi()%questions.size()]
	ui["quiz_reason"].text="Life lost: "+reason
	ui["quiz_q"].text=current_quiz["en"]+"\n"+current_quiz["es"]
	_clear_children(ui["quiz_answers"])
	for i in current_quiz["options"].size():
		var b:=Button.new()
		b.text=current_quiz["options"][i]
		b.custom_minimum_size=Vector2(0,46)
		b.pressed.connect(func():_answer_quiz(i,end_day_after))
		ui["quiz_answers"].add_child(b)
	ui["quiz_feedback"].text="Correct answer restores the lost life."
	ui["quiz_overlay"].visible=true
	_refresh_hud()

func _answer_quiz(index: int, end_day_after: bool) -> void:
	game["stats"]["quiz_total"]+=1
	var correct=index==int(current_quiz["correct"])
	if correct:
		game["lives"]=min(MAX_LIVES,game["lives"]+1)
		game["stats"]["quiz_right"]+=1
		ui["quiz_feedback"].text="Correct. "+current_quiz["explain"]+" Life restored."
	else:
		ui["quiz_feedback"].text="Incorrect. "+current_quiz["explain"]
	for child in ui["quiz_answers"].get_children():
		child.disabled=true
	var cont:=Button.new()
	cont.text="CONTINUE"
	cont.custom_minimum_size=Vector2(0,46)
	cont.pressed.connect(func():_after_quiz(correct,end_day_after))
	ui["quiz_answers"].add_child(cont)

func _after_quiz(_correct: bool, end_day_after: bool) -> void:
	ui["quiz_overlay"].visible=false
	if game["lives"]<=0:
		_finish_campaign(false)
		return
	if end_day_after:
		_show_management(0,false)
	else:
		game["paused"]=false

func _finish_campaign(victory := true) -> void:
	game["running"]=false
	game["paused"]=true
	var score:=int(game["stats"]["total_revenue"]+game["rep"]*18+game["cash"]+game["stats"]["total_tables"]*35-game["stats"]["walkouts"]*20)
	ui["end_text"].text=("Restaurant consolidated!" if victory and game["lives"]>0 else "The restaurant closed before completing the campaign.")+"\n\nFinal score: %d\nCash: $%.0f · Reputation: %.0f · Tables served: %d · Revenue: $%.0f\nGeometry Rescue: %d/%d" % [score,game["cash"],game["rep"],game["stats"]["total_tables"],game["stats"]["total_revenue"],game["stats"]["quiz_right"],game["stats"]["quiz_total"]]
	ui["management_overlay"].visible=false
	ui["end_overlay"].visible=true

func _refresh_all_ui() -> void:
	_refresh_hud()
	_refresh_orders_ui()
	_refresh_carried()
	_refresh_menu_overlay()
	_refresh_management_ui()
	_refresh_map()

func _refresh_hud() -> void:
	if not ui.has("day"):
		return
	ui["day"].text="%d / %d" % [game["day"],game["max_days"]]
	var sec:=int(game["time_left"])
	ui["time"].text="%02d:%02d" % [sec/60,sec%60]
	ui["cash"].text="$%.0f" % game["cash"]
	ui["rep"].text="%.0f" % game["rep"]
	ui["lives"].text="❤".repeat(max(0,game["lives"]))
	ui["served"].text="%d / %d" % [game["served_today"],game["target"]]
	ui["inventory"].text="Stock: greens %d · bread %d · beef %d · pasta %d · chicken %d" % [game["inventory"]["greens"],game["inventory"]["bread"],game["inventory"]["beef"],game["inventory"]["pasta"],game["inventory"]["chicken"]]

func _refresh_orders_ui() -> void:
	if not ui.has("orders_box"):
		return
	_clear_children(ui["orders_box"])
	var visible_count:=0
	for o in orders:
		if o["state"] in ["served","cancelled"]:
			continue
		var g=_group_by_id(o["group_id"])
		if g==null:
			continue
		var l:=_label("T%d · %s · %s · %.0f%% patience" % [o["table_id"],recipes[o["recipe_id"]]["icon"]+" "+recipes[o["recipe_id"]]["name"],o["state"].to_upper(),g["patience"]],14,Color("#e7edf8"))
		l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
		ui["orders_box"].add_child(l)
		visible_count+=1
		if visible_count>=9:
			break
	if visible_count==0:
		ui["orders_box"].add_child(_label("No active tickets.",14,Color("#9ca8bb")))

func _refresh_carried() -> void:
	if not ui.has("carried"):
		return
	var c=game.get("carried",null)
	if c==null:
		ui["carried"].text="Tray: empty"
	else:
		var r=recipes[c["recipe_id"]]
		ui["carried"].text="Tray: %s %s · Table %d · %s" % [r["icon"],r["name"],c["table_id"],"READY TO DELIVER" if c["mode"]=="ready" else "Next: "+str(r["route"][c["route_index"]]).to_upper()]

func _refresh_menu_overlay() -> void:
	if not ui.has("menu_grid"):
		return
	_clear_children(ui["menu_grid"])
	for rid in _active_menu_ids():
		var r=recipes[rid]
		var card:=HBoxContainer.new()
		card.custom_minimum_size=Vector2(410,82)
		var tex:=TextureRect.new()
		tex.texture=load(r["asset"])
		tex.custom_minimum_size=Vector2(70,70)
		tex.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
		tex.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		card.add_child(tex)
		var txt:=_label("%s\n$%d · %s" % [r["name"],game["prices"][rid],str(r["ingredients"].keys())],15,Color.WHITE)
		txt.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
		card.add_child(txt)
		ui["menu_grid"].add_child(card)

func _refresh_management_ui() -> void:
	if not ui.has("mg_cash"):
		return
	ui["mg_cash"].text="Cash $%.0f" % game["cash"]
	ui["mg_inventory"].text="Inventory: "+JSON.stringify(game["inventory"])
	for id in ["prep","stove","oven"]:
		var lvl=int(game["upgrades"][id])
		var cost=70+lvl*55
		ui["upgrade_"+id].text="%s LEVEL %d\nUpgrade: $%d" % [id.to_upper(),lvl,cost]
	_clear_children(ui["mg_menu_box"])
	for rid in recipes.keys():
		var r=recipes[rid]
		var row:=HBoxContainer.new()
		row.custom_minimum_size=Vector2(980,62)
		var tex:=TextureRect.new()
		tex.texture=load(r["asset"])
		tex.custom_minimum_size=Vector2(54,54)
		tex.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
		tex.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		row.add_child(tex)
		var unlocked=rid in game["unlocked_recipes"]
		var name:=_label("%s · $%d" % [r["name"],game["prices"][rid]],16,Color.WHITE)
		name.custom_minimum_size=Vector2(250,50)
		row.add_child(name)
		if unlocked:
			var toggle:=Button.new()
			toggle.text="ACTIVE" if game["menu"].get(rid,false) else "INACTIVE"
			toggle.pressed.connect(func():_toggle_recipe(rid))
			row.add_child(toggle)
			var minus:=Button.new()
			minus.text="- $"
			minus.pressed.connect(func():_change_price(rid,-1))
			row.add_child(minus)
			var plus:=Button.new()
			plus.text="+ $"
			plus.pressed.connect(func():_change_price(rid,1))
			row.add_child(plus)
		else:
			var unlock:=Button.new()
			var cost=int(r["unlock_cost"])
			unlock.text="UNLOCK $%d"%cost
			unlock.pressed.connect(func():_unlock_recipe(rid))
			row.add_child(unlock)
		ui["mg_menu_box"].add_child(row)
	_clear_children(ui["mg_staff_box"])
	for role in ["host","cook","waiter","cleaner"]:
		var row:=HBoxContainer.new()
		var lvl=int(game["staff"][role])
		var l:=_label("%s · Level %d · Wage $%d/day"%[role.capitalize(),lvl,lvl*_staff_wage(role)],17,Color.WHITE)
		l.custom_minimum_size=Vector2(460,52)
		row.add_child(l)
		var b:=Button.new()
		b.text=("HIRE" if lvl==0 else "TRAIN")+" · $%d"%_staff_hire_cost(role,lvl)
		b.pressed.connect(func():_hire_or_train(role))
		row.add_child(b)
		ui["mg_staff_box"].add_child(row)
	_clear_children(ui["mg_expansion_box"])
	for exp in ["hall_b","terrace","kitchen_wing"]:
		var owned=game["expansions"][exp]
		var cost={"hall_b":280,"terrace":420,"kitchen_wing":360}[exp]
		var b:=Button.new()
		b.text="%s · %s"%[exp.replace("_"," ").to_upper(),"OWNED" if owned else "$%d"%cost]
		b.disabled=owned
		b.custom_minimum_size=Vector2(0,58)
		b.pressed.connect(func():_buy_expansion(exp,cost))
		ui["mg_expansion_box"].add_child(b)
	_clear_children(ui["mg_style_box"])
	for style in ["classic","garden","neon"]:
		var owned=style in game["styles_owned"]
		var active=game["style"]==style
		var cost={"classic":0,"garden":160,"neon":240}[style]
		var b:=Button.new()
		b.text="%s · %s"%[style.to_upper(),"ACTIVE" if active else ("ACTIVATE" if owned else "$%d"%cost)]
		b.disabled=active
		b.custom_minimum_size=Vector2(0,56)
		b.pressed.connect(func():_buy_or_activate_style(style,cost))
		ui["mg_style_box"].add_child(b)

func _refresh_map() -> void:
	if not ui.has("map_text"):
		return
	ui["map_text"].text="🏠 Lobby: OPEN\n🍽️ Main Hall: OPEN · 11 tables\n🍽️ Hall B: %s · +4 tables\n🌿 Garden Terrace: %s · +5 tables\n🔥 Kitchen Wing: %s · unlocks oven\n📦 Storage: OPEN\n\nCapacity: %d seats\nStaff: Host L%d · Cook L%d · Waiter L%d · Cleaner L%d" % [_owned_text("hall_b"),_owned_text("terrace"),_owned_text("kitchen_wing"),_seat_capacity(),game["staff"]["host"],game["staff"]["cook"],game["staff"]["waiter"],game["staff"]["cleaner"]]

func _owned_text(exp:String)->String:return "OPEN" if game["expansions"][exp] else "LOCKED"
func _seat_capacity()->int:
	var total:=0
	for t in tables:
		if _table_zone_unlocked(t):
			total+=t["capacity"]
	return total

func _toggle_menu_overlay() -> void:
	if not ui.has("menu_overlay") or ui["management_overlay"].visible or ui["quiz_overlay"].visible:
		return
	ui["menu_overlay"].visible=not ui["menu_overlay"].visible
	game["paused"]=ui["menu_overlay"].visible
	if ui["menu_overlay"].visible:
		_refresh_menu_overlay()

func _toggle_map_overlay() -> void:
	if not ui.has("map_overlay") or ui["management_overlay"].visible or ui["quiz_overlay"].visible:
		return
	ui["map_overlay"].visible=not ui["map_overlay"].visible
	game["paused"]=ui["map_overlay"].visible
	if ui["map_overlay"].visible:
		_refresh_map()

func _close_soft_overlays() -> void:
	if ui["menu_overlay"].visible:
		ui["menu_overlay"].visible=false
		game["paused"]=false
	elif ui["map_overlay"].visible:
		ui["map_overlay"].visible=false
		game["paused"]=false

func _buy_kitchen_upgrade(id:String)->void:
	var lvl=int(game["upgrades"][id])
	var cost=70+lvl*55
	if game["cash"]<cost:
		_status("Not enough cash.")
		return
	game["cash"]-=cost
	game["upgrades"][id]=lvl+1
	_refresh_management_ui()
	_save_game()

func _restock_all()->void:
	if game["cash"]<65:
		_status("Not enough cash.")
		return
	game["cash"]-=65
	_add_stock(10)
	_refresh_management_ui()
	_save_game()

func _add_stock(amount:int)->void:
	for k in game["inventory"].keys():
		game["inventory"][k]+=amount

func _toggle_recipe(rid:String)->void:
	var active_count=_active_menu_ids().size()
	if game["menu"].get(rid,false) and active_count<=2:
		_status("Keep at least two dishes active.")
		return
	if not game["menu"].get(rid,false) and active_count>=6:
		_status("Maximum six active dishes.")
		return
	game["menu"][rid]=not game["menu"].get(rid,false)
	_refresh_management_ui()
	_refresh_menu_overlay()
	_save_game()

func _change_price(rid:String,delta:int)->void:
	game["prices"][rid]=clamp(int(game["prices"][rid])+delta,8,45)
	_refresh_management_ui()
	_save_game()

func _unlock_recipe(rid:String)->void:
	var cost=int(recipes[rid]["unlock_cost"])
	if game["cash"]<cost:
		_status("Not enough cash.")
		return
	if rid=="pizza" and not game["expansions"]["kitchen_wing"]:
		_status("Pizza needs the Kitchen Wing oven.")
		return
	game["cash"]-=cost
	game["unlocked_recipes"].append(rid)
	game["menu"][rid]=false
	_refresh_management_ui()
	_save_game()

func _hire_or_train(role:String)->void:
	var lvl=int(game["staff"][role])
	if lvl>=3:
		_status("Maximum staff level.")
		return
	var cost=_staff_hire_cost(role,lvl)
	if game["cash"]<cost:
		_status("Not enough cash.")
		return
	game["cash"]-=cost
	game["staff"][role]=lvl+1
	_spawn_or_refresh_staff()
	_refresh_management_ui()
	_save_game()

func _staff_hire_cost(role:String,lvl:int)->int:
	var base={"host":90,"cook":150,"waiter":120,"cleaner":80}[role]
	return base+lvl*90
func _staff_wage(role:String)->int:return {"host":18,"cook":30,"waiter":24,"cleaner":16}[role]

func _spawn_or_refresh_staff()->void:
	for n in employee_nodes.values():
		if is_instance_valid(n):
			n.queue_free()
	employee_nodes.clear()
	var defs={"host":["res://assets/staff/host.svg",Vector2(1120,310)],"cook":["res://assets/staff/cook.svg",Vector2(520,340)],"waiter":["res://assets/staff/waiter.svg",Vector2(930,670)],"cleaner":["res://assets/staff/cleaner.svg",Vector2(1950,1050)]}
	for role in defs.keys():
		if game["staff"][role]>0:
			var s:=Sprite2D.new()
			s.texture=load(defs[role][0])
			s.position=defs[role][1]
			s.scale=Vector2(.76,.76)
			s.z_index=int(s.position.y)
			actors_root.add_child(s)
			employee_nodes[role]=s

func _buy_expansion(exp:String,cost:int)->void:
	if game["cash"]<cost:
		_status("Not enough cash.")
		return
	game["cash"]-=cost
	game["expansions"][exp]=true
	if exp=="kitchen_wing":
		stations["oven"].visible=true
	_apply_expansion_visibility()
	_refresh_management_ui()
	_refresh_map()
	_save_game()

func _apply_expansion_visibility()->void:
	for child in world_root.get_children():
		if child.has_meta("locked_zone") and child.get_meta("locked_zone"):
			var exp=child.get_meta("expansion")
			var lock=child.get_node_or_null("LockLabel")
			if lock!=null:
				lock.visible=not game["expansions"].get(exp,false)
	for t in tables:
		t["node"].visible=_table_zone_unlocked(t)
	if stations.has("oven"):
		stations["oven"].visible=game["expansions"]["kitchen_wing"]

func _buy_or_activate_style(style:String,cost:int)->void:
	if style not in game["styles_owned"]:
		if game["cash"]<cost:
			_status("Not enough cash.")
			return
		game["cash"]-=cost
		game["styles_owned"].append(style)
	game["style"]=style
	_status("Style changed to %s."%style)
	_refresh_management_ui()
	_save_game()

func _patience_bonus()->float:
	var bonus: float = float(game["staff"]["host"]) * 3.0
	if game["style"]=="garden":
		bonus+=9.0
	elif game["style"]=="neon":
		bonus+=5.0
	return bonus

func _has_ingredients(need:Dictionary)->bool:
	for k in need.keys():
		if int(game["inventory"].get(k,0))<int(need[k]):
			return false
	return true
func _consume_ingredients(need:Dictionary)->void:
	for k in need.keys():
		game["inventory"][k]-=int(need[k])
func _active_menu_ids()->Array:
	var arr:=[]
	for rid in game["unlocked_recipes"]:
		if game["menu"].get(rid,false):
			arr.append(rid)
	return arr

func _order_by_id(id:int):
	for o in orders:
		if o["id"]==id:
			return o
	return null
func _group_by_id(id:int):
	for g in groups:
		if g["id"]==id:
			return g
	return null
func _table_by_id(id:int):
	for t in tables:
		if t["id"]==id:
			return t
	return null
func _remove_order(id:int)->void:
	var o: Variant = _order_by_id(id)
	if o != null:
		o["state"] = "cancelled"
	for d in ready_dishes.duplicate():
		if d["order_id"]==id:
			ready_dishes.erase(d)

func _clear_simulation()->void:
	for g in groups:
		for a in g["actors"]:
			if is_instance_valid(a):
				a.queue_free()
	groups.clear()
	orders.clear()
	ready_dishes.clear()
	next_group_id=1
	next_order_id=1
	action=null
	game["carried"]=null
	for t in tables:
		t["occupied"]=false
		t["dirty"]=false
		t["group_id"]=-1
	_spawn_or_refresh_staff()

func _status(text:String)->void:
	if ui.has("status"):
		ui["status"].text=text

func _clear_children(node:Node)->void:
	for child in node.get_children():
		child.queue_free()

func _save_game()->void:
	var serial={}
	for k in game.keys():
		if k!="carried":
			serial[k]=game[k]
	var f:=FileAccess.open(SAVE_PATH,FileAccess.WRITE)
	if f!=null:
		f.store_string(JSON.stringify(serial))

func _load_save()->bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var parsed=JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if typeof(parsed)!=TYPE_DICTIONARY:
		return false
	game=parsed
	game["running"]=false
	game["paused"]=true
	game["carried"]=null
	return true
