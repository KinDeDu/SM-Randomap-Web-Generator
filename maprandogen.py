import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import random
import json
import argparse
import os
import hashlib
import urllib.request

parser = argparse.ArgumentParser(
    description='Automatically generate randomized Super Metroid ROMs.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    usage='%(prog)s [-h] [-l] | [-t TOKEN [-b BROWSER]] | [-i INPUT] [-p PRESET] [-o OUTPUT] [-g GENERATE] [-r] [-s SPRITE] [-c COLOR] [-b BROWSER]'
)
parser.add_argument('-p', '--preset', help='JSON preset file, preset name, or comma-separated list for multiple seeds')
parser.add_argument('-i', '--input', help='Original Super Metroid ROM file')
parser.add_argument('-o', '--output', help='Output directory for generated ROM (default: current directory)')
parser.add_argument('-g', '--generate', type=int, default=1, help='Number of seeds to generate (default: 1)')
parser.add_argument('-r', '--random', action='store_true', help='Randomize Samus sprite and E-Tank color for each seed')
parser.add_argument('-s', '--sprite', help='Specify Samus sprite (use a valid sprite name)')
parser.add_argument('-c', '--color', help='Specify E-Tank color (use a valid hex code)')
parser.add_argument('-b', '--browser', choices=['chrome', 'firefox'], default='chrome', help='Browser to use (default: chrome)')
parser.add_argument('-t', '--token', help='Seed ID or URL to unlock spoiler map')
parser.add_argument('-l', '--list', action='store_true', help='List all available Samus sprites and E-Tank colors')
args = parser.parse_args()

def get_random_user_agent():
    try:
        url = "https://jnrbsn.github.io/user-agents/user-agents.json"
        with urllib.request.urlopen(url, timeout=5) as response:
            user_agents = json.loads(response.read().decode())
            return random.choice(user_agents)
    except Exception as e:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

def get_browser_driver(browser_type, download_path=None):
    user_agent = get_random_user_agent()
    if browser_type == 'firefox':
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.set_preference("general.useragent.override", user_agent)
        if download_path:
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_path)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-snes-rom")
        return webdriver.Firefox(options=options)
    else:
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-agent={user_agent}")
        if download_path:
            prefs = {"download.default_directory": download_path}
            options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=options)

samus_sprites = [
    "samus_vanilla", "samus_dread", "dread_samus", "santamus", "metroid_1_suit",
    "samus_fusion_typea_green", "dark_samus", "dark_samus_2", "dark_samus_reanimated",
    "samus_zero-mission", "samus_returns", "samus_maid", "hack_opposition", "ped_suit",
    "ascent", "ancient_chozo", "super_duper", "samus_clocktoberfest", "samus_aroace",
    "samus_aroace_2", "samus_enby", "samus_trans", "samus_agender", "samus_blue",
    "samus_greyscale", "alcoon", "alucard_sotn", "arcana", "bailey", "bob", "brad_fang",
    "bruno", "buffed_kirby", "buffed_eggplant", "buffed_pug", "cacodemon", "captain_novolin",
    "ceroba_ketsukane", "chairdeep", "charizard", "charlotte_aran", "crest", "crewmate",
    "cuphead", "cursor", "diddy_kong", "earthworm_jim", "fedtrooper", "fight", "goku_child",
    "infee_nitee", "inkling-girl", "junko", "katt_aran", "kiara", "kiara_idol", "kirby",
    "kirby_yarn", "knuckles", "link_2_the_past", "link_oot", "link_tall", "luigi_mansion",
    "lyn", "marga", "maria_pollo", "maria_renard", "mario_8bit", "mario_8bit_modern",
    "mario_dreamteam", "mario_smw", "master_hand", "maxim_kischine", "megamanx",
    "megamanx_bearded", "metroid", "modul", "moonclif", "officer_donut", "onefourty",
    "plissken", "protogen_laso", "pyronett", "pyronett_a", "richter_belmont",
    "ronald_mcdonald", "samus_combatarmor", "sans", "shantae", "shaktool", "shaktool-jr",
    "snes_controller", "sonic", "space_pirate", "sprite_can", "super_controid_pg", "tails",
    "tetris", "thomcrow_corbin", "wario", "yoshi", "zero_suit_samus", "samus_outline",
    "hitboxhelper2", "samus_backwards", "samus_upsidedown", "samus_180-degree", "samus_mini",
    "samus_left-leg", "samus_cannon", "samus_invisible"
]

sprite_names = {
    "samus_vanilla": "Samus", "samus_dread": "Dread Samus (Super)", "dread_samus": "Dread Samus",
    "santamus": "Santamus", "metroid_1_suit": "Metroid 1 Samus", "samus_fusion_typea_green": "Fusion Samus",
    "dark_samus": "Dark Samus", "dark_samus_2": "Dark Samus 2", "dark_samus_reanimated": "Dark Samus Reanimated",
    "samus_zero-mission": "Zero Mission Samus", "samus_returns": "Samus Returns Samus", "samus_maid": "Samus Maid",
    "hack_opposition": "Opposition Samus", "ped_suit": "PED Suit Samus", "ascent": "Ascent Samus",
    "ancient_chozo": "Ancient Chozo Samus", "super_duper": "Super Duper Samus", "samus_clocktoberfest": "Clocktoberfest Samus",
    "samus_aroace": "Aroace Samus (Old)", "samus_aroace_2": "Aroace Samus (New)", "samus_enby": "Enby Samus",
    "samus_trans": "Trans Samus", "samus_agender": "Agender Samus", "samus_blue": "Blue Samus",
    "samus_greyscale": "Greyscale Samus", "alcoon": "Alcoon", "alucard_sotn": "Alucard",
    "arcana": "Arcana", "bailey": "Justin Bailey", "bob": "B.O.B.", "brad_fang": "Brad Fang",
    "bruno": "Bruno", "buffed_kirby": "Buffed Kirby", "buffed_eggplant": "Buffed Eggplant",
    "buffed_pug": "Buffed Pug", "cacodemon": "Cacodemon", "captain_novolin": "Captain Novolin",
    "ceroba_ketsukane": "Ceroba Ketsukane", "chairdeep": "Chairdeep", "charizard": "Charizard",
    "charlotte_aran": "Charlotte Aran", "crest": "Crest", "crewmate": "Crewmate",
    "cuphead": "Cuphead", "cursor": "Cursor", "diddy_kong": "Diddy Kong",
    "earthworm_jim": "Earthworm Jim", "fedtrooper": "Galactic Federation Trooper", "fight": "Fight",
    "goku_child": "Goku (Child)", "infee_nitee": "Infee and Nitee", "inkling-girl": "Inkling Girl",
    "junko": "Junko", "katt_aran": "Katt Aran", "kiara": "Kiara", "kiara_idol": "Idol Kiara",
    "kirby": "Kirby", "kirby_yarn": "Kirby (Yarn)", "knuckles": "Knuckles",
    "link_2_the_past": "Link 2 the Past", "link_oot": "Link (OoT)", "link_tall": "Link (Z2)",
    "luigi_mansion": "Luigi", "lyn": "Lyn", "marga": "Alice Margatroid",
    "maria_pollo": "Maria Pollo", "maria_renard": "Maria Renard", "mario_8bit": "Mario (NES)",
    "mario_8bit_modern": "Mario (NES, Modern colors)", "mario_dreamteam": "Mario (Dream Team)",
    "mario_smw": "Mario (SMW)", "master_hand": "Master Hand", "maxim_kischine": "Maxim Kischine",
    "megamanx": "Mega Man X", "megamanx_bearded": "Mega Man X (Bearded)", "metroid": "Metroid",
    "modul": "Modul", "moonclif": "Moonclif", "officer_donut": "Officer Donut",
    "onefourty": "140", "plissken": "Plissken", "protogen_laso": "Protogen Laso",
    "pyronett": "Pyronett", "pyronett_a": "Pyronett (Recolor)", "richter_belmont": "Richter Belmont",
    "ronald_mcdonald": "Ronald McDonald", "samus_combatarmor": "Combat Armor Samus", "sans": "Sans",
    "shantae": "Shantae", "shaktool": "Shaktool", "shaktool-jr": "Shaktool Jr.",
    "snes_controller": "SNES Controller", "sonic": "Sonic the Hedgehog", "space_pirate": "Space Pirate",
    "sprite_can": "Sprite Can", "super_controid_pg": "Super Controid", "tails": "Tails",
    "tetris": "Tetromino", "thomcrow_corbin": "Thomcrow Corbin", "wario": "Wario",
    "yoshi": "Yoshi & Baby Mario", "zero_suit_samus": "Zero Suit Samus", "samus_outline": "Outline Samus",
    "hitboxhelper2": "Hitbox Helper", "samus_backwards": "Backwards Samus", "samus_upsidedown": "Upside-Down Samus",
    "samus_180-degree": "180-Degree Samus", "samus_mini": "Mini Samus", "samus_left-leg": "Left Leg Samus",
    "samus_cannon": "Samus Cannon", "samus_invisible": "Invisible Samus"
}

etank_colors = [
    "de3894", "de3843", "de8038", "ded338", "96de38", "43de38", "38de80", "38ded3",
    "3896de", "3843de", "8038de", "d338de", "de8cba", "de8c91", "deaf8c", "ded98c",
    "bade8c", "91de8c", "8cdeaf", "8cded9", "8cbade", "8c91de", "af8cde", "d98cde"
]

color_names = {
    "de3894": "Intense Pink", "de3843": "Bright Red", "de8038": "Orange", "ded338": "Yellow",
    "96de38": "Lime Green", "43de38": "Bright Green", "38de80": "Aqua Green", "38ded3": "Cyan",
    "3896de": "Sky Blue", "3843de": "Intense Blue", "8038de": "Purple", "d338de": "Magenta",
    "de8cba": "Pastel Pink", "de8c91": "Salmon Pink", "deaf8c": "Peach", "ded98c": "Pastel Yellow",
    "bade8c": "Pastel Green", "91de8c": "Mint Green", "8cdeaf": "Pastel Aqua", "8cded9": "Pastel Cyan",
    "8cbade": "Pastel Azure", "8c91de": "Lavender", "af8cde": "Lilac", "d98cde": "Pink Purple"
}

other_values = {
    "control_angle_down": "L", "control_angle_up": "R", "control_dash": "B",
    "control_item_cancel": "Y", "control_item_select": "Select", "control_jump": "A",
    "control_shot": "X", "disable_beeping": "false", "door_theme": "vanilla",
    "energy_tank_color": "", "flashing": "Reduced", "item_dot_change": "Fade",
    "moonwalk": "false", "music": "area", "quick_reload_a": False, "quick_reload_b": False,
    "quick_reload_down": False, "quick_reload_l": True, "quick_reload_left": False,
    "quick_reload_r": True, "quick_reload_right": False, "quick_reload_select": True,
    "quick_reload_start": True, "quick_reload_up": False, "quick_reload_x": False,
    "quick_reload_y": False, "reserve_hud_style": "true", "room_names": "true",
    "room_palettes": "vanilla", "room_theming": "tiling", "shaking": "Reduced",
    "spin_lock_a": False, "spin_lock_b": False, "spin_lock_down": False, "spin_lock_l": True,
    "spin_lock_left": False, "spin_lock_r": True, "spin_lock_right": False,
    "spin_lock_select": False, "spin_lock_start": False, "spin_lock_up": True,
    "spin_lock_x": True, "spin_lock_y": False, "tile_theme": "area_themed",
    "transition_letters": "true", "vanilla_screw_attack_animation": "false"
}

if args.list:
    print("\n╔════════════════════════╗")
    print("║  Sprites and Colors    ║")
    print("╚════════════════════════╝\n")
    print("SAMUS SPRITES:")
    print("─" * 70)
    max_display_len = max(len(name) for name in sprite_names.values())
    for sprite_id in samus_sprites:
        display_name = sprite_names.get(sprite_id, sprite_id)
        padding = max_display_len - len(display_name)
        print(f"  {display_name}{' ' * padding}  =  {sprite_id}")
    print("\n\nE-TANK COLORS:")
    print("─" * 70)
    max_color_len = max(len(name) for name in color_names.values())
    for color_id in etank_colors:
        display_name = color_names.get(color_id, color_id)
        padding = max_color_len - len(display_name)
        print(f"  {display_name}{' ' * padding}  =  {color_id}")
    print("\n")
    exit(0)

def check_race_mode_from_page(driver):
    try:
        is_race_mode = driver.execute_script("""
            const raceModeYes = document.getElementById('raceModeYes');
            if (raceModeYes) {
                return raceModeYes.checked;
            }
            return false;
        """)
        return is_race_mode
    except Exception as e:
        print(f"   ⚠️ Warning: Could not check race mode status: {e}")
        return False

def get_spoiler_token(driver):
    try:
        token = driver.execute_script("return localStorage.getItem('spoilerToken');")
        return token
    except:
        return None

def save_spoiler_token(output_dir, seed_id, token):
    try:
        filename = f"SpoilerToken_{seed_id}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Spoiler Token: {token}\n")
            f.write(f"URL: https://maprando.com/seed/{seed_id}\n")
        return filepath
    except Exception as e:
        print(f"   ⚠️ Warning: Could not save spoiler token to file: {e}")
        return None

def clear_spoiler_token(driver):
    try:
        driver.execute_script("localStorage.removeItem('spoilerToken');")
    except:
        pass

if args.token:
    if any([args.input, args.preset, args.output, args.generate != 1, args.random, args.sprite, args.color]):
        parser.error("-t/--token cannot be used with other generation arguments")
    print("\n╔═════════════════════════╗")
    print("║  Spoiler Map Unlocker   ║")
    print("╚═════════════════════════╝\n")
    seed_input = args.token.strip()
    if seed_input.startswith('http'):
        if '/seed/' not in seed_input:
            parser.error("Invalid seed URL format. Expected: https://maprando.com/seed/XXXXXXXXX or just the seed ID")
        seed_id = seed_input.rstrip('/').split('/seed/')[-1].split('/')[0].split('?')[0]
    else:
        seed_id = seed_input
    seed_url = f"https://maprando.com/seed/{seed_id}/"
    print(f"🔑 Seed ID: {seed_id}")
    spoiler_token_from_file = None
    token_file_pattern = f"SpoilerToken_{seed_id}.txt"
    search_directories = [os.getcwd()]
    if args.output:
        search_dir = os.path.abspath(args.output)
        if os.path.exists(search_dir):
            search_directories.insert(0, search_dir)
    for search_dir in search_directories:
        token_file_path = os.path.join(search_dir, token_file_pattern)
        if os.path.exists(token_file_path):
            try:
                with open(token_file_path, 'r') as f:
                    for line in f:
                        if line.startswith('Spoiler Token:'):
                            spoiler_token_from_file = line.split('Spoiler Token:')[1].strip()
                            break
                if spoiler_token_from_file:
                    print(f"📄 Found token file: {token_file_pattern}")
                    break
            except Exception as e:
                pass
    driver = get_browser_driver(args.browser)
    try:
        print("🌐 Connecting to seed page...", end="", flush=True)
        driver.get(seed_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(" ✓")
        if spoiler_token_from_file:
            print(f"🔓 Using token from file")
            spoiler_token_input = spoiler_token_from_file
        else:
            spoiler_token_input = input("🔐 Enter spoiler token: ").strip()
            if not spoiler_token_input:
                print("❌ Error: Spoiler token cannot be empty")
                driver.quit()
                exit(1)
        print("🔑 Setting spoiler token...", end="", flush=True)
        driver.execute_script(f"localStorage.setItem('spoilerToken', '{spoiler_token_input}');")
        print(" ✓")
        print("🔄 Reloading page...", end="", flush=True)
        driver.refresh()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.5)
        print(" ✓")
        print("🔓 Unlocking spoiler data...", end="", flush=True)
        result = driver.execute_script("""
            return new Promise((resolve) => {
                const token = localStorage.getItem('spoilerToken');
                if (!token) {
                    resolve({
                        success: false,
                        error: 'No spoiler token found in localStorage'
                    });
                    return;
                }
                const unlockForm = document.getElementById('unlockForm');
                if (!unlockForm) {
                    resolve({
                        success: false,
                        error: 'Unlock button not found - seed may not be in race mode'
                    });
                    return;
                }
                unlockForm.style.display = 'flex';
                const submitButton = unlockForm.querySelector('input[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                } else {
                    unlockForm.submit();
                }
                setTimeout(() => {
                    const checkResult = setInterval(() => {
                        const visualizerLink = document.querySelector('a[href*="visualizer"]');
                        if (visualizerLink) {
                            clearInterval(checkResult);
                            resolve({
                                success: true,
                                visualizerUrl: visualizerLink.href,
                                linkText: visualizerLink.textContent.trim()
                            });
                        }
                    }, 500);
                    setTimeout(() => {
                        clearInterval(checkResult);
                        const visualizerLink = document.querySelector('a[href*="visualizer"]');
                        if (visualizerLink) {
                            resolve({
                                success: true,
                                visualizerUrl: visualizerLink.href,
                                linkText: visualizerLink.textContent.trim()
                            });
                        } else {
                            resolve({
                                success: false,
                                error: 'Visualizer link not found after unlock'
                            });
                        }
                    }, 5000);
                }, 100);
            });
        """)
        print(" ✓")
        if result.get('success'):
            visualizer_url = result.get('visualizerUrl')
            print(f"\n✅ Success! Spoiler map unlocked")
            print(f"🗺️  Interactive Map URL:")
            print(f"   {visualizer_url}\n")
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f" ❌")
            print(f"\n❌ Error: {error_msg}")
            print("   The token may be invalid or the seed may not be in race mode\n")
    except Exception as e:
        print(f" ❌")
        print(f"\n❌ Error: {str(e)}\n")
    finally:
        driver.quit()
    exit(0)

EXPECTED_ROM_HASH = "12b77c4bc9c1832cee8881244659065ee1d84c70c3d29e6eaf92e6798cc2ca72"

def verify_rom_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_preset_file(driver, preset_path):
    preset_name = os.path.splitext(os.path.basename(preset_path))[0]
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#managePresetsModal']"))
    ).click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'Manage Settings Presets')]"))
    )
    file_input = driver.find_element(By.ID, "importPresetFile")
    file_input.send_keys(os.path.abspath(preset_path))
    time.sleep(0.5)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='managePresetsModal']//button[contains(text(),'Close')]"))
    ).click()
    time.sleep(0.3)
    return preset_name

def select_preset(driver, preset_name):
    preset_dropdown = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "fullSettingsPreset"))
    )
    select = Select(preset_dropdown)
    select.select_by_visible_text(preset_name)

if not args.input:
    parser.error("the following arguments are required: -i/--input\n\nNote: -l/--list command cannot be used with other arguments.")

if args.sprite and args.sprite not in samus_sprites:
    parser.error(f"Invalid sprite '{args.sprite}'. Please use a valid sprite name. Use -l to see all available sprites.")
if args.color and args.color not in etank_colors:
    parser.error(f"Invalid color '{args.color}'. Please use a valid hex code. Use -l to see all available colors.")

if args.random and (args.sprite or args.color):
    parser.error("Cannot use -r/--random with -s/--sprite or -c/--color")

output_dir = os.path.abspath(args.output) if args.output else os.getcwd()
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

preset_list = []
if args.preset:
    if ',' in args.preset:
        preset_list = [p.strip() for p in args.preset.split(',')]
        if len(preset_list) != args.generate:
            parser.error(f"Number of presets ({len(preset_list)}) must match number of seeds to generate ({args.generate})")
    else:
        preset_list = [args.preset] * args.generate
else:
    preset_list = [None] * args.generate

print("\n╔═══════════════════════════╗")
print("║  Randomap Web Generator   ║")
print("╚═══════════════════════════╝\n")

print(f"🔍 Verifying input ROM...")
input_rom_hash = verify_rom_hash(args.input)
if input_rom_hash != EXPECTED_ROM_HASH:
    print(f"❌ ERROR: ROM hash mismatch!")
    print(f"   Expected: {EXPECTED_ROM_HASH}")
    print(f"   Got:      {input_rom_hash}")
    print(f"   Please provide a valid Super Metroid ROM.\n")
    exit(1)
print(f"✓ ROM verified\n")

driver = get_browser_driver(args.browser, output_dir)
loaded_preset_files = {}

try:
    for seed_num in range(1, args.generate + 1):
        is_first_seed = (seed_num == 1)
        current_preset = preset_list[seed_num - 1]
        if args.generate > 1:
            print(f"[{seed_num}/{args.generate}] ", end="", flush=True)
        customization_data = other_values.copy()
        if args.random:
            selected_sprite = random.choice(samus_sprites)
            selected_color = random.choice(etank_colors)
            customization_data['samus_sprite'] = selected_sprite
            customization_data['etank_color'] = selected_color
            sprite_display_name = sprite_names.get(selected_sprite, selected_sprite)
            color_display_name = color_names.get(selected_color, selected_color)
            if is_first_seed:
                print(f"🎨 Randomizing customization for each seed")
            print(f"   👤 Sprite: {sprite_display_name}")
            print(f"   ❤️ E-Tank Color: {color_display_name}")
        elif args.sprite or args.color:
            if args.sprite:
                customization_data['samus_sprite'] = args.sprite
                sprite_display_name = sprite_names.get(args.sprite, args.sprite)
                if is_first_seed:
                    print(f"🎨 Using custom sprite")
                    print(f"   👤 Sprite: {sprite_display_name}")
            if args.color:
                customization_data['etank_color'] = args.color
                color_display_name = color_names.get(args.color, args.color)
                if is_first_seed:
                    if not args.sprite:
                        print(f"🎨 Using custom E-Tank color")
                    print(f"   ❤️ E-Tank Color: {color_display_name}")
        else:
            if is_first_seed:
                print(f"🎨 Using default customization")
        if is_first_seed:
            print("🌐 Connecting to maprando.com...", end="", flush=True)
        driver.get("https://maprando.com/generate")
        driver.execute_script(
            f"localStorage.setItem('customization-form', JSON.stringify({json.dumps(customization_data)}));"
        )
        driver.refresh()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fullSettingsPreset")))
        if is_first_seed:
            print(" ✓")
        if current_preset:
            if current_preset.endswith('.json') and os.path.isfile(current_preset):
                preset_name = os.path.splitext(os.path.basename(current_preset))[0]
                if current_preset not in loaded_preset_files:
                    if is_first_seed or args.generate > 1:
                        print(f"📋 Loading preset file '{preset_name}'...", end="", flush=True)
                    preset_name = load_preset_file(driver, current_preset)
                    loaded_preset_files[current_preset] = preset_name
                    if is_first_seed or args.generate > 1:
                        print(" ✓")
                else:
                    preset_name = loaded_preset_files[current_preset]
                    if args.generate > 1:
                        print(f"📋 Using preset '{preset_name}'...", end="", flush=True)
                        print(" ✓")
                select_preset(driver, preset_name)
            else:
                preset_name = current_preset
                if is_first_seed or args.generate > 1:
                    print(f"📋 Selecting preset '{preset_name}'...", end="", flush=True)
                try:
                    select_preset(driver, preset_name)
                    if is_first_seed or args.generate > 1:
                        print(" ✓")
                except Exception as e:
                    print(f" ❌")
                    print(f"   ERROR: Preset '{preset_name}' not found")
                    print(f"   Available presets can be viewed at https://maprando.com/generate")
                    driver.quit()
                    exit(1)
        elif is_first_seed and not current_preset:
            print("📋 Using default settings")
        time.sleep(0.3)
        is_race_mode = check_race_mode_from_page(driver)
        if args.generate > 1:
            print("⚙️  Generating...", end="", flush=True)
        else:
            print("⚙️  Generating seed...", end="", flush=True)
        generate_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate Game')]"))
        )
        generate_button.click()
        WebDriverWait(driver, 90).until(lambda d: '/seed/' in d.current_url)
        time.sleep(1)
        seed_id = driver.current_url.split('/seed/')[-1].split('/')[0].split('?')[0]
        seed_url = f"https://maprando.com/seed/{seed_id}"
        print(f" {seed_id}", end="", flush=True)
        spoiler_token = get_spoiler_token(driver)
        if spoiler_token and is_race_mode:
            print(" ✓")
            print(f"   🏁 Race Mode Detected")
            print(f"   🔒 Spoiler Token: {spoiler_token}")
            saved_path = save_spoiler_token(output_dir, seed_id, spoiler_token)
            if saved_path:
                print(f"   💾 Token saved to: {os.path.basename(saved_path)}")
            clear_spoiler_token(driver)
        else:
            print(" ✓")
            if spoiler_token:
                clear_spoiler_token(driver)
        driver.execute_script("""
            const modals = document.querySelectorAll('.modal');
            for (let modal of modals) {
                const heading = modal.querySelector('h1');
                if (heading && heading.textContent.includes('Input ROM')) {
                    modal.classList.add('show');
                    modal.style.display = 'block';
                    document.body.classList.add('modal-open');
                    let backdrop = document.querySelector('.modal-backdrop');
                    if (!backdrop) {
                        backdrop = document.createElement('div');
                        backdrop.className = 'modal-backdrop fade show';
                        document.body.appendChild(backdrop);
                    }
                    break;
                }
            }
        """)
        time.sleep(0.5)
        rom_input = driver.find_element(By.ID, "inputRom")
        rom_input.send_keys(os.path.abspath(args.input))
        time.sleep(1)
        download_submit = driver.execute_script("""
            const modal = document.querySelector('.modal.show');
            if (modal) {
                return modal.querySelector('input[type="submit"][value="Download ROM"]');
            }
            return null;
        """)
        if download_submit:
            download_submit.click()
        max_wait = 60
        elapsed = 0
        file_found = False
        expected_filename = f"map-rando-{seed_id}.sfc"
        while elapsed < max_wait:
            for filename in os.listdir(output_dir):
                if filename == expected_filename:
                    file_path = os.path.join(output_dir, filename)
                    try:
                        file_size = os.path.getsize(file_path)
                        time.sleep(2)
                        new_size = os.path.getsize(file_path)
                        if new_size == file_size:
                            file_found = True
                            break
                    except:
                        pass
            if file_found:
                break
            time.sleep(1)
            elapsed += 1
        if file_found:
            old_path = os.path.join(output_dir, expected_filename)
            new_filename = f"Super Metroid Randomap {seed_id}.sfc"
            new_path = os.path.join(output_dir, new_filename)
            try:
                os.rename(old_path, new_path)
            except:
                pass
        print(f"   🔗 Seed URL: {seed_url}")
    print("\n╔════════════╗")
    print("║  FINISHED  ║")
    print("╚════════════╝")
    print(f"\n📂 ROM(s) saved to: {output_dir}")
    if args.generate > 1:
        print(f"📊 Total seeds generated: {args.generate}\n")
    else:
        print()
finally:
    driver.quit()