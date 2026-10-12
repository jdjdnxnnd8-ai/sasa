# -*- coding: utf-8 -*-

import telebot
import requests
import threading
import time
import random
import json
import os
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== إعدادات البوت =====
BOT_TOKEN = "8805291460:AAHeRh8J1PT29EiJvXdQSSgGMAoXE34B3Fc"
ADMIN_ID = 6287438473
ADMINS = {ADMIN_ID}
BANNED_USERS = set()
BLOCKED_GROUPS = set()
VIDEO_URL = "https://t.me/hmo769/249"
bot = telebot.TeleBot(BOT_TOKEN)
SERVER_ME = "https://clientbp.ppmainecoonghj.com/"

GROUPS_FILE = "groups.json"
ADMINS_FILE = "admins.json"
BANNED_FILE = "banned.json"
BLOCKED_GROUPS_FILE = "blocked_groups.json"
CODES_FILE = "codes.json"
VIP_USERS_FILE = "vip_users.json"

# متغيرات للتحكم بالسبام اللانهائي لكل مجموعة وحسب الأيدي
active_infinite_spams = {} # (chat_id, target_uid): threading.Event

# ===== تحميل وحفظ البيانات =====
def load_data():
    global enabled_groups, ADMINS, BANNED_USERS, BLOCKED_GROUPS, activation_codes, vip_users
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r') as f:
            enabled_groups = set(json.load(f))
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            ADMINS = set(json.load(f))
            ADMINS.add(ADMIN_ID)
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, 'r') as f:
            BANNED_USERS = set(json.load(f))
    if os.path.exists(BLOCKED_GROUPS_FILE):
        with open(BLOCKED_GROUPS_FILE, 'r') as f:
            BLOCKED_GROUPS = set(json.load(f))
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, 'r') as f:
            activation_codes = json.load(f)
    else:
        activation_codes = {}
    if os.path.exists(VIP_USERS_FILE):
        with open(VIP_USERS_FILE, 'r') as f:
            vip_users = json.load(f)
    else:
        vip_users = {}

def save_data():
    with open(GROUPS_FILE, 'w') as f:
        json.dump(list(enabled_groups), f)
    with open(ADMINS_FILE, 'w') as f:
        json.dump(list(ADMINS), f)
    with open(BANNED_FILE, 'w') as f:
        json.dump(list(BANNED_USERS), f)
    with open(BLOCKED_GROUPS_FILE, 'w') as f:
        json.dump(list(BLOCKED_GROUPS), f)
    with open(CODES_FILE, 'w') as f:
        json.dump(activation_codes, f)
    with open(VIP_USERS_FILE, 'w') as f:
        json.dump(vip_users, f)

enabled_groups = set()
activation_codes = {}
vip_users = {}
load_data()

# ═══════════════════════════════════════════════════════
#   ✅ قائمة الحسابات الكاملة
# ═══════════════════════════════════════════════════════
ACCOUNTS_LIST = {
    "8023713432": "4O3NP2F3-IRW_0", "8023713847": "XP3Q6ZSF-IRW_0", "8023714003": "F60EZ6XN-IRW_0",
    "8023714144": "V9V2U964-IRW_0", "8023714244": "2N446P5M-IRW_0", "8023714552": "LUJSHM8V-IRW_0",
    "8023714567": "W4J3EM7T-IRW_0", "8023716057": "P1CBUQ2R-IRW_0", "8023716250": "HFV966FK-IRW_0",
    "8023716528": "3MVL7YKU-IRW_0", "8023716799": "MOD1JGJ0-IRW_0", "8023717876": "MJ8RVV59-IRW_0",
    "8023718368": "RIMTY5XM-IRW_0", "8023718898": "TJ9M2OXW-IRW_0", "8023721051": "9IHGNB1H-IRW_0",
    "8023722387": "5NREUFBN-IRW_0", "8023722558": "L7H5MQHQ-IRW_0", "8023722786": "ZKSO83HE-IRW_0",
    "8023723038": "JA2SRWJO-IRW_0", "8023723303": "OOUZQBU7-IRW_0", "8023723497": "9WHINA6L-IRW_0",
    "8023725548": "0ZTJOFI1-IRW_0", "8023726080": "0LJ6YFEC-IRW_0", "8023726884": "3FVHDKTR-IRW_0",
    "8023727107": "E98XTY6R-IRW_0", "8023727199": "X4FIDOLY-IRW_0", "8023727391": "KYN0H9LG-IRW_0",
    "8023728764": "PQLA9300-IRW_0", "8023730829": "1W0II0VF-IRW_0", "8023731359": "OAWLGITZ-IRW_0",
    "8023732522": "4S674W81-IRW_0", "8023735608": "A5HKV2RA-IRW_0", "8023735631": "NBR7RK5H-IRW_0",
    "8023736187": "0PH3QQ9E-IRW_0", "8023736555": "TT93JHXD-IRW_0", "8023736708": "EEWEP1F2-IRW_0",
    "8023738376": "EERO3JHE-IRW_0", "8023738547": "JFR9X6LQ-IRW_0", "8023738797": "ZMNFRMX7-IRW_0",
    "8023738942": "9EBXKAF6-IRW_0", "8023740179": "5XYPVULK-IRW_0", "8023740251": "0DN4035M-IRW_0",
    "8023743413": "1JCALJI2-IRW_0", "8023743454": "WD76GBPL-IRW_0", "8023743529": "O6A43740-IRW_0",
    "8023743556": "K2T4GBY7-IRW_0", "8023744002": "A0B9FFI5-IRW_0", "8023745282": "6D2HJS8O-IRW_0",
    "8023745542": "S744AS8P-IRW_0", "8023745848": "M4VM1RE9-IRW_0", "8023746091": "0GN5ID7K-IRW_0",
    "8023746141": "3KTQ6AF9-IRW_0", "8023746263": "AVF6WAGA-IRW_0", "8023746347": "XK98IMFA-IRW_0",
    "8023746470": "BI7UQH5Z-IRW_0", "8023746518": "0Q7OLY5X-IRW_0", "8023746652": "JERGBPPF-IRW_0",
    "8023746747": "GRTG5AKA-IRW_0", "8023746863": "2YITI0O1-IRW_0", "8023746922": "42GHTNYW-IRW_0",
    "8023747002": "AHUCEBVB-IRW_0", "8023747080": "FPD8I40L-IRW_0", "8023747241": "C5SM7LST-IRW_0",
    "8023747328": "WPRKBRAV-IRW_0", "8023747391": "Y1TONDOJ-IRW_0", "8023747491": "66IPFKXN-IRW_0",
    "8023747605": "UXB356YH-IRW_0", "8023747660": "5UVFJ03D-IRW_0", "8023747728": "9SWVD2DV-IRW_0",
    "8023747794": "AL602PKS-IRW_0", "8023747857": "U6EOUB5B-IRW_0", "8023747981": "ZS6HZKCD-IRW_0",
    "8023749679": "CPW7PRGI-IRW_0", "8023749854": "SVROFI04-IRW_0", "8023750047": "47LII1K7-IRW_0",
    "8023750113": "8KO725K1-IRW_0", "8023750331": "J3TJ5BP3-IRW_0", "8023750371": "7WMDCVUV-IRW_0",
    "8023750565": "ZHT82YQI-IRW_0", "8023750809": "MHZ527AP-IRW_0", "8023750751": "MCP3EDRL-IRW_0",
    "8023751004": "CT5XZNOQ-IRW_0", "8023751175": "MQKQBNOQ-IRW_0", "8023751176": "QQUPQ28C-IRW_0",
    "8023751307": "LQP24404-IRW_0", "8023751319": "QYFNAQ8L-IRW_0", "8023751406": "1F3X78RN-IRW_0",
    "8023751432": "XNPRBFEZ-IRW_0", "8023751548": "ECBRDNGN-IRW_0", "8023751630": "UD126VVM-IRW_0",
    "8023751676": "YYXCOD79-IRW_0", "8023751889": "SYXB8G1F-IRW_0", "8023751978": "6NRV9DTF-IRW_0",
    "8023752034": "4T68WQ6Q-IRW_0", "8023752113": "WOQTS287-IRW_0", "8023752192": "MFOI2QFW-IRW_0",
    "8023752304": "6299HXYB-IRW_0", "8023753149": "T1NHJXM3-IRW_0", "8023753503": "P7BVH0CD-IRW_0",
    "8023753978": "G8ZCZA6P-IRW_0", "8023754292": "UHUYJ5FP-IRW_0", "8023754556": "FWEHVUQY-IRW_0",
    "8023754716": "35KAHXVZ-IRW_0", "8023754912": "YEWC5WIC-IRW_0", "8023755052": "6YNEE0JQ-IRW_0",
    "8023755196": "T8EZTPWU-IRW_0", "8023755704": "BCXKCJMY-IRW_0", "8023756414": "V8LBV090-IRW_0",
    "8023756478": "T682SLVH-IRW_0", "8023756710": "BM5U2P5A-IRW_0", "8023756773": "J1NPGNKO-IRW_0",
    "8023756982": "XEH4HLY4-IRW_0", "8023757276": "QANZTIW3-IRW_0", "8023757460": "0ANPSIXD-IRW_0",
    "8023757516": "REHWF3ZD-IRW_0", "8023757659": "GYOYMQZJ-IRW_0", "8023757867": "RTU1CRYU-IRW_0",
    "8023758336": "XA6C183E-IRW_0", "8023759996": "2U8RFH4J-IRW_0", "8023760394": "T7U6IS5J-IRW_0",
    "8023760478": "047DLZUA-IRW_0", "8023760851": "2T5014XF-IRW_0", "8023760815": "WPXIMQBJ-IRW_0",
    "8023761185": "9NBOCXDB-IRW_0", "8023761213": "N89YOG6T-IRW_0", "8023761595": "5DGOBTH5-IRW_0",
    "8023761913": "N3IBJ93G-IRW_0", "8023761936": "MUZF4IPB-IRW_0", "8023762173": "MNWXBISJ-IRW_0",
    "8023762199": "RXH3GWXX-IRW_0", "8023762457": "6XBHAV7C-IRW_0", "8023762438": "LQNBW2ZG-IRW_0",
    "8023762643": "3KY03U7L-IRW_0", "8023762848": "ETZPRF3I-IRW_0", "8023762847": "AW4TTJU4-IRW_0",
    "8023763044": "ANF6NQVZ-IRW_0", "8023763045": "CI4PL4S3-IRW_0", "8023763392": "LG16IPWQ-IRW_0",
    "8023763529": "LKFH9TVY-IRW_0", "8023764140": "E5YGTDWT-IRW_0", "8023765520": "WTKDR4S5-IRW_0",
    "8023765536": "A3I1Y9KH-IRW_0", "8023766101": "X3J8NU6F-IRW_0", "8023766520": "3BKJR8WM-IRW_0",
    "8023766506": "9K9N62JW-IRW_0", "8023766912": "WSZVUG6P-IRW_0", "8023766917": "GNX75DI9-IRW_0",
    "8023767375": "GSD44200-IRW_0", "8023767709": "Z58YKEVZ-IRW_0", "8023767711": "FCG29P0Z-IRW_0",
    "8023768049": "MZVMUHCU-IRW_0", "8023768301": "LIFZE717-IRW_0", "8023768322": "LEDY8LAM-IRW_0",
    "8023768553": "T7E4SS1Y-IRW_0", "8023768780": "DIUZTS3Y-IRW_0", "8023768753": "6JXN41HS-IRW_0",
    "8023768961": "G9CYB2ZU-IRW_0", "8023768977": "MXRWET4W-IRW_0", "8023769151": "IY6JG1Y4-IRW_0",
    "8023769154": "V6NHN9JH-IRW_0", "8023769311": "ADDQWD1C-IRW_0", "8023769323": "RMB8H1XB-IRW_0",
    "8023769482": "KCKX0D0N-IRW_0", "8023769522": "UIVVDVNY-IRW_0", "8023769602": "4Z82Q670-IRW_0",
    "8023770993": "33FK7UEY-IRW_0", "8023771654": "F5ULXBBC-IRW_0", "8023771850": "XV7OIA76-IRW_0",
    "8023772176": "MNGRN9H1-IRW_0", "8023772336": "WQ49CNLO-IRW_0", "8023772442": "OXZ33TNB-IRW_0",
    "8023772598": "JS2V8D6J-IRW_0", "8023772717": "X1AZ3HH6-IRW_0", "8023772982": "ZX9G7A0H-IRW_0",
    "8023773145": "MFPNVS22-IRW_0", "8023773188": "K6ELUN48-IRW_0", "8023773336": "U3IH2JKY-IRW_0",
    "8023773479": "2Q8EVYC0-IRW_0", "8023773543": "W60OW1QX-IRW_0", "8023773632": "JM8SI4DZ-IRW_0",
    "8023773756": "Q1N9JKR8-IRW_0", "8023773847": "GEZI3A5E-IRW_0", "8023773902": "HZYYYCDF-IRW_0",
    "8023774001": "36ADI021-IRW_0", "8023774118": "E8FEXOE6-IRW_0", "8023774223": "G88N8KBZ-IRW_0",
    "8023774328": "3J3F8G1Q-IRW_0", "8023775389": "SDNBYRBP-IRW_0", "8023775439": "X0G8QHZA-IRW_0",
    "8023776183": "I8WZQ2E4-IRW_0", "8023776185": "GR0G7DZM-IRW_0", "8023776533": "3WADHG1B-IRW_0",
    "8023776792": "38CPIFJO-IRW_0", "8023776866": "HQ555ZES-IRW_0", "8023777081": "ZFSL7SVK-IRW_0",
    "8023777206": "ALK3IQ83-IRW_0", "8023777487": "3EKUFN3G-IRW_0", "8023777731": "TQXKMQ45-IRW_0",
    "8023777838": "ZGYFT7SA-IRW_0", "8023777937": "6UF8P51G-IRW_0", "8023778053": "CIXWPU4K-IRW_0",
    "8023778218": "BYVFYNAS-IRW_0", "8023778351": "Q9X7M2PL-IRW_0", "8023778492": "8K4N2W1X-IRW_0",
    "8023778610": "M3L9P0Q5-IRW_0", "8023778844": "7Z2V5K9H-IRW_0", "8023779012": "5B1Y8J4N-IRW_0",
    "8023779230": "2C6X9M3R-IRW_0", "8023779455": "9P4L1K7V-IRW_0", "8023779688": "4H8N2Q6Z-IRW_0",
    "8023779901": "1V5M3K8X-IRW_0", "8023780124": "6B9P7L2N-IRW_0", "8023780350": "3X1V8M5Q-IRW_0",
    "8023780591": "8N2H4K6P-IRW_0", "8023780812": "5Q9M1L3V-IRW_0", "8023781045": "2K6P8N4X-IRW_0",
    "8023781260": "9V1X3M7Q-IRW_0", "8023781498": "4L8N2K5P-IRW_0", "8023781721": "1X5V3M9Q-IRW_0",
    "8023781950": "7P2H4K8N-IRW_0", "8023782183": "3M9V1L6X-IRW_0",
    "8026689963": "350WKQDN-IRW_0", "8026690144": "PE2RNV9V-IRW_0", "8026690899": "NR0RUOG8-IRW_0",
    "8026690940": "0UFKLP6N-IRW_0", "8026691869": "WH3BMMOK-IRW_0", "8026692102": "O2PPBBB3-IRW_0",
    "8026692317": "2BZ0VZ7M-IRW_0", "8026692696": "RXQMTD0Q-IRW_0", "8026694134": "CH0UZAEI-IRW_0",
    "8026694476": "JES1PZWU-IRW_0", "8026695298": "F4CT14JM-IRW_0", "8026696124": "6FZZ68F1-IRW_0",
    "8026696198": "6T0RLDJ6-IRW_0", "8026696329": "IB752GVV-IRW_0", "8026696813": "9YT5Y4SN-IRW_0",
    "8026696868": "1P09I93J-IRW_0", "8026700296": "RTF09YK3-IRW_0", "8026700591": "BOQVTMJZ-IRW_0",
    "8026700889": "4IBT7OCK-IRW_0", "8026701570": "IREQX8QF-IRW_0", "8026701855": "0H4PC4HM-IRW_0",
    "8026701962": "FHF1G84N-IRW_0", "8026703038": "B5WFQYLN-IRW_0", "8026702898": "CV9N71FY-IRW_0",
    "8026704275": "QDZS9TCQ-IRW_0", "8026704701": "NT8Q0R3J-IRW_0", "8026706682": "YUD5DRBF-IRW_0",
    "8026707668": "9U1A8SUV-IRW_0", "8026710594": "Z0P6BWVN-IRW_0", "8026711427": "RWUV17Z0-IRW_0",
    "8026713686": "29WQ82EL-IRW_0", "8026714142": "CQR2QEH7-IRW_0", "8026715235": "DZ14I587-IRW_0",
    "8026715807": "KJUZDMHP-IRW_0", "8026716583": "VFCP749Q-IRW_0", "8026718688": "ZIYZT1F2-IRW_0",
    "8026719162": "4QRY9JJW-IRW_0", "8026719507": "D9HXC0TQ-IRW_0", "8026719654": "TRO1BTE4-IRW_0",
    "8026721156": "J6I2VT03-IRW_0", "8026721792": "UAHSPMF3-IRW_0", "8026724137": "LJ7ZILGP-IRW_0",
    "8026724689": "8ZDL5D8W-IRW_0", "8026725990": "CYUZNGTG-IRW_0", "8026727133": "VBQ0WTOG-IRW_0",
    "8026727480": "8MCE2A37-IRW_0", "8026727763": "FLJ73LGJ-IRW_0", "8026729107": "S383VOEN-IRW_0",
    "8026730165": "VC2XMK80-IRW_0", "8026730644": "9C7EFZM9-IRW_0", "8026731536": "LJP9V7UE-IRW_0",
    "8026733462": "I3GTOZ9W-IRW_0", "8026733838": "DOCDTPSA-IRW_0", "8026734208": "IUI4UYA8-IRW_0",
    "8026734689": "1EG8RH0R-IRW_0", "8026734982": "AP70RP6P-IRW_0", "8026735716": "UEJ2VCPC-IRW_0",
    "8026739526": "RP8YK58P-IRW_0", "8030176453": "CZ27FTG1-IRW_0", "8030176439": "FNV4FILE-IRW_0",
    "8030177424": "VI52JJFI-IRW_0", "8030178210": "RCMQDVTI-IRW_0", "8030178763": "NG07TFE5-IRW_0",
    "8030178997": "5Z0OH970-IRW_0", "8030179505": "X72UDDKX-IRW_0", "8030179188": "79PHY5V5-IRW_0",
    "8030180017": "4756T16T-IRW_0", "8030180092": "4AZVVSIG-IRW_0", "8030180334": "3ZYBW8GV-IRW_0",
    "8030180438": "LN867BG4-IRW_0", "8030180627": "6FO733LD-IRW_0", "8030180776": "K6QB8PFZ-IRW_0",
    "8030180852": "YKMWI0CI-IRW_0", "8030180965": "12EXGP6U-IRW_0", "8030181181": "9JTM77ID-IRW_0",
    "8030181411": "3QTN56WH-IRW_0", "8030181890": "5GWMUDIO-IRW_0", "8030183886": "LK3CW9SR-IRW_0",
    "8030183683": "QRQCM19Q-IRW_0", "8030184622": "M38459BO-IRW_0", "8030184626": "X1P51PAU-IRW_0",
    "8030185250": "WYTGO3K0-IRW_0", "8030185595": "RB0F29FB-IRW_0", "8030186465": "5QPX8Q6M-IRW_0",
    "8030186898": "SWTDCTL8-IRW_0", "8030187127": "NZBTU6DE-IRW_0", "8030187667": "FOMA5BRS-IRW_0",
    "8030187743": "Q3CSOXX1-IRW_0", "8030188138": "92K7RH6S-IRW_0", "8030188223": "BZY6ZDX3-IRW_0",
    "8030188581": "ACVKRWJN-IRW_0", "8030188913": "YZ6VMPJZ-IRW_0", "8030189035": "8M6BCI43-IRW_0",
    "8030189186": "I5YHO5NT-IRW_0", "8030189464": "MUNVY2YK-IRW_0", "8030189345": "JOFEGZ21-IRW_0",
    "8030189619": "NS6Y60E6-IRW_0", "8030189658": "3D1QYJVC-IRW_0", "8030189788": "UPRZ948B-IRW_0",
    "8030189889": "NVQZKQ74-IRW_0", "8030190603": "NFZCK0NP-IRW_0", "8030192711": "FDI9S858-IRW_0",
    "8030192231": "PLL71WOV-IRW_0", "8030193676": "84FVL383-IRW_0", "8030193994": "X9XOTWJQ-IRW_0",
    "8030194661": "TJFZDTY0-IRW_0", "8030195020": "BI20F1VS-IRW_0", "8030195242": "M73ZCEHT-IRW_0",
    "8030196167": "YR6JP5I0-IRW_0", "8030196654": "HOCJAILD-IRW_0", "8030196682": "5VZQ99G8-IRW_0",
    "8030197200": "VRPYFAVA-IRW_0", "8030197376": "Q4U9566O-IRW_0", "8030197905": "3H1A8P8G-IRW_0",
    "8030198070": "W4A6TKHJ-IRW_0", "8030202319": "KP8E15N5-IRW_0", "8030202441": "BYU908P5-IRW_0",
    "8030203103": "0LUWCXLE-IRW_0", "8030203201": "F6HQWQ0D-IRW_0", "8030203659": "MLGNKC01-IRW_0",
    "8030203724": "RYZE3VKM-IRW_0", "8030204203": "8467DDA1-IRW_0", "8030204256": "YGWENQAW-IRW_0",
    "8030204943": "E96E4T5Y-IRW_0", "8030205173": "5KZFHO91-IRW_0", "8030205689": "S6EVG3CW-IRW_0",
    "8030205994": "H065GUS2-IRW_0", "8030206212": "U8N5HRE3-IRW_0", "8030206563": "BZIXSR6N-IRW_0",
    "8030206641": "ARRH9F84-IRW_0", "8030206825": "RTRE3XSH-IRW_0", "8030206951": "CADWCFO0-IRW_0",
    "8030207240": "ACX4T2IT-IRW_0", "8030207547": "TRFENIAG-IRW_0", "8030207258": "CRTRMQ8V-IRW_0",
    "8030209309": "YXYYDO1D-IRW_0", "8030210291": "IBSSE5YN-IRW_0", "8030211074": "6HCR8CF8-IRW_0",
    "8030211576": "L47GUDTG-IRW_0", "8030212499": "ASYH32IX-IRW_0", "8030213139": "SYNYZL8Q-IRW_0",
    "8030213665": "YCEKF083-IRW_0", "8030214510": "YDLRIYAH-IRW_0", "8030214792": "522XTOBY-IRW_0",
    "8030215229": "DCRJI8YC-IRW_0", "8030215525": "TVE2A3XD-IRW_0", "8030215768": "E2TCFIJY-IRW_0",
    "8030215949": "VQJQ0W2Y-IRW_0", "8030216067": "407IW9W0-IRW_0", "8030216311": "SSWX2KOZ-IRW_0",
    "8030216421": "8LKN9UXF-IRW_0", "8030217807": "895DXWLC-IRW_0", "8030218870": "6UT0J4J6-IRW_0",
    "8030219157": "JPE4N85T-IRW_0", "8030219629": "I7ASMLE5-IRW_0", "8030220300": "AE0AYRSK-IRW_0",
    "8030220353": "ZDBL3SLL-IRW_0", "8030221248": "WUOEVSLD-IRW_0"
}

bot_accounts = []
last_reload = 0

def reload_accounts():
    global bot_accounts, last_reload
    bot_accounts = []
    items = list(ACCOUNTS_LIST.items())
    if not items:
        return
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(auto_login, uid, pwd): uid for uid, pwd in items}
        for future in as_completed(futures):
            session = future.result()
            if session:
                bot_accounts.append(session)
    last_reload = time.time()

def auto_login(uid, password):
    for _ in range(3):
        try:
            url = f"https://ff-jwt-gen-api.lovable.app/api/public/token?uid={uid}&password={password}"
            res = requests.get(url, timeout=15).json()
            if res.get("token") and res.get("account_id"):
                return {"jwt": res["token"], "account_id": res["account_id"], "server_url": SERVER_ME, "uid": uid}
        except Exception:
            time.sleep(2)
    return None

reload_accounts()

def is_group_enabled(chat_id):
    return chat_id in enabled_groups and chat_id not in BLOCKED_GROUPS

def is_user_vip(user_id):
    u_id_str = str(user_id)
    if u_id_str in vip_users:
        exp_time = datetime.fromisoformat(vip_users[u_id_str]["expire"])
        if datetime.now() < exp_time:
            return True
        else:
            del vip_users[u_id_str]
            save_data()
    return False

# ===== منع دخول الجروبات العشوائية =====
@bot.my_chat_member_handler()
def check_bot_added(message):
    new_status = message.new_chat_member.status
    chat = message.chat
    user = message.from_user
    if new_status in ['member', 'administrator']:
        if user.id != ADMIN_ID:
            try:
                bot.send_message(chat.id, "❌ غير مصرح لك إضافة البوت. البوت خاص بالمالك صاصا.")
                bot.leave_chat(chat.id)
            except Exception:
                pass

# ===== الخاص: رد المالك فقط + أوامر البان وإنشاء الأكواد =====
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_handler(message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        return bot.reply_to(message, "❌ ليس مصرح لك استخدام البوت أو التحدث معه في الخاص. البوت ملك لـ صاصا فقط.")

    text = message.text.strip() if message.text else ""
    
    if text.startswith('/get'):
        try:
            parts = text.split()
            days = int(parts[1])
            max_users = int(parts[2])
            code_name = parts[3].strip()
            
            activation_codes[code_name] = {
                "days": days,
                "max_users": max_users,
                "used_by": []
            }
            save_data()
            return bot.reply_to(message, f"✅ تم إنشاء كود التفعيل الفردي بنجاح!\n🔑 الكود: `{code_name}`\n⏳ المدة: {days} يوم\n👥 الحد الأقصى للأشخاص: {max_users}", parse_mode="Markdown")
        except Exception:
            return bot.reply_to(message, "❌ صيغة خاطئة. استخدم:\n`/get <الأيام> <عدد الأشخاص> <اسم الكود>`\nمثال: `/get 30 5 SASA2026`", parse_mode="Markdown")

    if text.startswith('/ban'):
        try:
            parts = text.split()
            target_id = int(parts[1])
            BANNED_USERS.add(target_id)
            save_data()
            return bot.reply_to(message, f"🚫 تم حظر المستخدم `{target_id}` من استخدام البوت بنجاح.", parse_mode="Markdown")
        except Exception:
            return bot.reply_to(message, "❌ استخدم: `/ban <ID>`")

    if text.startswith('/unban'):
        try:
            parts = text.split()
            target_id = int(parts[1])
            if target_id in BANNED_USERS:
                BANNED_USERS.remove(target_id)
                save_data()
                return bot.reply_to(message, f"✅ تم رفع الحظر عن المستخدم `{target_id}`.", parse_mode="Markdown")
            else:
                return bot.reply_to(message, "⚠️ المستخدم ليس محظوراً أساساً.")
        except Exception:
            return bot.reply_to(message, "❌ استخدم: `/unban <ID>`")

    if text.startswith('/blockgroup'):
        try:
            parts = text.split()
            g_id = int(parts[1])
            BLOCKED_GROUPS.add(g_id)
            save_data()
            return bot.reply_to(message, f"🚫 تم حظر المجموعة `{g_id}` من العمل.", parse_mode="Markdown")
        except Exception:
            return bot.reply_to(message, "❌ استخدم: `/blockgroup <chat_id>`")

    if text.startswith('/unblockgroup'):
        try:
            parts = text.split()
            g_id = int(parts[1])
            if g_id in BLOCKED_GROUPS:
                BLOCKED_GROUPS.remove(g_id)
                save_data()
                return bot.reply_to(message, f"✅ تم رفع الحظر عن المجموعة `{g_id}`.", parse_mode="Markdown")
            else:
                return bot.reply_to(message, "⚠️ المجموعة ليست محظورة.")
        except Exception:
            return bot.reply_to(message, "❌ استخدم: `/unblockgroup <chat_id>`")

    panel_text = (
        f"👑 أهلاً بك يا صاصا في لوحة التحكم الخاصة بك!\n\n"
        f"📋 **أوامر المالك المتاحة في الخاص:**\n"
        f"• `/get <أيام> <عدد الأشخاص> <اسم الكود>` - توليد كود تفعيل للأفراد\n"
        f"• `/ban <ID>` - حظر شخص\n"
        f"• `/unban <ID>` - رفع الحظر عن شخص\n"
        f"• `/blockgroup <chat_id>` - حظر جروب\n"
        f"• `/unblockgroup <chat_id>` - رفع حظر جروب\n"
    )
    bot.reply_to(message, panel_text, parse_mode="Markdown")

# ===== تفعيل الجروب (بواسطة المالك) =====
@bot.message_handler(func=lambda message: message.text and message.text.strip() == "++" and message.chat.type != 'private')
def enable_group_with_plus(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return bot.reply_to(message, "❌ أمر التفعيل مخصص للمالك (صاصا) فقط.")

    enabled_groups.add(message.chat.id)
    if message.chat.id in BLOCKED_GROUPS:
        BLOCKED_GROUPS.remove(message.chat.id)
    save_data()
    bot.reply_to(message, "✅ تم تفعيل المجموعة بواسطة المالك! البوت جاهز للعمل.")

# ===== شحن الكود للشخص: /redeem <CODE> =====
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/redeem') and message.chat.type != 'private')
def redeem_code_handler(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return

    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "❌ استخدم: `/redeem <اسم الكود>`")
    
    code = parts[1].strip()
    if code in activation_codes:
        code_data = activation_codes[code]
        u_id_str = str(user_id)
        
        if u_id_str in code_data["used_by"]:
            return bot.reply_to(message, "⚠️ لقد قمت بتفعيل هذا الكود مسبقاً!")
            
        if len(code_data["used_by"]) >= code_data["max_users"]:
            return bot.reply_to(message, "❌ عذراً، هذا الكود انتهى (استنفد الحد الأقصى للمستخدمين المسموح لهم).")
        
        code_data["used_by"].append(u_id_str)
        days = code_data["days"]
        
        expiry_date = datetime.now() + timedelta(days=days)
        vip_users[u_id_str] = {"expire": expiry_date.isoformat()}
        save_data()
        
        bot.reply_to(message, f"🎉 مبروك! تم تفعيل **السبام اللانهائي الخاص بك** بنجاح لمدة {days} يوم.\n⏳ ينتهي في: {expiry_date.strftime('%Y-%m-%d %H:%M')}")
    else:
        bot.reply_to(message, "❌ الكود غير صحيح أو انتهى.")

# ===== دوال تشفير والسبام =====
def buildpacket(fd):
    pk = bytearray()
    for f, v in fd.items():
        ev = []
        n = (f << 3) | (2 if isinstance(v, (dict, str, bytes)) else 0)
        while True:
            b = n & 0x7F
            n >>= 7
            if n:
                b |= 0x80
            ev.append(b)
            if not n:
                break
        pk.extend(bytes(ev))
        if isinstance(v, int):
            ev2 = []
            while True:
                b = v & 0x7F
                v >>= 7
                if v:
                    b |= 0x80
                ev2.append(b)
                if not v:
                    break
            pk.extend(bytes(ev2))
    return pk

def execute_friend_action(session, target_uid):
    try:
        obb = requests.get("https://version.ffmax.purplevioleto.com/live/ver.php?lang=ar&device=android", timeout=8).json().get("latest_release_version", "2.101.X")
        payload = buildpacket({1: int(session["account_id"]), 2: int(target_uid), 3: 22}).hex()
        key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        enc = bytes.fromhex(AES.new(key, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(payload), 16)).hex())
        headers = {
            "Authorization": f"Bearer {session['jwt']}",
            "ReleaseVersion": obb,
            "X-GA": "v1 1",
            "X-Unity-Version": "2022.3.47f1",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res = requests.post(f"{session['server_url']}RequestAddingFriend", headers=headers, data=enc, timeout=10)
        return res.status_code == 200
    except Exception:
        return False

# ===== إيقاف السبام اللانهائي المخصص: -- <UID> =====
@bot.message_handler(func=lambda message: message.text and message.text.startswith('--') and message.chat.type != 'private')
def stop_infinite_spam_custom(message):
    chat_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "❌ استخدم الصيغة لإيقاف السبام:\n`-- <UID>`\nمثال: `-- 8023713432`", parse_mode="Markdown")
    
    target = parts[1].strip()
    key = (chat_id, target)
    
    if key in active_infinite_spams:
        active_infinite_spams[key].set()
        del active_infinite_spams[key]
        bot.reply_to(message, f"🛑 تم إيقاف السبام اللانهائي للأيدي `{target}` بنجاح.", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ لا يوجد سبام لانهائي يعمل حالياً لهذا الايدي (`{target}`) في هذه المجموعة.", parse_mode="Markdown")

# ===== تنفيذ السبام عبر ++ <UID> في المجموعات المفعلة =====
@bot.message_handler(func=lambda message: message.text and message.text.startswith("++") and message.chat.type != 'private')
def spam_via_plus_plus(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return

    text = message.text.strip()
    parts = text.split()
    
    if len(parts) < 2:
        return

    chat_id = message.chat.id
    if not is_group_enabled(chat_id):
        return bot.reply_to(message, "❌ هذه المجموعة غير مفعلة. يجب أن يقوم المالك (صاصا) بإرسال `++` أولاً.")

    target = parts[1]
    if not target.isdigit() or not bot_accounts:
        return bot.reply_to(message, "❌ خطأ في الـ UID أو الحسابات غير متوفرة.")

    if time.time() - last_reload > 1200:
        reload_accounts()

    # إرسال رسالة "سيتم اضافه اسبام بـ 208 حساب..." كبداية مثل ما طلبت
    msg = bot.reply_to(message, f"🚀 سيتم اضافه اسبام بـ 208 حساب...\n🆔 الايدي: {target}")

    success_count = 0
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(execute_friend_action, acc, target) for acc in bot_accounts]
        for future in as_completed(futures):
            if future.result():
                success_count += 1

    failed_count = len(bot_accounts) - success_count

    # التحقق هل المستخدم VIP (معاه كود دائم)
    if is_user_vip(user_id):
        key = (chat_id, target)
        if key in active_infinite_spams:
            return bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"⚠️ يوجد سبام لانهائي يعمل بالفعل لهذا الايدي ({target}). أرسل `-- {target}` لإيقافه.")
        
        stop_event = threading.Event()
        active_infinite_spams[key] = stop_event
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f"🚀 **بدء السبام اللانهائي الدائم**\n🆔 الايدي: {target}\n📥 الناجح: {success_count} من أصل 100\n(لن يتوقف إلا عندما تكتب: `-- {target}`)",
            parse_mode="Markdown"
        )

        def infinite_loop():
            round_num = 1
            while not stop_event.is_set():
                s_count = 0
                with ThreadPoolExecutor(max_workers=50) as executor:
                    futures = [executor.submit(execute_friend_action, acc, target) for acc in bot_accounts]
                    for future in as_completed(futures):
                        if future.result():
                            s_count += 1
                try:
                    bot.send_message(chat_id, f"🔄 **[الدورة رقم {round_num}]**\n🆔 الايدي: {target}\n📥 الناجح: {s_count} من أصل 100")
                except Exception:
                    pass
                round_num += 1
                for _ in range(10):
                    if stop_event.is_set():
                        break
                    time.sleep(1)

        threading.Thread(target=infinite_loop, daemon=True).start()

    else:
        # الأشخاص العاديين
        if success_count == 0:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ لا يوجد إرسال، صاحب الحساب طلباته مليانة.\n🆔 الايدي: {target}\n📊 الحسابات الناجحة: 0 من أصل 100"
            )
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ انتهى السبام العادي بنجاح!\n🆔 الايدي: {target}\n📥 وصل: {success_count} من أصل 100\n❌ موصلش: {failed_count}"
            )

print("✅ ساسا بوت يعمل بكامل التعديلات والشكل الجمالي المطلوبة...")
bot.infinity_polling()