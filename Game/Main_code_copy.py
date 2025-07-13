#Импорт необходимых библиотек
import pygame
import Save_load
import Audio
import Menu
import settings
pygame.init()
Save_load.load_settings()
settings.music_playing = False
Audio.play_menu_music()
Menu.main_menu()
pygame.quit()