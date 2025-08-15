import pygame

from base_app import BaseApp
import pong_master

pygame.init()

class Home(BaseApp):
    def __init__(self, set_active_app, phone_apps):
        super().__init__(set_active_app, keys_utilities=[{'text': 'Click on any app icon to open it', 'key': 'Click'}])
        self.phone_apps = phone_apps
        self.apps_rect = []
        
        for i, app_name in enumerate(list(self.phone_apps.keys())[1:]):
            x = 12 + 96 * (i % 3)
            y = 12 + 116 * (i // 3)
            app_rect = pygame.Rect(x, y, 84, 84)
            self.apps_rect.append((app_name, app_rect))

        self.homescreen = pygame.image.load(r'phone\homescreen.png')

    def run(self, display):
        self.get_relative_mouse_pos(display)

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.homescreen, (0, 0))

        font = pygame.font.Font(None, 16)

        for app_name, app_rect in self.apps_rect:
            if hasattr(self.phone_apps[app_name], 'icon'):
                    icon = self.phone_apps[app_name].icon.convert_alpha()

                    mask = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                    pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=20)

                    icon = icon.copy()
                    icon.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

                    self.screen.blit(icon, (app_rect.x, app_rect.y))

            else:
                pygame.draw.rect(self.screen, (200, 200, 200), app_rect, border_radius=20)
                
            text_surface = font.render(app_name, True, (0, 0, 0))
            self.screen.blit(text_surface, (app_rect.x + app_rect.width // 2 - text_surface.get_width() // 2,
                                                app_rect.y + app_rect.height + 4))
        
    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for app_name, app_rect in self.apps_rect:
                if app_rect.collidepoint(self.mouse):
                    self.set_active_app(app_name)

                    break

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

phone_scene = pygame.image.load(r'phone\phone.png')
phone_scene.set_colorkey((255, 0, 0))

def set_active_app(app_name):
    global app
    app = phone_apps[app_name](set_active_app, phone_apps)

phone_apps = {
    'home': Home,
    'pong master': pong_master.PongMaster,
}

app = phone_apps['home'](set_active_app, phone_apps)

keys_utilities = []
utils_surfs = []

running = True
def render_utilities(app, utils_surfs):
    font = pygame.font.Font(None, 36)
    key_font = pygame.font.Font(None, 36)
    key_font.set_italic(True)

    for util in app.keys_utilities:
        text = util["text"]
        key_word = util["key"]

        parts = text.split(key_word, 1)
        before = parts[0]
        after = parts[1] if len(parts) > 1 else ""

        before_surf = font.render(before, True, (255, 255, 255))
        key_surf = key_font.render(key_word, True, (255, 255, 255))
        after_surf = font.render(after, True, (255, 255, 255))

        padding = 6
        key_bg_rect = pygame.Rect(0, 0,
                                    key_surf.get_width() + padding * 2,
                                    key_surf.get_height() + padding * 2)

        util_width = before_surf.get_width() + key_bg_rect.width + after_surf.get_width()
        util_height = key_bg_rect.height + padding * 2
        util_surf = pygame.Surface((util_width, util_height), pygame.SRCALPHA)

        util_surf.blit(before_surf, (0, padding))
        offset_x = before_surf.get_width()

        key_bg_rect.topleft = (offset_x, 0)
        pygame.draw.rect(util_surf, (128, 128, 128, 128), key_bg_rect, 0, 20)
        util_surf.blit(key_surf, (offset_x + padding, padding))
        offset_x += key_bg_rect.width

        util_surf.blit(after_surf, (offset_x, padding))

        utils_surfs.append(util_surf)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        app.events(event)

    screen.fill((255, 255, 255))

    app.run(screen)
    screen.blit(app.screen,
             (screen.get_width() // 2 - app.screen.get_width() // 2,
              screen.get_height() // 2 - app.screen.get_height() // 2))

    screen.blit(phone_scene, (0, 0))

    if app.keys_utilities == keys_utilities:
        for i, util_surf in enumerate(utils_surfs):
            screen.blit(util_surf, (10, 10 + i * (util_surf.get_height() + 10)))

    else:
        keys_utilities = app.keys_utilities
        utils_surfs.clear()

        render_utilities(app, utils_surfs)

    pygame.display.flip()

pygame.quit()