import sys, pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard


class AlienInvasion:
    '''
    游戏主运行文件
    飞船可在屏幕内上下左右移动，外星人一波波蛇形从上倒下移动，如外星人碰触飞船或触底，则飞船损失一艘；
    飞船最多发射三发子弹；
    飞船共三艘，全部损失则该局游戏结束；
    '''

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()
        # 自由尺寸
        # self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        # 全屏
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.play_button = Button(self, "Play")

    def _check_events(self):
        # 监听键盘与鼠标事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stats.write_log()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """点击开始按钮，并显示数据信息，隐藏鼠标箭头"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """
        按键之上下左右移动以及射击与退出
        :param event:
        :return:
        """
        if event.key == pygame.K_RIGHT:
            # 向右移动飞船
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            # 向左移动飞船
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            # 向上移动飞船
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            # 向下移动飞船
            self.ship.moving_down = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            self.stats.write_log()
            sys.exit()


    def _check_keyup_events(self, event):
        '''
        松键之上下左右
        :param event:
        :return:
        '''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_bullets_alien_collisions(self):
        '''
        检查子弹与外星人碰撞，并及时更新分数及外星人
        :return:
        '''
        collections = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collections:
            for aliens in collections.values():
                self.stats.score += self.settings.alien_points * len(aliens)

                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1
            self.sb.prep_level()

    def _check_aliens_bottom(self):
        '''
        检查外星人是否触底
        :return:
        '''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        '''
        外星人转向并下移
        :return:
        '''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _fire_bullet(self):
        # 子弹数量小于限定值
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        '''
        创建外星人舰队
        :return:
        '''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (0.1 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(int(number_aliens_x)):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_bnumber):
        '''创建外星人'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_bnumber
        self.aliens.add(alien)

    def _update_bullets(self):
        '''
        更新子弹
        :return:
        '''
        self.bullets.update()
        for bullet in self.bullets.copy():
            # 使用拷贝是因为列表的特性，防止超下标报错
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullets_alien_collisions()

    def _update_aliens(self):
        '''
        更新外星人
        :return:
        '''
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()

    def _update_screen(self):
        '''更新屏幕上的图像，并切换到新屏幕'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _ship_hit(self):
        '''
        飞船坠落
        :return:
        '''
        if self.stats.ships_left > 0:

            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_aliens()
                self._update_bullets()

            self._update_screen()


if __name__ == '__main__':
    # 创建游戏并运行游戏
    ai = AlienInvasion()
    ai.run_game()
