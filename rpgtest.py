import pygame
import random
import math

pygame.init()
pygame.mixer.init()

# --- Path ---
Music_Path = r"C:\Users\user\Desktop\Games\bgm.mp3"
Background_Image_Path = r"C:\Users\user\Desktop\Games\background.jpg"
Pixel_Font_Path = r"C:\Users\user\Desktop\Games\PressStart2P-Regular.ttf"

Normal1 = r"C:\Users\user\Desktop\Games\boss\normal-state\normal1.png"
Normal2 = r"C:\Users\user\Desktop\Games\boss\normal-state\normal2.png"
Normal3 = r"C:\Users\user\Desktop\Games\boss\normal-state\normal3.png"

Attack1 = r"C:\Users\user\Desktop\Games\boss\attack-state\attack1.png"
Attack2 = r"C:\Users\user\Desktop\Games\boss\attack-state\attack2.png"
Attack3 = r"C:\Users\user\Desktop\Games\boss\attack-state\attack3.png"
Attack4 = r"C:\Users\user\Desktop\Games\boss\attack-state\attack4.png"

Damage1 = r"C:\Users\user\Desktop\Games\boss\damage-state\damage-light.png"   
Damage2 = r"C:\Users\user\Desktop\Games\boss\damage-state\damage-heavy.png"
Dead_PNG_Path = r"C:\Users\user\Desktop\Games\boss\dead\pixil-frame-0.png"

Knight_Normal1= r"C:\Users\user\Desktop\Games\Knight\normal-state\knight1.png"
Knight_Normal2= r"C:\Users\user\Desktop\Games\Knight\normal-state\knight2.png"
Knight_Normal3= r"C:\Users\user\Desktop\Games\Knight\normal-state\knight3.png"
Knight_Normal4= r"C:\Users\user\Desktop\Games\Knight\normal-state\knight4.png"

Mage_Normal1=r"C:\Users\user\Desktop\Games\Mage\normal-state\mage1.png"
Mage_Normal2=r"C:\Users\user\Desktop\Games\Mage\normal-state\mage2.png"
Mage_Normal3=r"C:\Users\user\Desktop\Games\Mage\normal-state\mage3.png"
Mage_Normal4=r"C:\Users\user\Desktop\Games\Mage\normal-state\mage4.png"

Special_Normal1=r"C:\Users\user\Desktop\Games\Special\special1.png"
Special_Normal2=r"C:\Users\user\Desktop\Games\Special\special2.png"
Special_Normal3=r"C:\Users\user\Desktop\Games\Special\special3.png"
Special_Normal4=r"C:\Users\user\Desktop\Games\Special\special4.png"

Tank_Normal1=r"C:\Users\user\Desktop\Games\Tank\tank1.png"
Tank_Normal2=r"C:\Users\user\Desktop\Games\Tank\tank2.png"
Tank_Normal3=r"C:\Users\user\Desktop\Games\Tank\tank3.png"
Tank_Normal4=r"C:\Users\user\Desktop\Games\Tank\tank4.png"
# --- GAME SCREEN SETUP ---
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# --- GAME FONT SETUP
pixel_font = pygame.font.Font(Pixel_Font_Path, 16)

# --- Background SETUP ---
bg_img=pygame.image.load(Background_Image_Path)
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bg_y = 0
scroll_speed = 2

pygame.mixer.music.load(Music_Path) # Load background music
pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)         # Play music in a loop

# --- Battle Stats ---
clock = pygame.time.Clock()
turn_wait_time = 0  
start_ticks = pygame.time.get_ticks() # Get starting time
turn_count = 1
max_time_seconds = 3600 # 1 hour limit

game_state = "PLANNING"
executor_index = 0
execution_timer = 0

# --- Colors ---
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# --- Logic Classes ---
class Character:
    def __init__(self, name, hp, attk, mp, x, y, anim_dict, skills, df=0, charge=0):
        self.name = name        # Character Name
        self.hp = hp            # Health Points
        self.max_hp = hp        # Max Health Points
        self.attk = attk        # Attack Points
        self.mp = mp            # Mana Points
        self.max_mp = mp        # Max Mana Points
        self.skills=skills
        #self.df = df            # Defense Points
        #self.charge = charge    # Charge Attacks

        self.animations={}
        for state, path_list in anim_dict.items():
            loaded_frames = []
            for path in path_list:
                print(f"DEBUG: Trying to load State: [{state}] | Path: {path} | Type: {type(path)}")
                
                if not isinstance(path, str):
                    print(f"CRITICAL: The variable for {state} is a {type(path)}, not a string!")                
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (200, 200))
                img = pygame.transform.flip(img, False, False)
                loaded_frames.append(img)
            self.animations[state] = loaded_frames
        
        self.rect = self.animations["normal"][0].get_rect(center=(x, y))
        self.state="normal"
        self.frame_index=0
        self.anim_speed = 0.18 # Higher = faster animation

        
        self.start_x = x
        self.shake_x = 0
        self.timer = 0
        self.is_attacking = False
        self.attack_speed = 10 # Speed of the slide
        self.queued_skill = None  # Stores the skill chosen during Ready Phase
        self.action_ready = False
        self.dashboard_rect = pygame.Rect(0, 0, 0, 0)  # Placeholder, will be set in main loop
    
       
    def set_state(self,new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0

    def take_damage(self, damage):
        self.hp=max(0, self.hp - damage)
        if self.hp > 0:
            self.set_state ("hurt")
            self.timer = 30 # Shakes for 30 frames
        else:
            self.set_state("dead")

    def perform_attack(self):
        self.set_state("attack")
        self.is_attacking = True
        self.timer = 20 # Total frames for the slide forward and back

    def update(self):
        # --- HANDLE DEAD STATE ---
        if self.hp <= 0:
            self.set_state("dead")
            self.frame_index = len(self.animations["dead"]) - 1
            return

        # 1. Cycle through animation frames
        current_anim_list = self.animations[self.state]
        self.frame_index += self.anim_speed

        if self.frame_index >= len(current_anim_list):
            if self.state in ["attack","skill","hurt"]:
                self.set_state("normal")
            else:
                self.frame_index = 0

        # --- Handle Hurt Animation (Shake) ---
        if self.timer > 0:
            self.timer -= 1
            if self.state == "hurt":
                self.shake_x = random.randint(-5, 5)
        else:
            self.shake_x = 0

        
        
        # 3. Handle Attack Animation (Slide)
        if self.is_attacking:
            # First half of timer: Slide toward enemy
            if self.timer > 10:
                self.rect.x += self.attack_speed
            # Second half: Slide back to start
            else:
                self.rect.x -= self.attack_speed
            
            # Reset once done
            if self.timer <= 0:
                self.is_attacking = False
                self.rect.centerx = self.start_x
    
    def draw(self, surface):
        # Get current frame based on state
        img = self.animations[self.state][int(self.frame_index)]
        surface.blit(img, (self.rect.x + self.shake_x, self.rect.y))

    def use_skill(self,skill_name,target,skill_data):
        if self.mp >= skill_data["cost"]:
            self.mp -= skill_data["cost"]
            
            if skill_name == "Heal":
                damage_popups.append(DamageText(100, 150, f"+{abs(skill_data['damage'])}", GREEN))
                heal_amount = abs(skill_data["damage"])
                self.hp = min(self.max_hp, self.hp + heal_amount)
                return f"Used {skill_name}! Healed {heal_amount} HP!"
            else:
                target.take_damage(skill_data["damage"])
                damage_popups.append(DamageText(enemy.rect.centerx, enemy.rect.top, f"-{skill_data['damage']}", RED))
                return f"Used {skill_name}! Dealt {skill_data['damage']} damage!"
        return "Not enough Mana!"
    
class Knight(Character):
    def __init__(self,x,y):
        knight_animations = {
            "normal": [Knight_Normal1, Knight_Normal2, Knight_Normal3, Knight_Normal4],
            "attack": [Knight_Normal1], # Don't leave these as empty []
            "skill":  [Knight_Normal1],
            "dead":   [Knight_Normal1],
            "hurt":   [Knight_Normal1]
        }

        knight_skills=[
            {"name": "Slash", "damage": 40, "cost": 10},
            {"name": "Whirlwind", "damage": 60, "cost": 25}
        ]
        super().__init__("Knight",100,15,100,x,y,knight_animations,knight_skills)

class Mage(Character):
    def __init__(self,x,y):
        mage_animations={
            "normal":[Mage_Normal1,Mage_Normal2,Mage_Normal3,Mage_Normal4],
            "attack":[Mage_Normal1],
            "skills":[Mage_Normal1],
            "dead":[Mage_Normal1],
            "hurt":   [Mage_Normal1]

        }
        mage_skills=[
            {"name": "Fireball", "damage": 80, "cost": 30},
            {"name": "Heal", "damage": -50, "cost": 20} # Negative damage = Heal
        ]
        super().__init__("Mage",80,20,150,x,y,mage_animations,mage_skills)

class Special(Character):
     def __init__(self,x,y):
        special_animations={
            "normal":[Special_Normal1,Special_Normal2,Special_Normal3,Special_Normal4],
            "attack":[Special_Normal1],
            "skills":[Special_Normal1],
            "dead":[Special_Normal1],
            "hurt":[Special_Normal1]
        }
        special_skills=[
            {"name": "Shadow Strike", "damage": 100, "cost": 40},
            {"name": "Invisibility", "damage": 0, "cost": 15} # No damage, just a buff
        ]

        super().__init__("Special",90,80,120,x,y,special_animations,special_skills)

class Tank(Character):
    def __init__(self,x,y):
        special_animations={
            "normal":[Tank_Normal1,Tank_Normal2,Tank_Normal3,Tank_Normal4],
            "attack":[Tank_Normal1],
            "skills":[Tank_Normal1],
            "dead":[Tank_Normal1],
            "hurt":[Tank_Normal1]
        }
        tank_skills = [
            {"name": "Shield Bash", "damage": 30, "cost": 5},
            {"name": "Fortify", "damage": 0, "cost": 20} # No damage, just a buff
        ]

        super().__init__("Tank",150,10,80,x,y,special_animations,special_skills)

    

class EnemySprite:
    def __init__(self,name,hp,x,y,attk):
        self.name=name
        self.hp=hp
        self.max_hp=hp
        self.attk=attk
        
        self.normal_frames=[
            pygame.transform.scale(pygame.image.load(Normal1).convert_alpha(),(350,350)),
            pygame.transform.scale(pygame.image.load(Normal2).convert_alpha(),(350,350)),
            pygame.transform.scale(pygame.image.load(Normal3).convert_alpha(),(350,350)),
        ]

        self.attack_frames=[
            pygame.transform.scale(pygame.image.load(Attack1).convert_alpha(),(350,350)),
            pygame.transform.scale(pygame.image.load(Attack2).convert_alpha(),(350,350)),
            pygame.transform.scale(pygame.image.load(Attack3).convert_alpha(),(350,350)),
            pygame.transform.scale(pygame.image.load(Attack4).convert_alpha(),(350,350)),
        ]

        self.img_hurt_light = pygame.transform.scale(pygame.image.load(Damage1).convert_alpha(),(350,350))
        self.img_hurt_heavy = pygame.transform.scale(pygame.image.load(Damage2).convert_alpha(),(350,350))
        
        self.frame_index = 0
        self.attack_index = 0         # For attack animation (The missing one!)
        self.attack_hold_timer = 0
        self.anim_speed = 0.1

        self.img_dead=pygame.image.load(Dead_PNG_Path).convert_alpha()
        self.img_dead=pygame.transform.scale(self.img_dead,(350,350))
    
        self.rect = self.normal_frames[0].get_rect(center=(x, y))
        self.start_x=x
        self.start_y=y
        self.animation_step = 0
        self.shake_x = 0
        self.timer = 0
        self.state = "normal"
        self.is_animating_attack = False
        
        

        
    
    def take_damage(self,damage):
        self.hp -= damage
        
        if self.hp <= 0:
            self.state = "dead"
        elif damage >=100:
            self.state = "hurt_heavy"
            self.timer = 50
        else:
            self.state = "hurt_light"
            self.timer = 30
    
    def perform_attack(self):
        self.state = "attack"
        self.timer = 20 # Show attack frame for 20 frames
    
    def update(self):
        # 1. Normal Animation Logic
        if self.state == "normal":
            self.frame_index += self.anim_speed
            if self.frame_index >= len(self.normal_frames):
                self.frame_index = 0
            self.animation_step += 0.05 #Hovering effect
            self.shake_x = 0

        # 2. Attack Animation Logic
        elif self.state == "attack":
            if self.attack_index < len(self.attack_frames) - 1:
                self.attack_index += 0.15
            else:
                self.attack_index =len(self.attack_frames) - 1
                self.attack_hold_timer += 1

                if self.attack_hold_timer >=40:
                    self.deal_damage_now = True  # Signal to main loop to subtract HP
                    self.attack_index = 0
                    self.attack_hold_timer=0        
                    self.state = "normal"        # Snap back to idle
                    self.is_animating_attack = False # Reset toggle

        # 3. Hurt Animation Logic
        elif "hurt" in self.state:
            if self.timer > 0:
                self.timer -= 1
                if self.state == "hurt_heavy":
                    self.shake_x = random.randint(-12, 12)
                else:
                    self.shake_x = random.randint(-4, 4)
            else:
                self.state = "normal"
                self.shake_x = 0
        
        # 4. Dead State Logic
        elif self.state == "dead":
            self.shake_x = 0
            self.animation_step = 0 # Stop hovering when dead

        else:
            if self.state != "dead":
                self.state = "normal"
                self.shake_x = 0
    
    def draw(self, surface):
        # Only hover if not attacking (looks more stable during the hit)
        hover_y = math.sin(self.animation_step) * 15 if self.state == "normal" else 0

        
        if self.state == "normal":
            # Convert float index to int (0, 1, 2, or 3)
            img = self.normal_frames[int(self.frame_index)]
        elif self.state == "hurt_light":
            img = self.img_hurt_light
        elif self.state == "hurt_heavy":
            img = self.img_hurt_heavy
        elif self.state == "attack":
            # Use the attack list
            img = self.attack_frames[int(self.attack_index)]
        elif self.state == "dead":
            img = self.img_dead
        else:
            img = self.normal_frames

        
        # Use img instead of self.img_normal here:
        surface.blit(img, (self.rect.x + self.shake_x, self.rect.y + hover_y))


class DamageText:
    def __init__(self,x,y,text,color):
        self.x=x
        self.y=y
        self.text=text
        self.color=color
        self.timer=120  # Display for 120 frames (approx 2 seconds)
        self.opacity=255
    
    def update(self):
        # 2. SLOWER FLOAT: Changed from 2 to 0.5 for a smooth, slow rise
        self.y -= 0.8  
        self.timer -= 1
        
        # 3. SLOWER FADE: Opacity drops slower to match the longer timer
        # (255 / 120 frames is approx 2.1 per frame)
        if self.opacity > 2:
            self.opacity -= 2.1
    
    def draw(self,surface):
        if self.timer > 0:
            text_surf=pixel_font.render(self.text,True,self.color)
            text_surf.set_alpha(self.opacity)
            surface.blit(text_surf,(self.x,self.y))
        

# --- Data ---
warrior_skills = [
    {"name": "Slash", "damage": 40, "cost": 10},
    {"name": "Whirlwind", "damage": 60, "cost": 25}
]

mage_skills = [
    {"name": "Fireball", "damage": 80, "cost": 30},
    {"name": "Heal", "damage": -50, "cost": 20} # Negative damage = Heal
]

special_skills = [
    {"name": "Shadow Strike", "damage": 100, "cost": 40},
    {"name": "Invisibility", "damage": 0, "cost": 15} # No damage, just a buff
]

tank_skills = [
    {"name": "Shield Bash", "damage": 30, "cost": 5},
    {"name": "Fortify", "damage": 0, "cost": 20} # No damage, just a buff
]

party = [
    Knight(350,150),
    Mage(450,250),
    Special(350,350),
    Tank(450,450)
]
selected_hero = party[0]
enemy = EnemySprite("GHost", hp=1840, x=800,y=250,attk=10)
damage_popups = []

items = {
    "Potion":   {"effect": "heal", "value": 50, "count": 3, "color": GREEN},
    "Bomb":     {"effect": "damage", "value": 1000000, "count": 99, "color": RED}
}


# --- GUI Helpers --- ( FOR BOSS )
def boss_draw_bar(x, y, current, maximum, color, label, width=200):
    ratio = current / maximum
    # Background (The gray part)
    pygame.draw.rect(screen, GRAY, (x, y, width, 22)) 
    # Fill (The colored part)
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), 22)) 
    
    text = pixel_font.render(f"{label}", True, WHITE) # Draw only the label
    screen.blit(text, (x, y - 25))

def draw_bar(x, y, current, maximum, color, label, width=200):
    ratio = current / maximum
    # Background
    pygame.draw.rect(screen, GRAY, (x, y, width, 18)) 
    # Fill (Color)
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), 18)) 
    # Text
    bar_text = pixel_font.render(f"{label}: {current}/{maximum}", True, WHITE)
    screen.blit(bar_text, (x + 5, y - 4)) # Text starts 5px from the left edge

def draw_scanline():
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0,0,0,50), (0, y), (WIDTH, y), 1)

# --- Game State ---
battle_log = "Your turn! Choose a skill."
show_items = False
show_skills = False


# --- Main Loop ---
running=True
while running:
    # --- LAYER 1: BACKGROUND ---
    bg_y = (bg_y + scroll_speed) % HEIGHT
    screen.blit(bg_img, (0, bg_y))
    screen.blit(bg_img, (0, bg_y - HEIGHT))

    # --- LAYER 2: MODELS (Boss and Heroes) ---
    enemy.update()
    enemy.draw(screen)

    for hero in party:
        hero.update()
        if game_state == "PLANNING":
            if hero == selected_hero:
                pygame.draw.ellipse(screen, YELLOW, (hero.rect.x - 10, hero.rect.bottom - 10, 120, 20), 2)
            if hero.action_ready:
                pygame.draw.ellipse(screen, GREEN, (hero.rect.x - 5, hero.rect.bottom -5, 110, 15), 2)
        
        if game_state == "EXECUTING" and executor_index < len(party):
            if hero == party[executor_index]:
                pygame.draw.ellipse(screen, RED, (hero.rect.x - 10, hero.rect.bottom - 10, 120, 20), 2)
        hero.draw(screen)

    # --- LAYER 3: DAMAGE TEXT ---
    # --- LAYER 4: UI DASHBOARD & SKILLS ---
    start_x=10          # Move Dashboard horizontally  
    start_y=100         # Move Dashboard vertically
    box_height=80
    spacing=10
    skill_option_rects = []

    for i, hero in enumerate(party):
        current_y = start_y + i * (box_height + spacing)
        hero_rect = pygame.Rect(start_x, current_y, 200, box_height)
        hero.dashboard_rect = hero_rect  # Store for click detection

        bg_color = (50,50,50) if hero == selected_hero else (30,30,30)
        pygame.draw.rect(screen, bg_color, hero_rect)
        pygame.draw.rect(screen, WHITE, hero_rect, width=3)

        name_text = pixel_font.render(hero.name, True, WHITE)
        screen.blit(name_text, (start_x + 10, current_y + 5))
        draw_bar(start_x + 10, current_y + 30, hero.hp, hero.max_hp, GREEN, "HP", width=180)
        draw_bar(start_x + 10, current_y + 55, hero.mp, hero.max_mp, BLUE, "MP", width=180)
        
        if selected_hero == hero and show_skills:
            menu_x = hero_rect.right + 10
            menu_rect = pygame.Rect(menu_x, current_y, 200, box_height)
            pygame.draw.rect(screen, (20,20,20), menu_rect)
            pygame.draw.rect(screen, YELLOW, menu_rect, width=2)

            for s_idx, skill in enumerate(hero.skills):
                s_y = current_y + 10 + (s_idx * 30)
                # Create a rect for each skill to detect clicks
                s_rect = pygame.Rect(menu_x + 5, s_y, 190, 25)
                skill_option_rects.append((s_rect, skill)) # Store skill dict, not just name
                
                # Highlight if mouse is hovering
                if s_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (60, 60, 60), s_rect)

                skill_text = pixel_font.render(skill["name"], False, WHITE)
                screen.blit(skill_text, (s_rect.x + 5, s_rect.y + 2))
        

    # Item Button
    item_btn_rect = pygame.Rect(WIDTH - 160, HEIGHT - 70, 140, 50)
    pygame.draw.rect(screen, (100,50,0), item_btn_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, item_btn_rect, width=2, border_radius=10)
    btn_text = pixel_font.render("ITEMS", True, WHITE)
    screen.blit(btn_text, (item_btn_rect.x + 30, item_btn_rect.y + 10))

    # Attack Button
    attack_btn_rect = pygame.Rect(20, HEIGHT - 70, 200, 50)
    if game_state == "PLANNING":
        pygame.draw.rect(screen,RED,attack_btn_rect)
        pygame.draw.rect(screen, WHITE, attack_btn_rect, width=2)
        btn_text = pixel_font.render("ATTACK", False, WHITE)
        screen.blit(btn_text, (attack_btn_rect.x + 10, attack_btn_rect.y + 15))

    item_option_rects = [] # To store item button rects
    if show_items:
        menu_width = 400
        menu_rect = pygame.Rect(item_btn_rect.x - menu_width - 10, item_btn_rect.y, menu_width,50)
        pygame.draw.rect(screen, (40,40,40), menu_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, menu_rect, width=2, border_radius=10)

        # Draw specific items inside the menu
        for i, (name, data) in enumerate(items.items()):
            slot_rect = pygame.Rect(menu_rect.x + 10 + (i * 130), menu_rect.y + 5, 120, 40)
            item_option_rects.append((slot_rect, name))

            pygame.draw.rect(screen, data["color"], slot_rect, border_radius=5)
            item_text = pixel_font.render(f"{name}({data['count']})", True, WHITE)
            screen.blit(item_text, (slot_rect.x + 5, slot_rect.y + 5))
    
    # Calculate Time
    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, max_time_seconds - seconds_passed)
    # Convert to Minutes:Seconds format
    mins = time_left // 60
    secs = time_left % 60
    timer_string = f"Time: {mins:02d}:{secs:02d}"
    if time_left <=0 and current_turn != "game_over":
        current_turn = "game_over"
        battle_log = "Time's up! You have been defeated."

    
    # 3. Draw HUD
    pygame.draw.rect(screen,(0,0,0,150),(820,9,200,90),border_radius=10)
    boss_draw_bar(250, 40, enemy.hp, enemy.max_hp, RED, f"{enemy.name} HP", width=500)
    timer_text = pixel_font.render(timer_string, True, WHITE)
    turn_text = pixel_font.render(f"Turn: {turn_count}", True, WHITE)
    screen.blit(timer_text, (820, 20)) # Positioned at the top right
    screen.blit(turn_text, (820, 55))

    for popup in damage_popups[:]:  # [:] creates a copy so we can safely remove items
        popup.update()
        popup.draw(screen)
        if popup.timer <= 0:
            damage_popups.remove(popup)

    screen.blit(pixel_font.render(battle_log, True, WHITE), (300, 500))
    
    # 4. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "PLANNING":
            mouse_pos = pygame.mouse.get_pos()
            

            if attack_btn_rect.collidepoint(mouse_pos):
                game_state = "EXECUTING"
                execution_timer = 30
                executor_index = 0
                show_skills = False
                show_items = False
                continue 
        
            skill_used = False
            if show_skills:
                for rect, skill_data in skill_option_rects:
                    if rect.collidepoint(mouse_pos):
                        # Use the skill!
                        battle_log = selected_hero.use_skill(skill_data["name"], enemy, skill_data)
                        
                        if skill_data["damage"] > 0:
                            selected_hero.perform_attack()
                        skill_used = True
                        show_skills = False
                        
                        game_state = "PLANNING"
                        turn_wait_timer = 60
                        break
            if skill_used: continue
            for hero in party:
                if hero.dashboard_rect.collidepoint(mouse_pos) and hero.hp > 0:
                    selected_hero = hero
                    show_skills = True

            if item_btn_rect.collidepoint(mouse_pos):
                show_items = not show_items
                show_skills = False
                
                       
            # 3. Check for item button click
            if show_items:
                for rect, name in item_option_rects:
                    if rect.collidepoint(event.pos) and items[name]["count"]>0:
                        item_data = items[name]

                        if name == "Potion":
                            for hero in party:
                                hero.hp = min(hero.max_hp, hero.hp + item_data["value"])
                                damage_popups.append(DamageText(hero.rect.centerx, hero.rect.top, f"+{item_data['value']}", GREEN))
                            battle_log = f"Used {name}! Healed all party members."
                        
                        elif name == "Bomb":
                            enemy.take_damage(item_data["value"])
                            damage_popups.append(DamageText(enemy.rect.centerx, enemy.rect.top, f"-{item_data['value']}", RED))
                            battle_log = f"Used {name}! Dealt {item_data['value']} damage to {enemy.name}."

                        items[name]["count"] -= 1
                        show_items = False
                        current_turn = "waiting"
                        turn_wait_timer=60
                        
            if game_state == "PLANNING":
            # Check if the "EXECUTE ATTACK" button was clicked
            # Only start if at least one hero is ready to move
                if attack_btn_rect.collidepoint(mouse_pos):
                    if any(h.action_ready for h in party):
                        game_state = "EXECUTING"
                        executor_index = 0
                        execution_timer = 30 # Small delay before first hero moves
                        show_skills = False
                        show_items = False    
                    
                    

    
    # 5. Turn Management (New System)
    if game_state == "EXECUTING":
        execution_timer -= 1
    
        if execution_timer <= 0:
            # Cycle through all heroes from first to last
            if executor_index < len(party):
                current_hero = party[executor_index]
            
                if current_hero.hp > 0:
                    # Perform the attack
                    dmg = random.randint(current_hero.attk - 3, current_hero.attk + 3)
                    enemy.take_damage(dmg)
                    damage_popups.append(DamageText(enemy.rect.centerx, enemy.rect.top, f"-{dmg}", WHITE))
                    current_hero.perform_attack()
                    battle_log = f"{current_hero.name} deals damage" 
                    # Move to next hero after 1 second (60 frames)

                    executor_index += 1
                    execution_timer = 60 
                else:
                    # Skip dead heroes or heroes with no skill
                    executor_index += 1
                    execution_timer = 1
            else:
                # Everyone has finished! Now it's the Boss's turn
                game_state = "BOSS_TURN"
                execution_timer = 60
    
    elif game_state == "BOSS_TURN":
        if enemy.hp >0:
            if not enemy.is_animating_attack:
                enemy.state = "attack"
                enemy.is_animating_attack = True
                enemy.attack_index = 0
                enemy.attack_hold_timer = 0
            if hasattr(enemy, 'deal_damage_now') and enemy.deal_damage_now:
                # Boss attacks a random alive hero
                living_heroes = [hero for hero in party if hero.hp > 0]
                if living_heroes:
                    target_hero = random.choice(living_heroes)
                    dmg = random.randint(enemy.attk - 2, enemy.attk + 2)
                    target_hero.take_damage(dmg) # Just to trigger any visual effects
                    damage_popups.append(DamageText(target_hero.rect.centerx, target_hero.rect.top, f"-{dmg}", RED))  # Create damage popup
                    battle_log = f"{enemy.name} deals {dmg} damage to {target_hero.name}!"
                # Reset the flag and end turn
                enemy.deal_damage_now = False
                enemy.is_animating_attack = False
                game_state = "PLANNING_RESET"
                execution_timer = 90
        else:
            battle_log = f"{enemy.name} has been defeated! Victory!"
            game_state = "GAME_OVER"

    elif game_state == "PLANNING_RESET":
        execution_timer -=1
        if execution_timer <=0:
            for hero in party:
                hero.queued_skill = None
                hero.action_ready = False
            turn_count += 1
            game_state = "PLANNING"
            battle_log = "Your turn! Choose a skill."
            
    

    #draw_scanline() # Makes the screen look retro
    pygame.display.flip()
    clock.tick(60)
pygame.quit()



