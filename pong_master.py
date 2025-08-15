import pygame
import colorsys
import pickle
import math
import random

from base_app import BaseApp

class Ball:
    def __init__(self, screen_size, angle=math.radians(135), speed=300.0, color=(0, 0, 0)):
        self.rect = pygame.Rect(screen_size[0] // 2, screen_size[1] // 2,
                                 screen_size[1] // 40, screen_size[1] // 40)

        self.ball_angle = angle
        self.ball_speed = speed
        self.color = color
        self.ball_pos: list[float] = [self.rect.left, self.rect.top]

        self.last_trail_time = 0.0
        self.trail_length = 8
        self.trail_interval = 0.015
        self.trail = []

    @staticmethod
    def biased_random(start, end, alpha=0.3):
        r = random.betavariate(alpha, alpha)
        return start + (end - start) * r

    def update(self, delta, screen_size, on_death=None, game=None):
        self.ball_pos[0] += self.ball_speed * math.sin(self.ball_angle) * delta
        self.ball_pos[1] += self.ball_speed * math.cos(self.ball_angle) * delta

        if self.rect.left < 0:
            self.ball_pos[0] = 0
            self.ball_angle = -self.ball_angle

        if self.rect.right > screen_size[0]:
            self.ball_pos[0] = screen_size[0] - self.rect.width
            self.ball_angle = -self.ball_angle

        if self.rect.top < 0:
            self.ball_pos[1] = 0
            self.ball_angle = math.pi - self.ball_angle

        if self.rect.bottom > screen_size[1]:
            if on_death is not None:
                on_death(game)

            else:
                self.ball_pos[1] = screen_size[1] - self.rect.height
                self.ball_angle = math.pi - self.ball_angle

        self.rect.topleft = (int(self.ball_pos[0]), int(self.ball_pos[1]))

    def on_collide(self, player):
        hit_pos = 2 * (self.rect.centerx - player.centerx) / player.width
        angle = math.pi - hit_pos * math.pi / 4

        if abs(hit_pos) < 0.2:
            angle += self.biased_random(-math.radians(10), math.radians(10))

        self.ball_angle = angle

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.rect.width // 2)

    def update_trail(self, delta):
        self.last_trail_time += delta
        while self.last_trail_time >= self.trail_interval:
            if len(self.trail) == self.trail_length:
                self.trail.pop(0)
            self.trail.append(self.rect.center)
            self.last_trail_time -= self.trail_interval

    def draw_trail(self, screen):
        for i, pos in enumerate(self.trail[::-1]):
            t = (i + 1) / len(self.trail)
            alpha = int(255 * (1 - t))
            radius = int(self.rect.width // 2 * (1 - t) + 1 * t)

            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*self.color, alpha), (radius, radius), radius)

            screen.blit(circle_surface, (pos[0] - radius, pos[1] - radius)) 

class PowerUp:
    def __init__(self, pos, power=None) -> None:
        self.pos = pos
        self.power = power
        self.rect = pygame.Rect(pos, (15, 15))

        self.render_power_up()

    def render_power_up(self):
        self.surf = pygame.Surface((15, 15))
        self.surf.fill((0, 0, 0))
        pygame.draw.ellipse(self.surf, (255, 255, 255), (0, 0, 15, 15))
        self.surf.set_colorkey((0, 0, 0))

    def apply_power(self, *args, **kwargs):
        if self.power is not None:
            self.power(*args, **kwargs)

class PongMaster(BaseApp):
    icon = pygame.image.load('phone/pong_master.png')

    @staticmethod
    def load_high_score():
        try:
            with open("highscore.pkl", "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return 0

    @staticmethod
    def save_high_score(high_score):
        with open("highscore.pkl", "wb") as f:
            pickle.dump(high_score, f)

    def get_next_color(self):
        r, g, b = [x / 255.0 for x in self.color]
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        new_h = (h + self.hue_step) % 1.0  
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, l, s)

        return (int(new_r * 255), int(new_g * 255), int(new_b * 255))
    
    @staticmethod
    def change_lightness(color, amount):
        r, g, b = [x / 255.0 for x in color]
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        l = max(0, min(1, l + amount))
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, l, s)

        return (int(new_r * 255), int(new_g * 255), int(new_b * 255))

    def render_score_text(self, highscore=False):
        if not highscore:
            text = self.score_font.render(str(self.score), True, 
                                          self.score_color)

        else:
            text = self.high_score_font.render(str(self.score), True, self.high_score_color)

        return text

    def render_pause_screen(self):
        pause_screen = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        pause_screen.fill((0, 0, 0))

        pause_text = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 7).render("Paused", True, (255, 255, 255))
        pause_screen.blit(pause_text, (self.screen.get_width() // 2 - pause_text.get_width() // 2,
                                    100))

        self.resume_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() * 0.8 - 50, 200, 100)
        resume_text = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 10).render("Resume", True, (255, 255, 255))

        pygame.draw.rect(pause_screen, (30, 30, 30), self.resume_rect, 0, 20)
        pygame.draw.rect(pause_screen, (255, 255, 255), self.resume_rect, 7, 20)
        pause_screen.blit(resume_text, (self.resume_rect.centerx - resume_text.get_width() // 2,
                                       self.resume_rect.centery - resume_text.get_height() // 2))

        self.menu_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() * 0.8 - 180, 200, 100)
        menu_text = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 10).render("Menu", True, (255, 255, 255))

        pygame.draw.rect(pause_screen, (30, 30, 30), self.menu_rect, 0, 20)
        pygame.draw.rect(pause_screen, (255, 255, 255), self.menu_rect, 7, 20)
        pause_screen.blit(menu_text, (self.menu_rect.centerx - menu_text.get_width() // 2,
                                       self.menu_rect.centery - menu_text.get_height() // 2))
        
        return pause_screen
        
    def start_game(self):
        self.scope = 'play'
        self.keys_utilities = self.scope_to_utilities[self.scope]

        self.ball = Ball(self.screen_size)

        self.player = pygame.Rect(self.screen.get_width() // 2 - self.screen.get_width() // 3,
                                   self.screen.get_height() - 50, 75, 20)

        self.color = (237, 205, 32)
        self.score_color = self.change_lightness(self.color, -0.3)
        self.high_score_color = self.change_lightness(self.color, 0.3)
                    
        self.score = 0
        self.set_record = False
        self.score_text = self.render_score_text()

        self.anim_alpha = 0.0

        pygame.mouse.set_visible(False)

    @staticmethod
    def on_death(game):
        game.scope = 'menu'
        game.keys_utilities = game.scope_to_utilities[game.scope]

        game.last_frame = game.screen.copy()

        if game.set_record:
            game.save_high_score(game.high_score)

        game.render_menu_screen()

        pygame.mouse.set_visible(True)

    def __init__(self, set_active_app, *args, **kwargs):
        scope_to_utilities = {'menu': [{'text': 'press space to start', 'key': 'space'},
                                        {'text': 'press esc to quit', 'key': 'esc'}],
                               'play': [{'text': 'move the mouse to control the paddle', 'key': 'mouse'},
                                         {'text': 'press space to pause', 'key': 'space'}],
                               'pause': [{'text': 'press space to resume', 'key': 'space'},
                                         {'text': 'press esc to return to menu', 'key': 'esc'}]}

        super().__init__(set_active_app, scope='menu', scope_to_utilities=scope_to_utilities)

        self.color: tuple[int, int, int] = (237, 205, 32)
        self.hue_step = 0.23

        self.resume_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() * 0.8 - 50, 200, 100)

        self.pause_screen = self.render_pause_screen()
        self.last_frame = self.screen.copy()
        self.anim_alpha = 255.0

        self.colliding = False

        self.player_surf = pygame.Surface((75, 20))
        self.player_surf.fill((255, 255, 255))
        pygame.draw.rect(self.player_surf, (0, 0, 0), (10, 0, 50, 20))
        pygame.draw.ellipse(self.player_surf, (0, 0, 0), (0, 0, 25, 20))
        pygame.draw.ellipse(self.player_surf, (0, 0, 0), (50, 0, 25, 20))
        self.player_surf.set_colorkey((255, 255, 255))

        self.high_score = self.load_high_score()

        self.score_font = pygame.font.SysFont('bauhaus93', self.screen_size[1] // 8)
        self.high_score_font = pygame.font.SysFont('bauhaus93', self.screen_size[1] // 5)

        self.power_ups = []

        self.menu = pygame.Surface(self.screen_size)
        self.menu_screen = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.render_menu_screen()

        self.menu_balls = []
        for angle in range(0, 360, 36):
            self.menu_balls.append(Ball(self.screen_size, speed=float(random.randint(250, 800)),
                                         angle=math.radians(angle + random.randint(-10, 10)), color=(6, 6, 116)))

        self.menu_balls.append(Ball(self.screen_size, speed=550.0, color=(180, 195, 255)))

    def render_menu_screen(self):
        self.menu.fill((0, 0, 0))

        title_font = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 7)
        title_text = title_font.render("Pong Master", True, (180, 195, 255))
        self.menu.blit(
            title_text,
            (self.menu.get_width() // 2 - title_text.get_width() // 2,
            self.menu.get_height() // 2 - 250)
        )

        label_font = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 20)
        highscore_label = label_font.render("Highscore:", True, (180, 195, 255))

        highscore_value = self.high_score_font.render(str(self.high_score), True, (180, 195, 255))

        highscore_x = self.menu.get_width() // 2 - highscore_value.get_width() // 2
        self.menu.blit(highscore_label, (highscore_x, self.menu.get_height() // 2 - 155))
        self.menu.blit(highscore_value, (highscore_x, self.menu.get_height() // 2 - 150))

        self.play_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() * 0.8 - 50, 200, 100)
        play_text = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 10).render("Play", True, (180, 195, 255))
        pygame.draw.rect(self.menu, (15, 15, 130), self.play_rect, 0, 20)
        pygame.draw.rect(self.menu, (180, 195, 255), self.play_rect, 7, 20)
        self.menu.blit(play_text, (self.play_rect.centerx - play_text.get_width() // 2,
                                    self.play_rect.centery - play_text.get_height() // 2))

        self.quit_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() * 0.8 - 180, 200, 100)
        quit_text = pygame.font.SysFont('bauhaus93', self.screen_size[0] // 10).render("Quit", True, (180, 195, 255))
        pygame.draw.rect(self.menu, (15, 15, 130), self.quit_rect, 0, 20)
        pygame.draw.rect(self.menu, (180, 195, 255), self.quit_rect, 7, 20)
        self.menu.blit(quit_text, (self.quit_rect.centerx - quit_text.get_width() // 2,
                                    self.quit_rect.centery - quit_text.get_height() // 2))

        self.menu.set_colorkey((0, 0, 0))


    def slow_ball(self, amount):
        self.ball.ball_speed = max(200, self.ball.ball_speed - amount)

    def play(self, display, delta):
        mouse_x = self.mouse[0]
        mouse_y = display.get_width() // 2 - self.screen.get_height() // 2

        offset = display.get_width() // 2 - self.screen.get_width() // 2
        mouse_x = max(offset, min(mouse_x + offset, offset + self.screen.get_width() - 1))

        if pygame.mouse.get_pos() != (mouse_x, mouse_y):
            pygame.mouse.set_pos((mouse_x, mouse_y))

        self.mouse = (self.mouse[0], mouse_y)

        self.ball.update(delta, self.screen_size, self.on_death, self)

        if self.ball.rect.colliderect(self.player):
            if not self.colliding:
                self.colliding = True

                self.ball.on_collide(self.player)

                self.score += 1

                if self.score % 5 == 0:
                    self.color = self.get_next_color()
                    self.score_color = self.change_lightness(self.color, -0.2)
                    self.high_score_color = self.change_lightness(self.color, 0.2)
                    self.ball.ball_speed += 110

                if self.score > self.high_score:
                    self.high_score = self.score
                    self.set_record = True

                self.score_text = self.render_score_text(self.set_record)
        else:
            self.colliding = False

        self.player.x = self.mouse[0] - self.player.width // 2

        if self.player.left < 0:
            self.player.left = 0
        elif self.player.right > self.screen.get_width():
            self.player.right = self.screen.get_width()

        if random.random() < 0.08 * delta and len(self.power_ups) < 5:
            self.power_ups.append(
                PowerUp(
                    (random.randint(30, self.screen.get_width() - 30),
                     random.randint(30, self.screen.get_height() - 200)),
                    self.slow_ball
                )
            )

        self.ball.update_trail(delta)

        self.screen.fill(self.color)

        self.screen.blit(self.score_text, (
            self.screen.get_width() // 2 - self.score_text.get_width() // 2,
            self.screen.get_height() // 2 - self.score_text.get_height() // 2
        ))

        power_ups = []
        for power_up in self.power_ups:
            if self.ball.rect.colliderect(power_up.rect):
                power_up.apply_power(70)
                continue
            power_ups.append(power_up)
            self.screen.blit(power_up.surf, power_up.rect)

        self.power_ups = power_ups

        self.ball.draw_trail(self.screen)
        self.ball.draw(self.screen)

        self.screen.blit(self.player_surf, self.player)

    def run(self, display):
        delta = self.clock.tick() / 1000
        self.get_relative_mouse_pos(display)

        if self.scope == 'play':
            self.play(display, delta)

        elif self.scope == 'pause':
            self.screen.fill((0, 0, 0))
            self.animate(delta, self.pause_screen, max_alpha=150)
            self.screen.blit(self.pause_screen, (0, 0))

        elif self.scope == 'menu':
            self.menu_screen.fill((0, 0, 98))


            for menu_ball in self.menu_balls:
                menu_ball.update(delta, self.screen_size)

                menu_ball.update_trail(delta)
                menu_ball.draw_trail(self.menu_screen)

                menu_ball.draw(self.menu_screen)

            self.menu_screen.blit(self.menu, (0, 0))

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.last_frame, (0, 0))
            self.animate(delta, self.menu_screen, max_alpha=255)
            self.screen.blit(self.menu_screen, (0, 0))

    def animate(self, delta, surface, max_alpha):
        self.screen.blit(self.last_frame, (0, 0))
        self.anim_alpha = min(max_alpha, self.anim_alpha + 400 * delta)
        surface.set_alpha(int(self.anim_alpha))

    def events(self, event):
        if self.scope == 'play':
            if event.type == pygame.QUIT:
                self.save_high_score(self.high_score)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mouse.set_visible(True)
                    self.scope = 'pause'
                    self.keys_utilities = self.scope_to_utilities[self.scope]

                    self.anim_alpha = 0
                    self.last_frame = self.screen.copy()

        elif self.scope == 'pause':
            if event.type == pygame.QUIT:
                self.save_high_score(self.high_score)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mouse.set_visible(False)
                    self.scope = 'play'
                    self.keys_utilities = self.scope_to_utilities[self.scope]

                elif event.key == pygame.K_ESCAPE:
                    self.scope = 'menu'
                    self.keys_utilities = self.scope_to_utilities[self.scope]

                    self.anim_alpha = 0
                    self.last_frame = self.screen.copy()

                    if self.set_record:
                        self.save_high_score(self.high_score)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_rect.collidepoint(self.mouse):
                    pygame.mouse.set_visible(False)
                    self.scope = 'play'
                    self.keys_utilities = self.scope_to_utilities[self.scope]

                    self.anim_alpha = 0

                if self.menu_rect.collidepoint(self.mouse):
                    self.scope = 'menu'
                    self.keys_utilities = self.scope_to_utilities[self.scope]

                    self.anim_alpha = 0
                    self.last_frame = self.screen.copy()

                    if self.set_record:
                        self.save_high_score(self.high_score)

        elif self.scope == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_rect.collidepoint(self.mouse):
                    self.start_game()

                elif self.quit_rect.collidepoint(self.mouse):
                    self.save_high_score(self.high_score)
                    self.set_active_app('home')

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.set_active_app('home')

                elif event.key == pygame.K_SPACE:
                    self.start_game()