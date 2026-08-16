extends CharacterBody2D
class_name CustomerActor

signal destination_reached(actor)

var target_position := Vector2.ZERO
var moving := false
var move_speed := 92.0
var sprite: Sprite2D
var bubble: Label
var table_id := -1
var group_id := -1
var seat_index := -1

func setup(texture_path: String, group: int, seat: int, speed_bonus := 0.0) -> void:
	group_id = group
	seat_index = seat
	move_speed += speed_bonus
	sprite = Sprite2D.new()
	sprite.texture = load(texture_path)
	sprite.scale = Vector2(0.72, 0.72)
	add_child(sprite)
	bubble = Label.new()
	bubble.text = ""
	bubble.position = Vector2(-34, -82)
	bubble.size = Vector2(68, 28)
	bubble.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bubble.add_theme_font_size_override("font_size", 16)
	bubble.add_theme_color_override("font_color", Color("#172033"))
	bubble.add_theme_color_override("font_shadow_color", Color(1,1,1,0.9))
	bubble.add_theme_constant_override("shadow_offset_x", 1)
	bubble.add_theme_constant_override("shadow_offset_y", 1)
	add_child(bubble)

func go_to(point: Vector2) -> void:
	target_position = point
	moving = true
	set_seated(false)

func set_seated(value: bool) -> void:
	if sprite == null:
		return
	if value:
		sprite.scale = Vector2(0.72, 0.58)
		sprite.position = Vector2(0, 9)
	else:
		sprite.scale = Vector2(0.72, 0.72)
		sprite.position = Vector2.ZERO

func show_bubble(text: String) -> void:
	if bubble != null:
		bubble.text = text

func _physics_process(_delta: float) -> void:
	if moving:
		var delta_pos := target_position - global_position
		if delta_pos.length() < 7.0:
			global_position = target_position
			velocity = Vector2.ZERO
			moving = false
			destination_reached.emit(self)
		else:
			velocity = delta_pos.normalized() * move_speed
			move_and_slide()
	z_index = int(global_position.y)
