import pygame
import sys
import random
import math

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Villageois sur carte isométrique personnalisée")

clock = pygame.time.Clock()

# Configuration de la carte isométrique (sera redéfinie après chargement)
MAP_ROWS = 0
MAP_COLS = 0

scale = 100
terrain_map = []  # Matrice contenant les types de terrain

# Décalage pour centrer la map
offset_x = WINDOW_WIDTH // 2
offset_y = 0

# Types de terrain et leurs fichiers d'images
TERRAIN_TYPES = {
    '.': None,  # Vide (pas de tuile)
    'G': 'herbe.png',  # Herbe
    'S': 'sable.png',  # Sable
    'W': 'eau.png',  # Eau
    'R': 'roche.png',  # Roche/Terre
    'T': 'arbre.png',  # Arbre
    'B': 'bloc.png',  # Bloc (ajouté comme exemple)
}


def load_map_from_file(filename):
    """Charge une carte depuis un fichier texte"""
    global MAP_ROWS, MAP_COLS, terrain_map

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Nettoyer les lignes et enlever les espaces/retours à la ligne
        lines = [line.rstrip() for line in lines if line.strip()]

        if not lines:
            print(f"Fichier {filename} vide, utilisation de la carte par défaut")
            create_default_map()
            return

        MAP_ROWS = len(lines)
        MAP_COLS = max(len(line) for line in lines)

        # Créer la matrice de terrain
        terrain_map = []
        for i, line in enumerate(lines):
            row = []
            for j in range(MAP_COLS):
                if j < len(line):
                    char = line[j]
                    if char in TERRAIN_TYPES:
                        row.append(char)
                    else:
                        row.append('.')  # Caractère inconnu = vide
                else:
                    row.append('.')  # Compléter avec du vide
            terrain_map.append(row)

        print(f"Carte chargée: {MAP_ROWS}x{MAP_COLS}")

    except FileNotFoundError:
        print(f"Fichier {filename} non trouvé, création d'une carte par défaut")
        create_default_map()
    except Exception as e:
        print(f"Erreur lors du chargement de {filename}: {e}")
        create_default_map()


def create_default_map():
    """Crée une carte par défaut si le fichier n'est pas trouvé"""
    global MAP_ROWS, MAP_COLS, terrain_map

    MAP_ROWS = 15
    MAP_COLS = 15
    terrain_map = []

    # Créer une petite île avec différents terrains
    for i in range(MAP_ROWS):
        row = []
        for j in range(MAP_COLS):
            # Distance du centre
            center_i, center_j = MAP_ROWS // 2, MAP_COLS // 2
            dist = abs(i - center_i) + abs(j - center_j)

            if dist > 6:
                row.append('.')  # Vide autour
            elif dist > 5:
                row.append('W')  # Eau
            elif dist > 4:
                row.append('S')  # Sable
            elif random.random() < 0.1:
                row.append('T')  # Quelques arbres
            else:
                row.append('G')  # Herbe principalement
        terrain_map.append(row)


def load_tile_sprite(terrain_type):
    """Charge l'image PNG pour un type de terrain donné"""
    if terrain_type == '.' or terrain_type not in TERRAIN_TYPES:
        return None

    filename = TERRAIN_TYPES[terrain_type]
    if filename is None:
        return None

    try:
        # Charger l'image
        image = pygame.image.load(filename).convert_alpha()

        # Redimensionner l'image pour qu'elle s'adapte aux tuiles isométriques
        TILE_WIDTH = int(image.get_width())
        TILE_HEIGHT = int(image.get_height() // 2)
        target_height = scale // 2
        scale_ratio = target_height / image.get_height()
        target_width = int(TILE_WIDTH * scale_ratio)

        # Traitement spécial pour les arbres - 4 fois plus grands
        if terrain_type == 'T':
            scale_ratio *= 4  # Multiplier par 4 pour les arbres
            target_width = int(TILE_WIDTH * scale_ratio)
            target_height = int(image.get_height() * scale_ratio)

        # Conserver le ratio si l'image est carrée (comme beaucoup de tuiles isométriques)
        original_width, original_height = image.get_size()
        if original_width == original_height and terrain_type != 'T':
            # Image carrée -> redimensionner pour l'isométrie (sauf arbres)
            scaled_image = pygame.transform.scale(image, (target_width, target_height))
        else:
            # Image déjà aux bonnes proportions ou arbre
            scaled_image = pygame.transform.scale(image, (target_width, target_height))

        return scaled_image

    except pygame.error as e:
        print(f"Impossible de charger {filename}: {e}")
        return create_fallback_tile(terrain_type)
    except FileNotFoundError:
        print(f"Fichier {filename} non trouvé, utilisation d'une tuile de remplacement")
        return create_fallback_tile(terrain_type)


def create_fallback_tile(terrain_type):
    """Crée une tuile de remplacement si l'image PNG n'est pas trouvée"""
    tile_width, tile_height = 64, 32

    # Taille spéciale pour les arbres de remplacement
    if terrain_type == 'T':
        tile_width *= 4
        tile_height *= 4

    surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)

    # Couleurs de remplacement
    fallback_colors = {
        'G': (34, 139, 34),  # Herbe (vert)
        'S': (194, 178, 128),  # Sable (beige)
        'W': (65, 105, 225),  # Eau (bleu)
        'R': (139, 69, 19),  # Roche (marron)
        'T': (34, 100, 34),  # Arbre (vert foncé)
        'B': (100, 100, 100),  # Bloc (gris)
    }

    color = fallback_colors.get(terrain_type, (100, 100, 100))

    # Dessiner un losange comme remplacement
    points = [
        (tile_width // 2, 0),
        (tile_width, tile_height // 2),
        (tile_width // 2, tile_height),
        (0, tile_height // 2)
    ]

    pygame.draw.polygon(surface, color, points)
    border_color = tuple(max(0, c - 30) for c in color)
    pygame.draw.polygon(surface, border_color, points, 2)

    # Ajouter une indication que c'est un remplacement
    font_size = 16 if terrain_type != 'T' else 32
    font = pygame.font.SysFont(None, font_size)
    text = font.render(terrain_type, True, (255, 255, 255))
    text_rect = text.get_rect(center=(tile_width // 2, tile_height // 2))
    surface.blit(text, text_rect)

    return surface


def create_dummy_villager():
    """Crée un sprite temporaire de villageois"""
    surface = pygame.Surface((20, 30), pygame.SRCALPHA)
    # Corps
    pygame.draw.circle(surface, (255, 220, 177), (10, 8), 6)  # Tête
    pygame.draw.rect(surface, (139, 69, 19), (7, 12, 6, 12))  # Corps
    pygame.draw.rect(surface, (0, 0, 139), (5, 18, 10, 8))  # Jambes
    return surface


def create_dummy_carrot():
    """Crée un sprite temporaire de carotte"""
    surface = pygame.Surface((16, 20), pygame.SRCALPHA)
    # Carotte (triangle orange)
    pygame.draw.polygon(surface, (255, 140, 0), [(8, 18), (4, 8), (12, 8)])
    # Feuilles vertes
    pygame.draw.polygon(surface, (0, 150, 0), [(6, 8), (8, 2), (10, 8)])
    return surface


# Charger la carte depuis un fichier
load_map_from_file("map.txt")

# Créer les sprites de tuiles pour chaque type de terrain
tile_sprites = {}
for terrain_type in TERRAIN_TYPES:
    if terrain_type != '.':
        sprite = load_tile_sprite(terrain_type)
        if sprite:
            tile_sprites[terrain_type] = sprite

# Dimensions des tuiles
target_width = scale * 0.9
target_height = scale // 2.2

# Chargement du sprite villageois
try:
    villager_img = pygame.image.load("villagois.png").convert_alpha()
    w, h = villager_img.get_size()
    v_target_height = scale * 0.6
    v_scale_ratio = v_target_height / h
    v_target_width = int(w * v_scale_ratio)
    villager_sprite = pygame.transform.scale(villager_img, (v_target_width, v_target_height))
    villager_sprite_flipped = pygame.transform.flip(villager_sprite, True, False)
except:
    print("Image villagois.png non trouvée, utilisation d'un sprite temporaire")
    villager_sprite = create_dummy_villager()
    villager_sprite_flipped = pygame.transform.flip(villager_sprite, True, False)

# Chargement du sprite coeur pour les particules
try:
    heart_img = pygame.image.load("coeur.png").convert_alpha()
    heart_sprite = pygame.transform.scale(heart_img, (16, 16))  # Petite taille pour les particules
except:
    print("Image coeur.png non trouvée, utilisation d'un sprite temporaire")
    # Créer un coeur temporaire
    heart_sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.polygon(heart_sprite, (255, 20, 147),
                       [(8, 4), (12, 0), (16, 4), (16, 8), (8, 16), (0, 8), (0, 4), (4, 0)])

# Chargement du sprite carotte
try:
    carrot_img = pygame.image.load("carrot.png").convert_alpha()
    w, h = carrot_img.get_size()
    c_target_height = scale * 0.3
    c_scale_ratio = c_target_height / h
    c_target_width = int(w * c_scale_ratio)
    carrot_sprite = pygame.transform.scale(carrot_img, (c_target_width, c_target_height))
except:
    print("Image carrot.png non trouvée, utilisation d'un sprite temporaire")
    carrot_sprite = create_dummy_carrot()

th = target_height // 2
tw = target_width // 2


def iso_to_screen(i, j):
    """Convertit les coordonnées isométriques en coordonnées écran"""
    screen_x = (i - j) * (tw // 2) + offset_x
    screen_y = (i + j) * (th // 2) + offset_y
    return screen_x, screen_y


def iso_to_screen_walkable(i, j):
    """Convertit les coordonnées isométriques en coordonnées écran pour le dessus des blocs"""
    screen_x = (i - j) * (tw // 2) + offset_x - (target_width * 0.2)
    # Ajustement pour placer les villageois sur le dessus des blocs
    # Réduire screen_y pour compenser la hauteur des côtés des blocs
    screen_y = (i + j) * (th // 2) + offset_y - (target_height * 0.6)  # Ajustement vertical
    return screen_x, screen_y


def screen_to_iso(screen_x, screen_y):
    """Convertit les coordonnées écran en coordonnées isométriques"""
    x = screen_x - offset_x
    y = screen_y - offset_y
    i = (x / (tw // 2) + y / (th // 2)) / 2
    j = (y / (th // 2) - x / (tw // 2)) / 2
    return int(round(i)), int(round(j))


def is_valid_tile(i, j):
    """Vérifie si les coordonnées de tuile sont valides et marchables"""
    if 0 <= i < MAP_ROWS and 0 <= j < MAP_COLS:
        terrain_type = terrain_map[i][j]
        # Les villageois peuvent marcher sur l'herbe, le sable, les rochers et les blocs
        # Les arbres ('T') et le vide ('.') ne sont pas traversables
        return terrain_type in ['G', 'S', 'R', 'B']
    return False


def draw_iso_map():
    """Dessine la carte isométrique (sans les arbres)"""
    for i in range(MAP_ROWS):
        for j in range(MAP_COLS):
            terrain_type = terrain_map[i][j]
            if terrain_type != '.' and terrain_type in tile_sprites:  # and terrain_type != 'T'
                if terrain_type == 'T':
                    screen_x, screen_y = iso_to_screen(i, j)
                    screen.blit(tile_sprites["G"], (screen_x, screen_y))
                else:
                    screen_x, screen_y = iso_to_screen(i, j)
                    screen.blit(tile_sprites[terrain_type], (screen_x, screen_y))


def draw_trees():
    """Dessine les arbres en dernier pour qu'ils apparaissent au-dessus de tout"""
    for i in range(MAP_ROWS):
        for j in range(MAP_COLS):
            terrain_type = terrain_map[i][j]
            if terrain_type == 'T' and terrain_type in tile_sprites:
                screen_x, screen_y = iso_to_screen(i, j)
                sprite = tile_sprites[terrain_type]
                # Centrer l'arbre sur la tuile et le déplacer 2 blocs plus haut
                adjusted_x = screen_x - (sprite.get_width() - target_width) // 1.5
                adjusted_y = screen_y - (sprite.get_height() - target_height) + target_height // 2 - (target_height)
                screen.blit(sprite, (adjusted_x, adjusted_y))


class Carrot:
    def __init__(self):
        self.sprite = carrot_sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()

        # Trouver une position valide pour la carotte
        attempts = 0
        while attempts < 100:
            self.tile_i = random.randint(0, MAP_ROWS - 1)
            self.tile_j = random.randint(0, MAP_COLS - 1)

            if is_valid_tile(self.tile_i, self.tile_j):
                screen_x, screen_y = iso_to_screen_walkable(self.tile_i, self.tile_j)
                self.x = screen_x + (target_width - self.width) // 2
                self.y = screen_y + target_height - self.height
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                break
            attempts += 1

        # Animation de la carotte
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.bob_amplitude = 3

    def update(self):
        """Met à jour l'animation de la carotte"""
        self.bob_offset += self.bob_speed

    def draw(self, surface):
        """Dessine la carotte avec un effet de flottement"""
        bob_y = self.y + math.sin(self.bob_offset) * self.bob_amplitude
        surface.blit(self.sprite, (self.x, bob_y))

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-0.2, 0.2)
        self.vel_y = random.uniform(-0.3, -0.1)
        self.life = 360  # Durée de vie en frames
        self.max_life = 360
        self.sprite = heart_sprite

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1  # Gravité légère
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        temp_surface = self.sprite.copy()
        temp_surface.set_alpha(alpha)
        surface.blit(temp_surface, (self.x, self.y))

    def is_alive(self):
        return self.life > 0


class Villageois:
    def __init__(self, all_villagers, is_baby=False, spawn_pos=None):
        self.image_original = villager_sprite
        self.image_flipped = villager_sprite_flipped
        self.current_image = self.image_original
        self.facing_right = False

        self.width = self.current_image.get_width()
        self.height = self.current_image.get_height()

        # Nouvelles propriétés pour l'âge et la reproduction
        self.is_baby = is_baby
        self.age_carrots = 0  # Carottes nécessaires pour grandir (si bébé)
        self.reproduction_timer = 0  # Timer pour éviter la reproduction trop fréquente
        self.seeking_partner = False
        self.target_partner = None
        self.reproduction_state = "none"  # "none", "seeking", "reproducing"

        # Ajuster la taille selon l'âge
        if self.is_baby:
            # Réduire la taille pour les bébés
            baby_scale = 0.6
            baby_width = int(self.image_original.get_width() * baby_scale)
            baby_height = int(self.image_original.get_height() * baby_scale)
            self.image_original = pygame.transform.scale(self.image_original, (baby_width, baby_height))
            self.image_flipped = pygame.transform.scale(self.image_flipped, (baby_width, baby_height))
            self.current_image = self.image_original

        self.width = self.current_image.get_width()
        self.height = self.current_image.get_height()

        # Position initiale
        if spawn_pos:
            # Utiliser la position fournie (pour les bébés nés de parents)
            self.tile_i, self.tile_j = spawn_pos
            screen_x, screen_y = iso_to_screen_walkable(self.tile_i, self.tile_j)
            self.x = screen_x + (target_width - self.width) // 2
            self.y = screen_y + target_height - self.height
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        else:
            # Position initiale sur une tuile valide (pour les villageois créés normalement)
            attempts = 0
            while attempts < 100:  # Éviter une boucle infinie
                self.tile_i = random.randint(0, MAP_ROWS - 1)
                self.tile_j = random.randint(0, MAP_COLS - 1)

                if is_valid_tile(self.tile_i, self.tile_j):
                    # Utiliser la fonction walkable pour positionner sur le dessus des blocs
                    screen_x, screen_y = iso_to_screen_walkable(self.tile_i, self.tile_j)
                    self.x = screen_x + (target_width - self.width) // 2
                    self.y = screen_y + target_height - self.height
                    self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

                    # Vérifier qu'il n'y a pas de collision avec d'autres villageois
                    if not any(self.rect.colliderect(v.rect) for v in all_villagers):
                        break

                attempts += 1

            if attempts >= 100:
                print("Impossible de placer le villageois, pas assez de tuiles valides")
                # Position par défaut au centre
                self.tile_i = MAP_ROWS // 2
                self.tile_j = MAP_COLS // 2
                screen_x, screen_y = iso_to_screen_walkable(self.tile_i, self.tile_j)
                self.x = screen_x + (target_width - self.width) // 2
                self.y = screen_y + target_height - self.height
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Propriétés de mouvement et comportement (initialisées pour tous les villageois)
        self.angle = 0
        self.angle_dir = 1
        self.speed = 1

        self.target_tile_i = self.tile_i
        self.target_tile_j = self.tile_j
        self.moving = False

        self.state = "pause"
        self.timer = random.randint(0, 60)

        # Inventaire du villageois
        self.carrots_collected = 0
        self.target_carrot = None  # Carotte ciblée
        self.seeking_carrot = False

    def get_adjacent_tiles(self):
        """Retourne les tuiles adjacentes valides"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        valid_tiles = []

        for di, dj in directions:
            new_i = self.tile_i + di
            new_j = self.tile_j + dj
            if is_valid_tile(new_i, new_j):
                valid_tiles.append((new_i, new_j))

        return valid_tiles

    def find_nearest_carrot(self, carrots):
        """Trouve la carotte la plus proche"""
        if not carrots:
            return None

        min_distance = float('inf')
        nearest_carrot = None

        for carrot in carrots:
            distance = abs(self.tile_i - carrot.tile_i) + abs(self.tile_j - carrot.tile_j)
            if distance < min_distance:
                min_distance = distance
                nearest_carrot = carrot

        return nearest_carrot

    def path_to_carrot(self, target_carrot):
        """Trouve le prochain mouvement vers la carotte ciblée"""
        if not target_carrot:
            return None

        # Calculer la direction générale vers la carotte
        di = target_carrot.tile_i - self.tile_i
        dj = target_carrot.tile_j - self.tile_j

        # Normaliser la direction
        if di > 0:
            di = 1
        elif di < 0:
            di = -1

        if dj > 0:
            dj = 1
        elif dj < 0:
            dj = -1

        # Essayer de se déplacer vers la carotte
        next_i = self.tile_i + di
        next_j = self.tile_j + dj

        if is_valid_tile(next_i, next_j):
            return (next_i, next_j)

        # Si le mouvement direct n'est pas possible, essayer les alternatives
        alternatives = []
        if di != 0:
            alternatives.append((self.tile_i + di, self.tile_j))
        if dj != 0:
            alternatives.append((self.tile_i, self.tile_j + dj))

        for alt_i, alt_j in alternatives:
            if is_valid_tile(alt_i, alt_j):
                return (alt_i, alt_j)

        return None

    def path_to_partner(self, target_partner):
        """Trouve le prochain mouvement vers le partenaire ciblé"""
        if not target_partner:
            return None

        # Calculer la direction générale vers le partenaire
        di = target_partner.tile_i - self.tile_i
        dj = target_partner.tile_j - self.tile_j

        # Normaliser la direction
        if di > 0:
            di = 1
        elif di < 0:
            di = -1

        if dj > 0:
            dj = 1
        elif dj < 0:
            dj = -1

        # Essayer de se déplacer vers le partenaire
        next_i = self.tile_i + di
        next_j = self.tile_j + dj

        if is_valid_tile(next_i, next_j):
            return (next_i, next_j)

        # Si le mouvement direct n'est pas possible, essayer les alternatives
        alternatives = []
        if di != 0:
            alternatives.append((self.tile_i + di, self.tile_j))
        if dj != 0:
            alternatives.append((self.tile_i, self.tile_j + dj))

        for alt_i, alt_j in alternatives:
            if is_valid_tile(alt_i, alt_j):
                return (alt_i, alt_j)

        return None

    def move_to_tile(self, target_i, target_j, others):
        """Commence le mouvement vers une tuile cible"""
        # Utiliser la fonction walkable pour calculer la position cible
        target_screen_x, target_screen_y = iso_to_screen_walkable(target_i, target_j)
        target_x = target_screen_x + (target_width - self.width) // 2
        target_y = target_screen_y + target_height - self.height
        target_rect = pygame.Rect(target_x, target_y, self.width, self.height)

        # Vérifier collision avec autres villageois UNIQUEMENT sur la tuile de destination
        for other in others:
            if (other is not self and
                    other.tile_i == target_i and other.tile_j == target_j and
                    not other.moving):  # Ignorer les villageois en mouvement
                return False

        self.target_tile_i = target_i
        self.target_tile_j = target_j
        self.moving = True

        # Déterminer la direction de regard
        if target_j > self.tile_j or target_i < self.tile_i:
            if not self.facing_right:
                self.facing_right = True
                self.current_image = self.image_original
        elif target_j < self.tile_j or target_i > self.tile_i:
            if self.facing_right:
                self.facing_right = False
                self.current_image = self.image_flipped

        return True

    def grow_up(self):
        """Transforme un bébé en adulte"""
        if self.is_baby:
            self.is_baby = False
            # Restaurer la taille adulte
            self.image_original = villager_sprite
            self.image_flipped = villager_sprite_flipped
            self.current_image = self.image_original if self.facing_right else self.image_flipped
            self.width = self.current_image.get_width()
            self.height = self.current_image.get_height()
            # Réajuster la position
            screen_x, screen_y = iso_to_screen_walkable(self.tile_i, self.tile_j)
            self.x = screen_x + (target_width - self.width) // 2
            self.y = screen_y + target_height - self.height
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            print(f"Un bébé villageois est devenu adulte !")

    def can_reproduce(self):
        """Vérifie si le villageois peut se reproduire"""
        return (not self.is_baby and
                self.carrots_collected >= 5 and
                self.reproduction_timer <= 0 and
                self.reproduction_state == "none")

    def find_reproduction_partner(self, others):
        """Trouve un partenaire pour la reproduction"""
        available_partners = []
        for other in others:
            if (other is not self and
                    other.can_reproduce() and
                    other.reproduction_state == "none"):
                available_partners.append(other)

        if not available_partners:
            return None

        # Retourner le partenaire le plus proche
        min_distance = float('inf')
        nearest_partner = None

        for partner in available_partners:
            distance = abs(self.tile_i - partner.tile_i) + abs(self.tile_j - partner.tile_j)
            if distance < min_distance:
                min_distance = distance
                nearest_partner = partner

        return nearest_partner

    def try_reproduce(self, other_villager, all_villagers, particules):
        """Tente de se reproduire avec un autre villageois"""
        # Distance permissive pour la reproduction (distance de Manhattan <= 2)
        distance = abs(self.tile_i - other_villager.tile_i) + abs(self.tile_j - other_villager.tile_j)

        if distance <= 2:  # Distance permissive pour reproduction
            # Créer des particules de coeur
            center_x = (self.x + other_villager.x) // 2 + self.width // 2
            center_y = (self.y + other_villager.y) // 2 + self.height // 2

            for _ in range(15):  # 15 particules de coeur
                particules.append(Particle(center_x, center_y))

            # Consommer les carottes
            self.carrots_collected -= 5
            other_villager.carrots_collected -= 5

            # Définir un timer de reproduction
            self.reproduction_timer = 300  # 5 secondes
            other_villager.reproduction_timer = 300

            # Réinitialiser les états
            self.reproduction_state = "none"
            other_villager.reproduction_state = "none"
            self.seeking_partner = False
            other_villager.seeking_partner = False
            self.target_partner = None
            other_villager.target_partner = None

            # Nettoyer les compteurs de blocage
            if hasattr(self, 'reproduction_stuck_counter'):
                delattr(self, 'reproduction_stuck_counter')
            if hasattr(other_villager, 'reproduction_stuck_counter'):
                delattr(other_villager, 'reproduction_stuck_counter')

            # Créer un bébé à la position de l'un des parents (choix aléatoire)
            parent_pos = random.choice([(self.tile_i, self.tile_j), (other_villager.tile_i, other_villager.tile_j)])
            baby = Villageois(all_villagers, is_baby=True, spawn_pos=parent_pos)
            all_villagers.append(baby)

            print(f"Un bébé villageois est né ! Population: {len(all_villagers)}")
            return True
        else:
            # Distance trop grande, ne pas abandonner mais continuer à se rapprocher
            return False

    def execute_movement_action(self, target_tile, others, action_name):
        """Exécute une action de mouvement avec 30% de chance de mouvement aléatoire"""
        # 10% de chance de faire un mouvement aléatoire
        if random.random() < 0.1:
            adjacent_tiles = self.get_adjacent_tiles()
            if adjacent_tiles:
                random_tile = random.choice(adjacent_tiles)
                if self.move_to_tile(random_tile[0], random_tile[1], others):
                    self.state = "move"
                    self.timer = random.randint(20, 40)
                    return True

        # Sinon, exécuter l'action prévue
        if target_tile:
            target_i, target_j = target_tile
            if self.move_to_tile(target_i, target_j, others):
                self.state = "move"
                self.timer = random.randint(30, 60)
                return True

        return False

    def update(self, others, carrots, particles):
        if self.reproduction_timer > 0:
            self.reproduction_timer -= 1

        # Vérifier si on est sur une carotte
        for carrot in carrots[:]:  # Copie de la liste pour éviter les problèmes de modification
            if self.tile_i == carrot.tile_i and self.tile_j == carrot.tile_j:
                carrots.remove(carrot)
                self.carrots_collected += 1
                self.target_carrot = None
                self.seeking_carrot = False

                # Si c'est un bébé, vérifier s'il peut grandir
                if self.is_baby:
                    self.age_carrots += 1
                    if self.age_carrots >= 3:
                        self.grow_up()
                print(
                    f"{'Bébé' if self.is_baby else 'Villageois'} a collecté une carotte ! Total: {self.carrots_collected}")

        # Gestion du mouvement
        if self.moving:
            # Utiliser la fonction walkable pour calculer la position cible
            target_screen_x, target_screen_y = iso_to_screen_walkable(self.target_tile_i, self.target_tile_j)
            target_x = target_screen_x + (target_width - self.width) // 2
            target_y = target_screen_y + (target_height - self.height)

            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > self.speed:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.x = target_x
                self.y = target_y
                self.tile_i = self.target_tile_i
                self.tile_j = self.target_tile_j
                self.moving = False
                self.state = "pause"
                self.timer = random.randint(15, 60)

                # Vérifier si on a atteint le partenaire pour reproduction
                if (self.reproduction_state == "seeking" and
                        self.target_partner and
                        self.target_partner in others):

                    if self.try_reproduce(self.target_partner, others, particles):
                        pass  # Reproduction réussie
                    # Si la reproduction échoue, on continuera à essayer au prochain cycle

                if hasattr(self, 'stuck_counter'):
                    self.stuck_counter = 0

            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

            # Animation de balancement
            self.angle += self.angle_dir * 2
            if abs(self.angle) > 8:
                self.angle_dir *= -1
        else:
            # Gestion des comportements quand le villageois ne bouge pas
            self.timer -= 1

            if self.timer <= 0:
                if self.state == "pause":
                    # PRIORITÉ 1: REPRODUCTION - Chercher un partenaire et se diriger vers lui
                    if self.can_reproduce() and self.reproduction_state == "none":
                        partner = self.find_reproduction_partner(others)
                        if partner:
                            # Marquer les deux villageois comme cherchant à se reproduire
                            self.target_partner = partner
                            self.seeking_partner = True
                            self.reproduction_state = "seeking"
                            partner.target_partner = self
                            partner.seeking_partner = True
                            partner.reproduction_state = "seeking"

                            print(f"Villageois a trouvé un partenaire et se dirige vers lui pour reproduction")

                            # Se diriger vers le partenaire immédiatement
                            next_tile = self.path_to_partner(partner)
                            if self.execute_movement_action(next_tile, others, "seek_partner"):
                                pass  # Mouvement réussi
                            else:
                                self.timer = random.randint(10, 20)

                    # Continuer à chercher le partenaire si on est en mode reproduction
                    elif self.reproduction_state == "seeking" and self.target_partner:
                        partner = self.target_partner

                        # Vérifier si le partenaire est toujours disponible
                        if partner not in others or not partner.can_reproduce() or partner.reproduction_state != "seeking":
                            # Le partenaire n'est plus disponible, annuler
                            self.reproduction_state = "none"
                            self.seeking_partner = False
                            self.target_partner = None
                            print("Partenaire non disponible, annulation de la reproduction")
                            self.timer = random.randint(10, 30)
                        else:
                            distance = abs(self.tile_i - partner.tile_i) + abs(self.tile_j - partner.tile_j)

                            if distance <= 2:  # Assez proche pour se reproduire
                                if self.try_reproduce(partner, others, particles):
                                    pass  # Reproduction réussie, arrêter ici
                                else:
                                    # Se rapprocher encore
                                    next_tile = self.path_to_partner(partner)
                                    if not self.execute_movement_action(next_tile, others, "approach_partner"):
                                        self.timer = random.randint(5, 15)
                            else:
                                # Se diriger vers le partenaire
                                next_tile = self.path_to_partner(partner)
                                if not self.execute_movement_action(next_tile, others, "approach_partner"):
                                    # Mouvement bloqué, essayer des alternatives
                                    if not hasattr(self, 'reproduction_stuck_counter'):
                                        self.reproduction_stuck_counter = 0
                                    self.reproduction_stuck_counter += 1

                                    if self.reproduction_stuck_counter > 10:
                                        # Annuler la reproduction si trop bloqué
                                        self.reproduction_state = "none"
                                        self.seeking_partner = False
                                        partner.reproduction_state = "none"
                                        partner.seeking_partner = False
                                        self.target_partner = None
                                        partner.target_partner = None
                                        print("Reproduction annulée - trop bloqué")
                                        self.timer = random.randint(30, 60)
                                    else:
                                        self.timer = random.randint(10, 20)

                    # PRIORITÉ 2: CHERCHER DE LA NOURRITURE (seulement si pas de reproduction)
                    elif self.reproduction_state == "none":
                        # Chercher une carotte si on n'en cherche pas déjà
                        if not self.seeking_carrot and carrots:
                            self.target_carrot = self.find_nearest_carrot(carrots)
                            if self.target_carrot:
                                self.seeking_carrot = True
                                print(f"Villageois a trouvé une carotte et se dirige vers elle")

                        # Se diriger vers la carotte
                        if self.seeking_carrot and self.target_carrot:
                            if self.target_carrot not in carrots:
                                # La carotte n'existe plus
                                self.target_carrot = None
                                self.seeking_carrot = False
                                self.timer = random.randint(10, 30)
                            else:
                                next_tile = self.path_to_carrot(self.target_carrot)
                                if not self.execute_movement_action(next_tile, others, "seek_carrot"):
                                    # Mouvement vers carotte bloqué
                                    if not hasattr(self, 'carrot_stuck_counter'):
                                        self.carrot_stuck_counter = 0
                                    self.carrot_stuck_counter += 1

                                    if self.carrot_stuck_counter > 5:
                                        # Changer de cible
                                        self.target_carrot = None
                                        self.seeking_carrot = False
                                        self.carrot_stuck_counter = 0
                                        self.timer = random.randint(10, 30)
                                    else:
                                        self.timer = random.randint(5, 15)
                        else:
                            # PRIORITÉ 3: MOUVEMENT ALÉATOIRE
                            # Si aucune action spécifique, faire un mouvement aléatoire
                            adjacent_tiles = self.get_adjacent_tiles()
                            if adjacent_tiles:
                                target_i, target_j = random.choice(adjacent_tiles)
                                if self.move_to_tile(target_i, target_j, others):
                                    self.state = "move"
                                    self.timer = random.randint(30, 90)
                                else:
                                    self.timer = random.randint(15, 30)
                            else:
                                self.timer = random.randint(30, 60)

                if self.state == "pause":
                    self.angle = 0

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.current_image, self.angle)
        rect = rotated.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated, rect)


# Création des villageois
nb_villagois = 3
villageois_list = []
for _ in range(nb_villagois):
    v = Villageois(villageois_list, is_baby=False)
    villageois_list.append(v)

# Création des carottes
carrots_list = []
carrot_spawn_timer = 0
MAX_CARROTS = 5
CARROT_SPAWN_INTERVAL = 180  # Spawn une carotte toutes les 3 secondes (180 frames à 60 FPS)

# Création des particules
particles_list = []

# Instructions
font = pygame.font.SysFont(None, 20)
small_font = pygame.font.SysFont(None, 18)
instructions = [
    "Espace: Ajouter un villageois",
    "R: Réinitialiser",
    "C: Ajouter une carotte"
]

# Boucle principale
running = True
while running:
    screen.fill((40, 60, 80))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                v = Villageois(villageois_list)
                villageois_list.append(v)
            elif event.key == pygame.K_r:
                villageois_list = []
                carrots_list = []
                for _ in range(nb_villagois):
                    v = Villageois(villageois_list)
                    villageois_list.append(v)
            elif event.key == pygame.K_c:
                if len(carrots_list) < MAX_CARROTS:
                    carrots_list.append(Carrot())

    # Spawn automatique des carottes
    carrot_spawn_timer += 1
    if carrot_spawn_timer >= CARROT_SPAWN_INTERVAL and len(carrots_list) < MAX_CARROTS:
        carrots_list.append(Carrot())
        carrot_spawn_timer = 0

    # Dessiner la carte (terrains uniquement, sans les arbres)
    draw_iso_map()

    # Mettre à jour et dessiner les carottes
    for carrot in carrots_list:
        carrot.update()
        carrot.draw(screen)

    # Mettre à jour les villageois
    for v in villageois_list:
        v.update(villageois_list, carrots_list, particles_list)

        # Mettre à jour les particules
        particles_list = [p for p in particles_list if p.is_alive()]
        for particle in particles_list:
            particle.update()

    # Trier les villageois par profondeur (i + j) - les plus petites valeurs en premier
    sorted_villagers = sorted(villageois_list, key=lambda v: v.tile_i + v.tile_j)

    # Dessiner les villageois dans l'ordre de profondeur
    for v in sorted_villagers:
        v.draw(screen)

    # Dessiner les particules
    for particle in particles_list:
        particle.draw(screen)

    # Dessiner les arbres en dernier pour qu'ils apparaissent au-dessus des villageois
    draw_trees()

    # Afficher les instructions
    for i, text in enumerate(instructions):
        if i < 2:
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        else:
            text_surface = small_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))

        # Afficher les infos
        adult_count = sum(1 for v in villageois_list if not v.is_baby)
        baby_count = sum(1 for v in villageois_list if v.is_baby)

        count_text = f"Adultes: {adult_count} | Bébés: {baby_count}"
        count_surface = font.render(count_text, True, (255, 255, 255))
        screen.blit(count_surface, (WINDOW_WIDTH - count_surface.get_width() - 10, 10))

        map_info = f"Carte: {MAP_ROWS}x{MAP_COLS}"
        map_surface = small_font.render(map_info, True, (255, 255, 255))
        screen.blit(map_surface, (WINDOW_WIDTH - map_surface.get_width() - 10, 35))

        # Afficher les infos des carottes
        carrot_info = f"Carottes: {len(carrots_list)}/{MAX_CARROTS}"
        carrot_surface = small_font.render(carrot_info, True, (255, 255, 255))
        screen.blit(carrot_surface, (WINDOW_WIDTH - carrot_surface.get_width() - 10, 55))

        # Afficher le total de carottes collectées
        total_collected = sum(v.carrots_collected for v in villageois_list)
        collected_info = f"Collectées: {total_collected}"
        collected_surface = small_font.render(collected_info, True, (255, 255, 255))
        screen.blit(collected_surface, (WINDOW_WIDTH - collected_surface.get_width() - 10, 75))

        # Afficher les villageois prêts à se reproduire
        ready_to_reproduce = sum(1 for v in villageois_list if v.can_reproduce())
        reproduce_info = f"Prêts reproduction: {ready_to_reproduce}"
        reproduce_surface = small_font.render(reproduce_info, True, (255, 255, 255))
        screen.blit(reproduce_surface, (WINDOW_WIDTH - reproduce_surface.get_width() - 10, 95))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()



