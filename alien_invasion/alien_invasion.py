# -*- coding: utf-8 -*-
import sys
import pygame

from settings import Settings
from ship import Ship
from alien import Alien
import game_functions as gf
from pygame.sprite import Group
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

def run_game():
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    #创建play按钮
    play_button = Button(ai_settings,screen,"Play")
    #
    stats = GameStats(ai_settings)
    #创建得分牌
    sb = Scoreboard(ai_settings,screen,stats)
    #
    ship = Ship(ai_settings,screen)
    #
    bullets = Group()
    #
    aliens = Group()
    gf.create_fleet(ai_settings,screen,ship,aliens)

    while True:
        gf.check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets)
        if stats.game_active:
            ship.update()
            #处理子弹状态 子弹和外星人的关系
            gf.update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets)
            #处理外星人状态 外星人和飞船的关系
            gf.update_aliens(ai_settings,screen,stats,sb,ship,aliens,bullets)

        gf.update_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button)

run_game()