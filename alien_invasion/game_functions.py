# -*- coding: utf-8 -*-
import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep

#按键按下事件
def check_keydown_events(event,ai_settings,screen,ship,bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif event.key == pygame.K_q:
        sys.exit()

#按键抬起事件
def check_keyup_events(event,ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    if event.key == pygame.K_LEFT:
        ship.moving_left = False

#paly按钮事件
def check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y):
    button_clicked = play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        #重置增长量
        ai_settings.initialize_dynamic_settings()
        #游戏开始后隐藏光标
        pygame.mouse.set_visible(False)
        #如果点击的是play按钮
        if play_button.rect.collidepoint(mouse_x,mouse_y):
            stats.reset_stats()
            stats.game_active = True

            #
            sb.prep_score()
            sb.prep_high_score()
            sb.prep_level()
            sb.prep_ships()

            #清空外星人列表和子弹列表
            aliens.empty()
            bullets.empty()

            #创建新的一群外星人和飞船，并让飞船居中
            create_fleet(ai_settings,screen,ship,aliens)
            ship.center_ship()

#按键事件处理
def check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets):
    for event in pygame.event.get():
        #点击窗口的差，退出游戏
        if event.type == pygame.QUIT:
            sys.exit()
        #按键按下事件
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        #按键抬起事件
        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)
        #鼠标按下事件
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y)

 #
def update_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button):
    screen.fill(ai_settings.bg_color)
    #绘画子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    #绘画飞船
    ship.blitme()
    #绘画外星人
    aliens.draw(screen)
    #显示得分
    sb.show_score()
    #如果游戏处于非活动状态就绘制play按钮
    if not stats.game_active:
        play_button.draw_button()

    pygame.display.flip()

def check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets):
    #检查是否有子弹击中外星人，如果是就删除相应的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)
    #每击落一个外星人则记一分
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points
            sb.prep_score()
        check_high_score(stats,sb)

    if len(aliens) == 0:
        #删除现有的子弹
        bullets.empty()
        #提升速度
        ai_settings.increase_speed()
        #提升等级
        stats.level += 1
        sb.prep_level()
        #新建一群外星人
        create_fleet(ai_settings,screen,ship,aliens)

#重画子弹
def update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets):
    bullets.update()
    #删除已经消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets)

#发射子弹
def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def get_number_aliens_x(ai_settings,alien_width):
    available_space_x = ai_settings.screen_width -2 * alien_width
    number_aliens_x = int(available_space_x / (2*alien_width))
    return number_aliens_x

#创建外星人
def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    alien = Alien(ai_settings,screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

#创建一群外星人
def create_fleet(ai_settings,screen,ship,aliens):
    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows = get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)

def get_number_rows(ai_settings,ship_height,alien_height):
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

#飞船被外星人撞击后处理
def ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets):
    if stats.ships_left > 0:
        #更新剩余飞船数量
        stats.ships_left -= 1
        sb.prep_ships()
        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

#检查是否有外星人达到了屏幕底端
def check_aliens_bottom(ai_settings,screen,stats,sb,ship,aliens,bullets):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)
            break

#
def update_aliens(ai_settings,screen,stats,sb,ship,aliens,bullets):
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    #处理外星人和飞船相撞
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)

    check_aliens_bottom(ai_settings,screen,stats,sb,ship,aliens,bullets)

def check_fleet_edges(ai_settings,aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1



#检测是否产生了最高分
def check_high_score(stats,sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
