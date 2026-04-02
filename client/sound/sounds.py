# Audio asset registry

MUSIC_TRACKS: dict[str, str] = {
    "lobby": "assets/music/lobby_menu_music.wav",
    "ingame": "assets/music/ingame_music.wav",
    "win_music": "assets/music/win_music.wav",
    "lose_music": "assets/music/lose_music.wav",
}

SFX: dict[str, str] = {
    "button_click": "assets/sounds/button.wav",
    "tile_shift": "assets/sounds/tile_shift.wav",
    "player_move": "assets/sounds/move_player.wav",
    "your_turn": "assets/sounds/button.wav", # add
    "timer_beep": "assets/sounds/timer.wav", # add
    "treasure_collect": "assets/sounds/collect_sound.wav", # add
    "treasure_collect_meow": "assets/sounds/meow.mp3",
    "error": "assets/sounds/error_sound.wav", # add
}
