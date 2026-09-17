#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ NELHUMBLE CPM STORE - ULTIMATE ENGINE ⚡
"""

import requests
import time
import json
import telebot
import random
import base64
import struct
import brotli
import hashlib
import zlib
import threading
import sqlite3
import uuid
import html
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from telebot import types
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════════
# 🌐 FLASK HEALTH SERVER
# ═══════════════════════════════════════════════════════════
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home(): return jsonify({"status": "Humble CPM Store Online"})

@app.route('/health')
def health(): return jsonify({"status": "healthy"})

def run_flask(): app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
threading.Thread(target=run_flask, daemon=True).start()

# ═══════════════════════════════════════════════════════════
# 🎨 NORMAL EMOJIS
# ═══════════════════════════════════════════════════════════
EMOJI = {
    "core_commands": "🚀", "message_router": "🎯", "economy_profile": "💰",
    "account_info": "👤", "unlocks_login": "🔓", "access_granted": "♾️",
    "role": "🎖️", "choose_section": "👇", "refresh": "🔄", "info": "ℹ️",
    "set_name": "✏️", "set_id": "🆔", "email": "📧", "password": "🔒",
    "back": "🔙", "not_logged_in": "🕶️", "create_account": "🆕",
    "terminal_hybrid": "⚡", "encryption": "⚙️", "car_injection": "🎮",
    "money": "💵", "coin": "🪙", "w16_engine": "🛠️", "max_fuel": "⛽",
    "no_damage": "🛡️", "horns": "📯", "animations": "🔥", "all_houses": "🏠",
    "wheels": "🛞", "complete_all_levels": "🏆", "ultimate_glitch": "💀",
    "vehicles": "🚗", "add_admin": "👤", "remove_admin": "🗑️",
    "stats_telemetry": "📈", "broadcast_announcement": "📢", "success": "✅",
    "error": "❌", "warning": "⚠️", "loading": "⏳", "smoke": "💨",
    "request_access": "🔔", "pending": "⏳", "approved": "✅",
    "rejected": "🚫", "admin_panel": "👑", "users": "👥", "lock": "🔒",
}

def E(name): return EMOJI.get(name, "")
def btn(text, callback_data): return types.InlineKeyboardButton(text=text, callback_data=callback_data)

# ═══════════════════════════════════════════════════════════
# 🤖 BOT INIT
# ═══════════════════════════════════════════════════════════
BOT_TOKEN = '8754288681:AAFjdTyUZtp8GdcUYdv2WgBAggqfrEPCzbk'
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=100)

try:
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "⚡ Open Main Terminal"),
        telebot.types.BotCommand("/admin", "👑 Open Overseer Panel")
    ])
except: pass

FK = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"

LOAD_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords3"
SAVE_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/SavePlayerRecordsPartially8"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating5"
MAX_MONEY = 50_000_000
MAX_COIN = 500_000

GAME_HEADERS = {
    "Accept": "*/*", "Accept-Encoding": "gzip", "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

http_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3)
http_session.mount('https://', adapter)
http_session.mount('http://', adapter)

# ═══════════════════════════════════════════════════════════
# 🛡️ SQLITE DATABASE ONLY
# ═══════════════════════════════════════════════════════════
ADMIN_IDS = set()
TRACKED_USERS_CACHE = set()
APPROVED_USERS = {}
PENDING_REQUESTS = set()

db_path = "ashmit_store.db"
with sqlite3.connect(db_path) as c:
    c.execute("CREATE TABLE IF NOT EXISTS approved_users (user_id INTEGER PRIMARY KEY, approved_at REAL, expires_at REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS pending_requests (user_id INTEGER PRIMARY KEY, requested_at REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS tokens (user_id INTEGER PRIMARY KEY, auth_token TEXT, email TEXT, password TEXT, refresh_token TEXT, firebase_uid TEXT, token_expires_at REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS user_data (cache_key TEXT PRIMARY KEY, email TEXT, data_json TEXT, saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS bot_users (user_id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS bot_admins (user_id INTEGER PRIMARY KEY)")
    try: c.execute("ALTER TABLE approved_users ADD COLUMN expires_at REAL")
    except: pass
    c.commit()

with sqlite3.connect(db_path) as c:
    if c.execute("SELECT COUNT(*) FROM bot_admins").fetchone()[0] == 0:
        for aid in [6784382795]:
            c.execute("INSERT OR IGNORE INTO bot_admins (user_id) VALUES (?)", (aid,))
        c.commit()
    for row in c.execute("SELECT user_id FROM bot_admins").fetchall(): ADMIN_IDS.add(row[0])
    for row in c.execute("SELECT user_id FROM bot_users").fetchall(): TRACKED_USERS_CACHE.add(row[0])
    for row in c.execute("SELECT user_id, expires_at FROM approved_users").fetchall(): APPROVED_USERS[row[0]] = row[1] if row[1] else 0
    for row in c.execute("SELECT user_id FROM pending_requests").fetchall(): PENDING_REQUESTS.add(row[0])

# ═══════════════════════════════════════════════════════════
# 👥 USER / ADMIN / APPROVAL MANAGEMENT
# ═══════════════════════════════════════════════════════════
def track_user(user_id):
    if user_id in TRACKED_USERS_CACHE: return
    TRACKED_USERS_CACHE.add(user_id)
    with sqlite3.connect(db_path) as c:
        c.execute("INSERT OR IGNORE INTO bot_users (user_id) VALUES (?)", (user_id,))
        c.commit()

def get_total_users(): return len(TRACKED_USERS_CACHE)
def get_all_tracked_users(): return list(TRACKED_USERS_CACHE)

def is_admin(user_id): return user_id in ADMIN_IDS

def add_admin(user_id):
    ADMIN_IDS.add(user_id)
    with sqlite3.connect(db_path) as c:
        c.execute("INSERT OR IGNORE INTO bot_admins (user_id) VALUES (?)", (user_id,))
        c.commit()
    return True

def remove_admin(user_id):
    ADMIN_IDS.discard(user_id)
    with sqlite3.connect(db_path) as c:
        c.execute("DELETE FROM bot_admins WHERE user_id=?", (user_id,))
        c.commit()
    return True

def get_all_admins(): return list(ADMIN_IDS)

def is_approved(user_id):
    if is_admin(user_id): return True
    exp = APPROVED_USERS.get(user_id)
    if exp is None: return False
    if exp < time.time():
        APPROVED_USERS.pop(user_id, None)
        with sqlite3.connect(db_path) as c:
            c.execute("DELETE FROM approved_users WHERE user_id=?", (user_id,))
            c.commit()
        return False
    return True

def approve_user(user_id, days=1):
    expires_at = time.time() + (days * 86400)
    APPROVED_USERS[user_id] = expires_at
    PENDING_REQUESTS.discard(user_id)
    with sqlite3.connect(db_path) as c:
        c.execute("INSERT OR REPLACE INTO approved_users (user_id, approved_at, expires_at) VALUES (?, ?, ?)", (user_id, time.time(), expires_at))
        c.execute("DELETE FROM pending_requests WHERE user_id=?", (user_id,))
        c.commit()
    return True

def reject_user(user_id):
    PENDING_REQUESTS.discard(user_id)
    APPROVED_USERS.pop(user_id, None)
    with sqlite3.connect(db_path) as c:
        c.execute("DELETE FROM pending_requests WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM approved_users WHERE user_id=?", (user_id,))
        c.commit()
    return True

def add_pending_request(user_id):
    if user_id in PENDING_REQUESTS: return False
    PENDING_REQUESTS.add(user_id)
    with sqlite3.connect(db_path) as c:
        c.execute("INSERT OR REPLACE INTO pending_requests (user_id, requested_at) VALUES (?, ?)", (user_id, time.time()))
        c.commit()
    return True

def get_all_pending(): return list(PENDING_REQUESTS)

# ═══════════════════════════════════════════════════════════
# ⚙️ ENCRYPTION & SERIALIZATION
# ═══════════════════════════════════════════════════════════
def clean_str(text):
    if not text: return "Unknown"
    return str(text).replace('_', '-').replace('*', '•').replace('`', "'").replace('[', '(').replace(']', ')')

def make_xor_key(uid: str) -> bytes:
    chars = list(str(uid or ""))
    if len(chars) >= 9: chars[1], chars[8] = chars[8], chars[1]
    if len(chars) >= 3: chars.pop(2)
    if len(chars) >= 5: chars.append(chars[4])
    return "".join(chars).encode("utf-8") or b"0"

def xor_bytes(data: bytes, key: bytes) -> bytes: return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def decompress(data: bytes):
    try: return brotli.decompress(data)
    except: pass
    for args in ((zlib.MAX_WBITS | 16,), tuple()):
        try: return zlib.decompress(data, *args)
        except: pass
    return None

def decrypt_aes(data: bytes, key: bytes):
    try: return unpad(AES.new(key[:16], AES.MODE_CBC, b"\x00" * 16).decrypt(data), 16)
    except: return None

def _md5(text: str) -> bytes: return hashlib.md5(str(text).encode()).digest()
def _sha1(text: str) -> bytes: return hashlib.sha1(str(text).encode()).digest()[:16]
def build_aes_keys(uid: str, password: str = None, email: str = None) -> list:
    keys = [_md5("olzhas_carparking")]
    if password: keys.extend([_md5(password), _sha1(password)])
    if uid: keys.extend([_md5(uid), _sha1(uid)])
    if email: keys.append(_md5(email))
    return keys

class Reader:
    def __init__(self, data: bytes): self.buf, self.pos = data, 0
    def has_bytes(self, n: int) -> bool: return self.pos + n <= len(self.buf)
    def read_byte(self) -> int:
        if not self.has_bytes(1): return 0
        v = self.buf[self.pos]; self.pos += 1; return v
    def read_int(self) -> int:
        if not self.has_bytes(4): self.pos = len(self.buf); return 0
        v = struct.unpack_from("<i", self.buf, self.pos)[0]; self.pos += 4; return v
    def read_float(self) -> float:
        if not self.has_bytes(4): self.pos = len(self.buf); return 0.0
        v = struct.unpack_from("<f", self.buf, self.pos)[0]; self.pos += 4; return v
    def read_string(self) -> str:
        marker = self.read_int()
        if marker in (0, -1): return ""
        length = (-marker) - 1 if marker < -1 else marker
        if marker < -1: self.read_int()
        length = max(0, min(length, 1000000))
        if not self.has_bytes(length): return ""
        text = self.buf[self.pos:self.pos + length].decode("utf-8", errors="replace")
        self.pos += length
        return text.replace("\x00", "").strip()
    def read_list(self, item_fn):
        count = self.read_int()
        if count <= 0 or count > 1000000: return []
        res = []
        for _ in range(count):
            if self.pos >= len(self.buf): break
            val = item_fn()
            if val is not None: res.append(val)
        return res
    def read_dict(self) -> dict:
        count = self.read_int()
        if count <= 0 or count > 1000000: return {}
        return {self.read_int(): self.read_int() for _ in range(count) if self.pos < len(self.buf)}
    def read_equipment(self):
        if self.read_byte() == 0: return None
        return {k: self.read_list(self.read_int) for k in ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]} | {"Gender": self.read_int()}

def parse_player(buf: bytes) -> dict:
    r = Reader(buf)
    if r.read_byte() == 0: return None
    player = {"Name": r.read_string(), "money": r.read_int(), "coin": r.read_int(), "localID": r.read_string(), "boughtFsos": r.read_list(r.read_int)}
    player["FriendsID"] = r.read_list(lambda: (r.read_byte(), {"id": r.read_string(), "Name": r.read_string(), "accountID": r.read_string()})[1])
    player.update({"LevelsDoneTime": r.read_list(r.read_float), "floats": r.read_list(r.read_float), "integers": r.read_list(r.read_int), "fcar": r.read_list(r.read_int), "favouriteWheels": r.read_list(r.read_int), "favouriteVinyls": r.read_list(r.read_int), "favouriteEmojis": r.read_list(r.read_int), "personEquipmentsMale": r.read_equipment(), "personEquipmentsFemale": r.read_equipment()})
    if r.read_byte() == 0: player["platesData"] = None
    else:
        def read_vinyl(): r.read_byte(); return {"vectors": r.read_list(lambda: {"x": r.read_float(), "y": r.read_float(), "z": r.read_float()}), "v": r.read_list(r.read_string), "floats": r.read_list(r.read_float), "text": r.read_string()}
        def read_plate(): r.read_byte(); return {"plateId": r.read_int(), "frontCarId": r.read_int(), "rearCarId": r.read_int(), "vinyls": r.read_list(read_vinyl)}
        player["platesData"] = {"allPlates": r.read_list(read_plate)}

    if r.read_byte() == 0: player["carIDnStatus"] = None
    else: player["carIDnStatus"] = {"carGeneratedIDs": r.read_list(r.read_string), "carStatus": r.read_list(r.read_int)}
    
    player["allData"] = r.read_string()
    player["flags"] = r.read_dict()
    player["animations"] = r.read_list(r.read_int)
    player["emojiPacks"] = r.read_list(r.read_int)
    player["wheels"] = r.read_list(r.read_int)
    player["boughtPoliceLights"] = r.read_list(r.read_int)
    player["boughtPoliceSirens"] = r.read_list(r.read_int)
    return player

def try_parse(buf: bytes) -> dict:
    candidates = [buf, decompress(buf)]
    if candidates[1]: candidates.append(decompress(candidates[1]))
    for candidate in filter(None, candidates):
        if candidate[0] in (17, 23, 24):
            try:
                p = parse_player(candidate)
                if p and p.get("Name") is not None: return p
            except: pass
        try:
            clean = candidate[3:] if len(candidate) >= 3 and candidate[:2] == b"\xef\xbb" else candidate
            if clean and clean[0] == 123: return json.loads(clean.decode("utf-8"))
        except: pass
    return None

def decrypt_player_record(base64_text: str, uid: str, password: str = None, email: str = None) -> dict:
    try: buf = base64.b64decode(base64_text)
    except: return {"success": False, "message": "Bad base64"}
    if len(buf) < 10: return {"success": False, "message": "Too small"}
    direct = try_parse(buf)
    if direct: return {"success": True, "record": direct}
    if uid:
        try:
            decoded = decompress(xor_bytes(buf, make_xor_key(uid)))
            if decoded:
                parsed = try_parse(decoded)
                if parsed: return {"success": True, "record": parsed}
        except: pass
    for key in build_aes_keys(uid or "", password, email):
        plain = decrypt_aes(buf, key)
        if not plain: continue
        parsed = try_parse(plain)
        if parsed: return {"success": True, "record": parsed}
    return {"success": False, "message": "Could not decrypt"}

class Writer:
    def __init__(self): self._p: List[bytes] = []
    def write_byte(self, v): self._p.append(bytes([int(v or 0) & 0xFF]))
    def write_int(self, v): self._p.append(struct.pack("<i", int(v or 0)))
    def write_float(self, v): self._p.append(struct.pack("<f", float(v or 0.0)))
    def write_string(self, s):
        if s is None: self._p.append(struct.pack("<i", -1)); return
        s = str(s)
        if s == "": self._p.append(struct.pack("<i", 0)); return
        enc = s.encode("utf-8")
        self._p.append(struct.pack("<ii", -(len(enc)) - 1, len(s)) + enc)
    def write_list(self, lst, fn):
        if lst is None: self._p.append(struct.pack("<i", -1)); return
        self._p.append(struct.pack("<i", len(lst)))
        for item in lst: fn(item)
    def write_equipment(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(13)
        for key in ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]:
            self.write_list(data.get(key, []), self.write_int)
        self.write_int(data.get("Gender", 0))
    def write_plates(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(1)
        plates = data.get("allPlates", [])
        self._p.append(struct.pack("<i", len(plates)))
        for plate in plates:
            self.write_byte(4); self.write_int(plate.get("plateId", 0)); self.write_int(plate.get("frontCarId", 0)); self.write_int(plate.get("rearCarId", 0))
            vinyls = plate.get("vinyls", [])
            self._p.append(struct.pack("<i", len(vinyls)))
            for vinyl in vinyls:
                self.write_byte(4)
                vecs = vinyl.get("vectors", [])
                self._p.append(struct.pack("<i", len(vecs)))
                for vec in vecs: self._p.append(struct.pack("<fff", vec.get("x", 0), vec.get("y", 0), vec.get("z", 0)))
                self.write_list(vinyl.get("v", []), self.write_string)
                self.write_list(vinyl.get("floats", []), self.write_float)
                self.write_string(vinyl.get("text", ""))
    def write_car_id_status(self, data):
        if not data: self.write_byte(0); return
        self.write_byte(2)
        self.write_list(data.get("carGeneratedIDs", []), self.write_string)
        self.write_list(data.get("carStatus", []), self.write_int)
    def to_bytes(self): return b"".join(self._p)

FIELD_MAPPING = [(1, "localID"), (2, "money"), (3, "Name"), (4, "coin"), (5, "allData"), (6, "boughtFsos"), (7, "boughtPoliceLights"), (8, "boughtPoliceSirens"), (9, "FriendsID"), (10, "LevelsDoneTime"), (11, "floats"), (12, "integers"), (13, "fcar"), (14, "favouriteWheels"), (15, "favouriteVinyls"), (16, "favouriteEmojis"), (18, "emojiPacks"), (41, "personEquipmentsMale"), (42, "personEquipmentsFemale"), (43, "platesData"), (44, "carIDnStatus"), (45, "flags"), (46, "animations"), (48, "wheels")]
INT_LIST_FIELDS = {6, 7, 8, 12, 13, 14, 15, 16, 18, 46, 48}
FLOAT_LIST_FIELDS = {10, 11}

def _field_modified(new_value, old_value) -> bool:
    if new_value is None and old_value is None: return False
    if new_value is None or old_value is None: return True
    if type(new_value) != type(old_value): return True
    if isinstance(new_value, (dict, list)): return json.dumps(new_value, sort_keys=True) != json.dumps(old_value, sort_keys=True)
    return new_value != old_value

def serialize_field(fid: int, value: Any) -> Optional[bytes]:
    w = Writer()
    if fid in (1, 3, 5): w.write_string(value); return w.to_bytes()
    if fid in (2, 4): w.write_int(value or 0); return w.to_bytes()
    if fid == 9:
        friends = value or []
        w._p.append(struct.pack("<i", len(friends)))
        for friend in friends: w.write_byte(3); w.write_string(friend.get("id", "")); w.write_string(friend.get("Name", "")); w.write_string(friend.get("accountID", ""))
        return w.to_bytes()
    if fid in INT_LIST_FIELDS: w.write_list(value or [], w.write_int); return w.to_bytes()
    if fid in FLOAT_LIST_FIELDS: w.write_list(value or [], w.write_float); return w.to_bytes()
    if fid in (41, 42): w.write_equipment(value); return w.to_bytes()
    if fid == 43: w.write_plates(value); return w.to_bytes()
    if fid == 44: w.write_car_id_status(value); return w.to_bytes()
    if fid == 45:
        w._p.append(struct.pack("<i", len(value or {})))
        for key, val in (value or {}).items(): w.write_int(int(key)); w.write_int(int(val))
        return w.to_bytes()
    return None

def build_payload(record: Dict[str, Any], uid: str, original: Optional[Dict[str, Any]] = None, force_fields: Optional[set] = None) -> str:
    force_fields = set(force_fields or [])
    fields = []
    for fid, key in FIELD_MAPPING:
        value = record.get(key)
        if value is None: continue
        if key == "allData": should_send = isinstance(value, str) and len(value) > 0
        elif key in force_fields: should_send = True
        elif original is not None: should_send = _field_modified(value, original.get(key))
        else: should_send = True
        if not should_send: continue
        raw = serialize_field(fid, value)
        if raw is not None: fields.append((fid, raw))
    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields: parts.extend([struct.pack("<hi", fid, len(raw)), raw])
    combined = b"".join(parts)
    compressed = brotli.compress(combined)
    encrypted = xor_bytes(compressed, make_xor_key(uid))
    return base64.b64encode(encrypted).decode("ascii")

# ═══════════════════════════════════════════════════════════
# ⚙️ SYNCHRONOUS BACKEND
# ═══════════════════════════════════════════════════════════
class SyncCPMNuker:
    def __init__(self): self.cache = {}

    def _ck(self, uid: int, email: Optional[str] = None) -> str:
        td = self.get_token_data(uid)
        return f"{uid}_{email or (td.get('email') if td else '')}"

    def save_token(self, uid: int, auth: str, email: str, pw: Optional[str] = None, rt: Optional[str] = None, fuid: Optional[str] = None):
        with sqlite3.connect(db_path) as c:
            c.execute("INSERT OR REPLACE INTO tokens (user_id, auth_token, email, password, refresh_token, firebase_uid, token_expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (uid, auth, email, pw, rt, fuid, time.time() + 3600))
            c.commit()

    def get_token_data(self, uid: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(db_path) as c:
            row = c.execute("SELECT auth_token, email, password, refresh_token, firebase_uid, token_expires_at FROM tokens WHERE user_id=?", (uid,)).fetchone()
        if not row: return None
        return {"auth_token": row[0], "email": row[1], "password": row[2], "refresh_token": row[3], "firebase_uid": row[4], "token_expires_at": row[5]}

    def update_token(self, uid: int, auth: str, rt: Optional[str] = None):
        with sqlite3.connect(db_path) as c:
            if rt: c.execute("UPDATE tokens SET auth_token=?, refresh_token=?, token_expires_at=? WHERE user_id=?", (auth, rt, time.time() + 3600, uid))
            else: c.execute("UPDATE tokens SET auth_token=?, token_expires_at=? WHERE user_id=?", (auth, time.time() + 3600, uid))
            c.commit()

    def delete_token(self, uid: int):
        with sqlite3.connect(db_path) as c:
            c.execute("DELETE FROM tokens WHERE user_id=?", (uid,))
            c.commit()
        for key in list(self.cache.keys()):
            if key.startswith(str(uid)): del self.cache[key]

    def is_expired(self, uid: int) -> bool:
        td = self.get_token_data(uid)
        return not td or not td.get("token_expires_at") or td.get("token_expires_at") < time.time()

    def get_record(self, uid: int, email: Optional[str] = None) -> Dict[str, Any]:
        ck = self._ck(uid, email)
        if ck not in self.cache:
            with sqlite3.connect(db_path) as c:
                row = c.execute("SELECT data_json FROM user_data WHERE cache_key=?", (ck,)).fetchone()
            if row:
                try: self.cache[ck] = json.loads(row[0])
                except: pass
        return self.cache.get(ck, {})

    def set_record(self, uid: int, data: Dict[str, Any], email: Optional[str] = None):
        ck = self._ck(uid, email)
        self.cache[ck] = data
        with sqlite3.connect(db_path) as c:
            c.execute("INSERT OR REPLACE INTO user_data (cache_key, email, data_json) VALUES (?, ?, ?)", (ck, email, json.dumps(data)))
            c.commit()

    def _post(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        try:
            clean_headers = {k: v for k, v in headers.items() if k.lower() != "host"}
            resp = http_session.post(url, json=payload, headers=clean_headers, timeout=15)
            try: return resp.json()
            except: return {"raw": resp.text, "status": resp.status_code, "ok": False}
        except Exception:
            return {"ok": False, "message": "CONNECTION FAILED."}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        result = self._post(url, payload, GAME_HEADERS)
        if result.get("ok") is False: return result
        if "idToken" in result: return {"ok": True, "message": "OK", "auth": result["idToken"], "refresh_token": result.get("refreshToken", ""), "firebase_uid": result.get("localId", "")}
        err = "INVALID_CREDENTIALS"
        try:
            if isinstance(result.get("error"), dict): err = str(result["error"].get("message", "INVALID_CREDENTIALS"))
            elif isinstance(result.get("error"), str): err = result["error"]
        except: pass
        return {"ok": False, "message": err.upper()[:80]}

    def register(self, email: str, password: str) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FK}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        result = self._post(url, payload, GAME_HEADERS)
        if result.get("ok") is False: return result
        if "idToken" in result: return {"ok": True, "message": "OK", "auth": result["idToken"], "refresh_token": result.get("refreshToken", ""), "firebase_uid": result.get("localId", "")}
        err = "REGISTRATION_FAILED"
        try:
            if isinstance(result.get("error"), dict): err = str(result["error"].get("message", "FAILED"))
            elif isinstance(result.get("error"), str): err = result["error"]
        except: pass
        return {"ok": False, "message": err.upper()[:80]}

    def _refresh(self, uid: int) -> Tuple[bool, str]:
        td = self.get_token_data(uid)
        if not td: return False, "NO_TOKEN"
        rt, em, pw = td.get("refresh_token"), td.get("email"), td.get("password")
        if rt:
            res = self._post(f"https://securetoken.googleapis.com/v1/token?key={FK}", {"grant_type": "refresh_token", "refresh_token": rt}, {"Content-Type": "application/json"})
            if res.get("id_token"):
                self.update_token(uid, res["id_token"], res.get("refresh_token", rt))
                return True, "OK"
        if em and pw:
            res = self.login(em, pw)
            if res.get("ok"):
                self.save_token(uid, res["auth"], em, pw, res.get("refresh_token", ""), res.get("firebase_uid", ""))
                return True, "OK"
        return False, "REFRESH_FAILED"

    def get_auth(self, uid: int) -> Tuple[bool, str, str]:
        if self.is_expired(uid):
            ok, msg = self._refresh(uid)
            if not ok: return False, msg, ""
        td = self.get_token_data(uid)
        if td and td.get("auth_token"): return True, "OK", td.get("auth_token")
        return False, "NO_TOKEN", ""

    def load(self, uid: int, force: bool = False) -> bool:
        td = self.get_token_data(uid)
        if not td: return False
        if not force and self._ck(uid) in self.cache: return True
        ok, msg, auth = self.get_auth(uid)
        if not ok: return False
        res = self._post(LOAD_URL, {"data": None}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}"})
        if res.get("ok") is False or not res.get("result"): return False
        dec = decrypt_player_record(res["result"], td.get("firebase_uid", ""), td.get("password", ""), td.get("email", ""))
        if dec.get("success") and dec.get("record"):
            self.set_record(uid, dec["record"], td.get("email", ""))
            return True
        return False

    def _ok(self, value: Any) -> bool:
        if value in (1, True, "1"): return True
        if value in (0, False, None, "0"): return False
        if isinstance(value, str):
            try: return self._ok(json.loads(value.strip()))
            except: return False
        if isinstance(value, dict):
            for k in ("result", "ok", "success"):
                if k in value: return self._ok(value[k])
        return False

    def _send(self, auth: str, record: Dict[str, Any], fuid: str, original: Optional[Dict[str, Any]] = None, force_fields: Optional[set] = None) -> Tuple[bool, str]:
        if not fuid: return False, "NO_FIREBASE_UID"
        try:
            payload = build_payload(record, fuid, original, force_fields=force_fields)
            res = self._post(SAVE_URL, {"data": {"data": payload, "deviceId": fuid[:8]}}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}", "Connection": "Keep-Alive", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)"})
            if res.get("ok") is False: return False, res.get("message", "API TIMEOUT")
            if res and self._ok(res): return True, "OK"
            return False, "SAVE-FAILED"
        except Exception as e: return False, str(e)

    def _save(self, uid: int, data: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        ok, msg, auth = self.get_auth(uid)
        if not ok: return {"ok": False, "message": msg}
        td = self.get_token_data(uid)
        fuid = td.get("firebase_uid", "") if td else ""
        email = td.get("email", "") if td else ""
        original = self.get_record(uid, email) or None
        ok2, msg2 = self._send(auth, data, fuid, original, force_fields=force_fields)
        if ok2:
            self.set_record(uid, data, email)
            return {"ok": True, "message": "OK"}
        return {"ok": False, "message": msg2}

    def _modify(self, uid: int, mods: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        if not self.load(uid): return {"ok": False, "message": "ACCOUNT LOAD FAILED. CHECK CREDENTIALS."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        if not data or data.get("Name") is None: return {"ok": False, "message": "PROFILE DATA CORRUPTED."}
        for k, v in mods.items():
            if k == "money": v = min(int(v), MAX_MONEY)
            if k == "coin": v = min(int(v), MAX_COIN)
            data[k] = v
        return self._save(uid, data, force_fields=set(force_fields or mods.keys()))

    def _set_floats(self, uid: int, indices_values: List[Tuple[int, float]]) -> Dict[str, Any]:
        if not self.load(uid): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        if not data or data.get("Name") is None: return {"ok": False, "message": "PROFILE DATA CORRUPTED."}
        floats = data.get("floats", [])
        max_idx = max(idx for idx, _ in indices_values)
        while len(floats) <= max_idx: floats.append(0.0)
        for idx, val in indices_values: floats[idx] = float(val)
        data["floats"] = floats
        return self._save(uid, data, force_fields={"floats"})

    def _set_integers(self, uid: int, indices_values: List[Tuple[int, int]]) -> Dict[str, Any]:
        if not self.load(uid): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        if not data or data.get("Name") is None: return {"ok": False, "message": "PROFILE DATA CORRUPTED."}
        integers = data.get("integers", [])
        max_idx = max(idx for idx, _ in indices_values)
        while len(integers) <= max_idx: integers.append(0)
        for idx, val in indices_values: integers[idx] = int(val)
        data["integers"] = integers
        return self._save(uid, data, force_fields={"integers"})

    def set_money(self, uid: int, amount: int) -> Dict[str, Any]: return self._modify(uid, {"money": min(int(amount), MAX_MONEY)}, force_fields={"money"})
    def set_coin(self, uid: int, amount: int) -> Dict[str, Any]: return self._modify(uid, {"coin": min(int(amount), MAX_COIN)}, force_fields={"coin"})

    def change_player_id(self, uid: int, new_id: str) -> Dict[str, Any]:
        if not self.load(uid, force=True): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        if not data or data.get("Name") is None: return {"ok": False, "message": "PROFILE DATA CORRUPTED."}
        new_id_upper = str(new_id).strip().upper()
        data["localID"] = new_id_upper
        result = self._save(uid, data, force_fields={"localID"})
        if result.get("ok"): return {"ok": True, "message": f"TAG MASKED TO {new_id_upper}", "new_id": new_id_upper}
        return {"ok": False, "message": result.get("message", "SAVE FAILED")}

    def change_player_name(self, uid: int, new_name: str) -> Dict[str, Any]:
        if not self.load(uid, force=True): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        data["Name"] = new_name
        return self._save(uid, data, force_fields={"Name"})

    def change_email(self, uid: int, new_email: str) -> Dict[str, Any]:
        td = self.get_token_data(uid)
        if not td: return {"ok": False, "message": "Not logged in"}
        return {"ok": True, "message": "OK"}

    def unlock_w16(self, uid: int) -> Dict[str, Any]: return self._set_floats(uid, [(32, 1.0)])
    def unlock_horns(self, uid: int) -> Dict[str, Any]: return self._set_floats(uid, [(27, 1.0), (28, 1.0), (29, 1.0), (30, 1.0), (31, 1.0)])
    def disable_damage(self, uid: int) -> Dict[str, Any]: return self._set_floats(uid, [(34, 1.0)])
    def unlimited_fuel(self, uid: int) -> Dict[str, Any]: return self._set_floats(uid, [(3, 1.0)])
    def unlock_smoke(self, uid: int) -> Dict[str, Any]: return self._set_floats(uid, [(33, 1.0)])

    def unlock_animations(self, uid: int) -> Dict[str, Any]:
        if not self.load(uid): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        data["animations"] = sorted(set(data.get("animations", []) + list(range(301))))
        return self._save(uid, data, force_fields={"animations"})

    def unlock_wheels(self, uid: int) -> Dict[str, Any]:
        if not self.load(uid): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        data["wheels"] = sorted(set(data.get("wheels", []) + list(range(73, 221))))
        integers = data.get("integers", [])
        while len(integers) < 113: integers.append(0)
        for idx in [0, 1, 2, 3, 4, 5, 110, 111, 112]: integers[idx] = 1
        data["integers"] = integers
        return self._save(uid, data, force_fields={"wheels", "integers"})

    def unlock_houses(self, uid: int) -> Dict[str, Any]: return self._set_integers(uid, [(8, 1), (110, 1), (111, 1), (112, 1)])
    def complete_all_levels(self, uid: int) -> Dict[str, Any]: return self._modify(uid, {"LevelsDoneTime": [0] + [120 if i == 43 else 1 for i in range(1, 110)]}, force_fields={"LevelsDoneTime"})

    def set_rank(self, uid: int) -> Dict[str, Any]:
        self.load(uid)
        ok, msg, auth = self.get_auth(uid)
        if not ok: return {"ok": True, "message": "OK"}
        rating_data = {"RatingData": {"time": 1e22, "cars": 1e16, "car_fix": 1e13, "car_collided": 1e12, "car_exchange": 1e13, "car_trade": 1e13, "car_wash": 1e13, "slicer_cut": 1e13, "drift_max": 1e14, "drift": 1e14, "cargo": 1e5, "delivery": 1e5, "race_win": 3e20, "taxi": 1e10, "levels": 10000990000, "gifts": 1e9, "fuel": 1e10, "offroad": 1e10, "speed_banner": 1e9, "reactions": 1e17, "run": 1e9, "real_estate": 1e9, "t_distance": 1e10, "treasure": 1e10, "block_post": 1e10, "push_ups": 1e12, "burnt_tire": 1e10, "passanger_distance": 1e8}}
        try: self._post(RANK_URL, {"data": json.dumps(rating_data)}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}"})
        except: pass
        return {"ok": True, "message": "OK"}

    def unlock_all_features(self, uid: int) -> Dict[str, Any]:
        feature_calls = [("W16 Engine", self.unlock_w16), ("Horns", self.unlock_horns), ("No Damage", self.disable_damage), ("Unlimited Fuel", self.unlimited_fuel), ("Smoke", self.unlock_smoke), ("Animations", self.unlock_animations), ("Wheels", self.unlock_wheels), ("Houses", self.unlock_houses), ("All Levels", self.complete_all_levels), ("Max Rank", self.set_rank)]
        if not self.load(uid, force=True): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        results, failed = [], []
        for name, fn in feature_calls:
            res = fn(uid)
            if res.get("ok"): results.append(name)
            else: failed.append(f"{name}: {res.get('message', 'Failed')}")
        return {"ok": not failed, "message": f"Unlocked {len(results)}/{len(feature_calls)} features"}

    def fix_account(self, uid: int) -> Dict[str, Any]:
        if not self.load(uid, force=True): return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        data = deepcopy(self.get_record(uid, td.get("email") if td else None))
        if data.get("money", 0) > MAX_MONEY: data["money"] = MAX_MONEY
        if data.get("coin", 0) > MAX_COIN: data["coin"] = MAX_COIN
        flags = data.get("flags", {})
        if isinstance(flags, dict):
            for bad_flag in [0, 1, 2, "0", "1", "2"]:
                flags.pop(bad_flag, None)
            data["flags"] = flags
        return self._save(uid, data, force_fields={"money", "coin", "flags"})

    def get_account_info(self, uid: int, force_refresh: bool = False) -> Dict[str, Any]:
        if not self.load(uid, force=force_refresh): return {"ok": False}
        td = self.get_token_data(uid)
        if not td: return {"ok": False}
        data = self.get_record(uid, td.get("email"))
        if not data or data.get("Name") is None: return {"ok": False}
        cars_count = 0
        try:
            c_status = data.get('carIDnStatus')
            if isinstance(c_status, dict):
                c_list = c_status.get('carStatus', [])
                if isinstance(c_list, list): cars_count = len(c_list)
        except: pass
        if cars_count == 0:
            try:
                ad = data.get('allData', '{}')
                if isinstance(ad, str):
                    ad_json = json.loads(ad)
                    if isinstance(ad_json, dict):
                        cars_count = len(ad_json.get('cars', []))
            except: pass
        return {"ok": True, "name": data.get("Name", "Unknown"), "money": data.get("money", 0), "coin": data.get("coin", 0), "localID": data.get("localID", "Unknown"), "email": td.get("email"), "cars": cars_count}

    def clone_account(self, target_uid: int, master_email: str, master_pass: str) -> Dict[str, Any]:
        """Clones money, coins, cars, vinyls, rank/levels, equipment, etc., from master_email to target_uid."""
        # 1. Master Account load aur decrypt karein
        master_auth_res = self.login(master_email, master_pass)
        if not master_auth_res.get("ok"):
            return {"ok": False, "message": f"MASTER LOGIN FAILED: {master_auth_res.get('message', 'INVALID CREDENTIALS')}"}
        
        m_auth = master_auth_res.get("auth")
        m_fuid = master_auth_res.get("firebase_uid")
        
        res = self._post(LOAD_URL, {"data": None}, {**GAME_HEADERS, "Authorization": f"Bearer {m_auth}"})
        if not res.get("ok") or not res.get("result"):
            return {"ok": False, "message": "FAILED TO LOAD MASTER ACCOUNT DATA"}
            
        m_dec = decrypt_player_record(res["result"], m_fuid, master_pass, master_email)
        if not m_dec.get("success") or not m_dec.get("record"):
            return {"ok": False, "message": "FAILED TO DECRYPT MASTER ACCOUNT"}
            
        master_data = m_dec["record"]
        
        # 2. Target Account load karein
        if not self.load(target_uid, force=True):
            return {"ok": False, "message": "TARGET ACCOUNT LOAD FAILED"}
            
        target_td = self.get_token_data(target_uid)
        target_email = target_td.get("email") if target_td else None
        target_data = deepcopy(self.get_record(target_uid, target_email))
        
        if not target_data or target_data.get("Name") is None:
            return {"ok": False, "message": "TARGET PROFILE DATA CORRUPTED"}
            
        # 3. Master account ka data Target pe copy karein
        clone_keys = [
            "money", "coin", "allData", "boughtFsos", "boughtPoliceLights", "boughtPoliceSirens",
            "LevelsDoneTime", "floats", "integers", "fcar", "favouriteWheels", "favouriteVinyls",
            "favouriteEmojis", "emojiPacks", "personEquipmentsMale", "personEquipmentsFemale",
            "platesData", "carIDnStatus", "flags", "animations", "wheels"
        ]
        
        for key in clone_keys:
            if key in master_data:
                target_data[key] = deepcopy(master_data[key])
                
        target_data["money"] = min(int(target_data.get("money", 0)), MAX_MONEY)
        target_data["coin"] = min(int(target_data.get("coin", 0)), MAX_COIN)

        # 4. Save cloned data
        save_res = self._save(target_uid, target_data, force_fields=set(clone_keys))
        if not save_res.get("ok"):
            return save_res
            
                # 5. King Rank apply karein
        self.set_rank(target_uid)

        return {"ok": True, "message": "ACCOUNT CLONED SUCCESSFULLY"}


nuker = SyncCPMNuker()



# ═══════════════════════════════════════════════════════════
# 🤖 BOT STATE


# ═══════════════════════════════════════════════════════════
# 🤖 BOT STATE
# ═══════════════════════════════════════════════════════════
user_sessions, user_states = {}, {}

def get_web_uid(telegram_id):
    return int(str(telegram_id)[:12])

# ═══════════════════════════════════════════════════════════
# 🎛️ KEYBOARDS
# ═══════════════════════════════════════════════════════════
def cancel_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(btn("❌ Cancel", "menu_main"))
    return markup

def create_dashboard_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(btn("👤 Account", "menu_account"), btn("💰 Economy", "menu_economy"))
    markup.row(btn("🔓 Unlocks", "menu_unlocks"))
    if is_admin(chat_id):
        markup.row(btn("👑 OVERSEER PANEL", "admin_panel"))
    markup.row(btn("🔄 Refresh", "refresh_account"), btn("🔙 Logout", "logout"))
    return markup

def create_account_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(btn("ℹ️ Info", "acc_info"), btn("✏️ Set Name", "acc_name"))
    markup.row(btn("🆔 Set ID", "acc_id"), btn("📧 Change Email", "acc_email"))
    markup.row(btn("🔒 Change Pass", "acc_pass"))
    markup.add(btn("🔙 Back", "menu_main"))
    return markup

def create_economy_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(btn("💵 Money 50M", "eco_money_max"), btn("🪙 Coins 500K", "eco_coins_max"))
    markup.row(btn("💵 Custom Money", "eco_money_cust"), btn("🪙 Custom Coins", "eco_coins_cust"))
    markup.row(btn("👑 King Rank", "eco_king"))
    markup.add(btn("🔙 Back", "menu_main"))
    return markup

def create_unlocks_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(btn("🛠️ W16 Engine", "unl_w16"), btn("💨 Smoke", "unl_smoke"))
    markup.row(btn("⛽ Max Fuel", "unl_fuel"), btn("🛡️ No Damage", "unl_damage"))
    markup.row(btn("📯 Horns", "unl_horns"), btn("🔥 Animations", "unl_anim"))
    markup.row(btn("🏠 All Houses", "unl_houses"), btn("🛞 Wheels", "unl_wheels"))
    markup.row(btn("🏆 Complete All Levels", "unl_levels"))
    markup.row(btn("👥 Clone Account", "unl_clone"))
    markup.row(btn("💀 ULTIMATE GLITCH", "unl_ultimate"))
    markup.add(btn("🔙 Back", "menu_main"))
    return markup

def create_admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(btn("👤 Add Admin", "admin_add_admin"), btn("🗑️ Remove Admin", "admin_rem_admin"))
    markup.row(btn("👥 View Admins", "admin_view_admins"), btn("📋 View Requests", "admin_view_requests"))
    markup.row(btn("📈 Stats", "admin_stats"), btn("📢 Broadcast", "admin_broadcast"))
    markup.add(btn("🔙 Back", "menu_main"))
    return markup

# ═══════════════════════════════════════════════════════════
# 🖥️ DASHBOARD
# ═══════════════════════════════════════════════════════════
def safe_send_dashboard(chat_id, custom_top_msg=None, force_refresh=False, is_callback=False, message_id=None):
    try:
        if not is_approved(chat_id):
            if chat_id in PENDING_REQUESTS:
                msg = f"{E('pending')} <b>Access Pending</b>\n\nYour request has been sent to admins. Please wait for approval."
                markup = types.InlineKeyboardMarkup()
                markup.add(btn("🔄 Refresh", "menu_main"))
            else:
                msg = f"{E('lock')} <b>Access Restricted</b>\n\nYou need to request access to use <b>Ashmit's CPM Store</b>."
                markup = types.InlineKeyboardMarkup()
                markup.add(btn("🔔 Request Access", "request_access"))

            if is_callback and message_id:
                try: bot.edit_message_text(msg, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
                except: bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            return

        session_data = user_sessions.get(chat_id, {})
        is_logged_in = session_data.get('cpm_logged_in', False)

        if not is_logged_in:
            msg = f"{E('not_logged_in')} <b>Not logged in</b> — tap Login or Register to get started."
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.row(btn("🔓 Login", "init_login"), btn("🆕 Register", "init_register"))

            if is_callback and message_id:
                try: bot.edit_message_text(msg, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
                except: bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            return

        web_uid = get_web_uid(chat_id)
        info = nuker.get_account_info(web_uid, force_refresh=force_refresh)

        if not info.get("ok"):
            user_sessions[chat_id]['cpm_logged_in'] = False
            msg = f"{E('error')} <b>Session Expired or Load Failed.</b> Please Login again."
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.row(btn("🔓 Login", "init_login"), btn("🆕 Register", "init_register"))

            if is_callback and message_id:
                try: bot.edit_message_text(msg, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
                except: bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="HTML")
            return

        if is_admin(chat_id):
            role = "👑 Admin"
        else:
            exp = APPROVED_USERS.get(chat_id, 0)
            days_left = max(0, int((exp - time.time()) / 86400))
            role = f"✅ Approved User ({days_left} days left)"
            
        name = html.escape(clean_str(info.get('name', 'Unknown')))
        tag = html.escape(clean_str(info.get('localID', 'Unknown')))
        email = html.escape(clean_str(info.get('email', 'Unknown')))
        cars_owned = info.get('cars', 0)

        try: money_val = int(info.get('money') or 0)
        except: money_val = 0
        try: coin_val = int(info.get('coin') or 0)
        except: coin_val = 0

        text = f"{E('success')} <b>Logged in!</b>\n\n" \
               f"{E('account_info')} <b>Your Information</b>\n───────────────\n" \
               f"{E('access_granted')} Status: Access granted\n" \
               f"{E('set_id')} Telegram ID: <code>{chat_id}</code>\n" \
               f"{E('role')} Role: {role}\n\n" \
               f"{E('vehicles')} <b>CPM DASHBOARD</b>\n───────────────\n" \
               f"{E('account_info')} Name: {name}\n" \
               f"{E('set_id')} ID: {tag}\n" \
               f"{E('money')} Money: {money_val:,}\n" \
               f"{E('coin')} Coins: {coin_val:,}\n" \
               f"{E('vehicles')} Cars owned: {cars_owned}\n" \
               f"{E('email')} {email}\n\n" \
               f"{E('choose_section')} Choose a section:"

        if custom_top_msg: text = f"{E('info')} <b>{html.escape(custom_top_msg)}</b>\n\n{text}"

        markup = create_dashboard_keyboard(chat_id)

        if is_callback and message_id:
            try: bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
            except: bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════
# 🚀 COMMANDS
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    try:
        chat_id = message.chat.id
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        if chat_id in user_states: del user_states[chat_id]
        track_user(chat_id)

        if chat_id not in user_sessions:
            user_sessions[chat_id] = {'cpm_logged_in': False}
        elif 'cpm_logged_in' not in user_sessions[chat_id]:
            user_sessions[chat_id]['cpm_logged_in'] = False

        bot.send_message(chat_id, f"{E('terminal_hybrid')} <b>ASHMIT'S CPM STORE</b> {E('terminal_hybrid')}", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
        safe_send_dashboard(chat_id, force_refresh=False, is_callback=False)
    except: pass

@bot.message_handler(commands=['admin'])
def admin_command(message):
    try:
        chat_id = message.chat.id
        try: bot.delete_message(chat_id, message.message_id)
        except: pass
        if chat_id in user_states: del user_states[chat_id]
        if not is_admin(chat_id): return bot.send_message(chat_id, f"{E('error')} <b>UNAUTHORIZED.</b>", parse_mode="HTML")
        bot.send_message(chat_id, f"{E('admin_panel')} <b>OVERSEER TERMINAL</b>", reply_markup=create_admin_keyboard(), parse_mode="HTML")
    except: pass

@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    try:
        chat_id = message.chat.id
        if not is_admin(chat_id): return
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(chat_id, f"{E('error')} Format: <code>/addadmin &lt;user_id&gt;</code>", parse_mode="HTML")
            return
        target_id = int(args[1])
        if add_admin(target_id): bot.send_message(chat_id, f"{E('success')} User <code>{target_id}</code> is now an Admin.", parse_mode="HTML")
    except: pass

@bot.message_handler(commands=['remadmin'])
def rem_admin_command(message):
    try:
        chat_id = message.chat.id
        if not is_admin(chat_id): return
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(chat_id, f"{E('error')} Format: <code>/remadmin &lt;user_id&gt;</code>", parse_mode="HTML")
            return
        target_id = int(args[1])
        if remove_admin(target_id): bot.send_message(chat_id, f"{E('success')} User <code>{target_id}</code> is no longer an Admin.", parse_mode="HTML")
    except: pass

# ═══════════════════════════════════════════════════════════
# 🎯 MESSAGE ROUTER
# ═══════════════════════════════════════════════════════════
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        chat_id = message.chat.id
        text = message.text

        try: bot.delete_message(chat_id, message.message_id)
        except: pass

        track_user(chat_id)
        if not text or text.startswith('/'): return

        if chat_id in user_states:
            state = user_states[chat_id]

            if state.get('awaiting_add_admin'):
                del user_states[chat_id]
                msg_id = state.get('msg_id')
                if not is_admin(chat_id): return
                try:
                    target_id = int(text.strip())
                    add_admin(target_id)
                    try: bot.delete_message(chat_id, msg_id)
                    except: pass
                    bot.send_message(chat_id, f"{E('success')} Admin rights granted to ID: <code>{target_id}</code>", parse_mode="HTML")
                except:
                    try: bot.edit_message_text(f"{E('error')} Invalid ID format.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return

            if state.get('awaiting_rem_admin'):
                del user_states[chat_id]
                msg_id = state.get('msg_id')
                if not is_admin(chat_id): return
                try:
                    target_id = int(text.strip())
                    remove_admin(target_id)
                    try: bot.delete_message(chat_id, msg_id)
                    except: pass
                    bot.send_message(chat_id, f"{E('error')} Admin rights revoked from ID: <code>{target_id}</code>", parse_mode="HTML")
                except:
                    try: bot.edit_message_text(f"{E('error')} Invalid ID format.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return

            if state.get('awaiting_broadcast'):
                del user_states[chat_id]
                msg_id = state.get('msg_id')
                if not is_admin(chat_id): return
                c = 0
                for uid in get_all_tracked_users():
                    try: bot.send_message(uid, f"{E('broadcast_announcement')} <b>ANNOUNCEMENT</b>\n┣━━━━━━━━━━━━━━━━━━┫\n{html.escape(text)}", parse_mode="HTML"); c += 1
                    except: pass
                try:
                    bot.delete_message(chat_id, msg_id)
                    bot.send_message(chat_id, f"{E('success')} Delivered to {c} users.", parse_mode="HTML")
                except: pass
                return

            # --- LOGIN ---
            if state.get('awaiting_cpm_login_email'):
                user_sessions[chat_id]['email'] = text.strip()
                msg_id = state.get('msg_id')
                user_states[chat_id] = {'awaiting_cpm_login_pass': True, 'msg_id': msg_id}
                try: bot.edit_message_text(f"{E('password')} Send the password to login:", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                except: pass
                return

            if state.get('awaiting_cpm_login_pass'):
                password = text.strip()
                email = user_sessions[chat_id].get('email', '')
                msg_id = state.get('msg_id')
                del user_states[chat_id]

                try: bot.edit_message_text(f"{E('loading')} Authenticating...", chat_id, msg_id, parse_mode="HTML")
                except: pass

                try:
                    web_uid = get_web_uid(chat_id)
                    res = nuker.login(email, password)
                    if res and isinstance(res, dict) and res.get("ok"):
                        nuker.save_token(web_uid, res.get("auth", ""), email, password, res.get("refresh_token", ""), res.get("firebase_uid", ""))
                        user_sessions[chat_id].update({'cpm_logged_in': True, 'web_uid': web_uid})
                        safe_send_dashboard(chat_id, force_refresh=True, is_callback=True, message_id=msg_id)
                    else:
                        err = clean_str(res.get('message', 'Unknown Error') if isinstance(res, dict) else 'Network Failure')
                        try: bot.edit_message_text(f"{E('error')} AUTH FAILED: {html.escape(err)}", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                        except: pass
                except:
                    try: bot.edit_message_text(f"{E('error')} API Timeout.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return

            # --- REGISTER ---
            if state.get('awaiting_cpm_register_email'):
                user_sessions[chat_id]['reg_email'] = text.strip()
                msg_id = state.get('msg_id')
                user_states[chat_id] = {'awaiting_cpm_register_pass': True, 'msg_id': msg_id}
                try: bot.edit_message_text(f"{E('password')} Send a new password (min 6 chars):", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                except: pass
                return

            if state.get('awaiting_cpm_register_pass'):
                password = text.strip()
                email = user_sessions[chat_id].get('reg_email', '')
                msg_id = state.get('msg_id')
                del user_states[chat_id]

                try: bot.edit_message_text(f"{E('loading')} Creating Account...", chat_id, msg_id, parse_mode="HTML")
                except: pass

                try:
                    web_uid = get_web_uid(chat_id)
                    res = nuker.register(email, password)
                    if res and isinstance(res, dict) and res.get("ok"):
                        auth = res.get("auth", "")
                        fuid = res.get("firebase_uid", "")
                        blank_profile = {
                            "Name": "Player", "money": 25000, "coin": 0,
                            "localID": str(random.randint(1000000, 9999999)).zfill(8),
                            "allData": '{"cars":[]}', "floats": [], "integers": []
                        }
                        try: nuker._send(auth, blank_profile, fuid)
                        except: pass
                        nuker.save_token(web_uid, auth, email, password, res.get("refresh_token", ""), fuid)
                        user_sessions[chat_id].update({'cpm_logged_in': True, 'web_uid': web_uid})
                        safe_send_dashboard(chat_id, custom_top_msg="Account Created Successfully!", force_refresh=True, is_callback=True, message_id=msg_id)
                    else:
                        err = clean_str(res.get('message', 'Registration Failed') if isinstance(res, dict) else 'Network Failure')
                        try: bot.edit_message_text(f"{E('error')} CREATE FAILED: {html.escape(err)}", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                        except: pass
                except:
                    try: bot.edit_message_text(f"{E('error')} API Timeout.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return

            # --- ACCOUNT EDITS ---
            if state.get('awaiting_cpm1_email'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                nuker.change_email(user_sessions[chat_id].get('web_uid'), text.strip())
                safe_send_dashboard(chat_id, custom_top_msg="Email Changed!", force_refresh=True, is_callback=True, message_id=msg_id)
                return

            if state.get('awaiting_change_id'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                nuker.change_player_id(user_sessions[chat_id].get('web_uid'), text.strip().upper())
                safe_send_dashboard(chat_id, custom_top_msg="Tag Masked!", force_refresh=True, is_callback=True, message_id=msg_id)
                return

            if state.get('awaiting_change_name'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                nuker.change_player_name(user_sessions[chat_id].get('web_uid'), text.strip())
                safe_send_dashboard(chat_id, custom_top_msg="Name Changed!", force_refresh=True, is_callback=True, message_id=msg_id)
                return

            if state.get('awaiting_change_pass'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                try: bot.delete_message(chat_id, msg_id)
                except: pass
                safe_send_dashboard(chat_id, custom_top_msg="Password Feature Processed!", force_refresh=True, is_callback=False)
                return

            if state.get('awaiting_money'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                try:
                    nuker.set_money(user_sessions[chat_id].get('web_uid'), int(text.strip()))
                    safe_send_dashboard(chat_id, custom_top_msg="Custom Money Applied!", force_refresh=True, is_callback=True, message_id=msg_id)
                except:
                    try: bot.edit_message_text(f"{E('error')} Numeric required.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return

            if state.get('awaiting_coin'):
                msg_id = state.get('msg_id')
                del user_states[chat_id]
                try:
                    nuker.set_coin(user_sessions[chat_id].get('web_uid'), int(text.strip()))
                    safe_send_dashboard(chat_id, custom_top_msg="Custom Coins Applied!", force_refresh=True, is_callback=True, message_id=msg_id)
                except:
                    try: bot.edit_message_text(f"{E('error')} Numeric required.", chat_id, msg_id, reply_markup=cancel_keyboard(), parse_mode="HTML")
                    except: pass
                return
    except Exception:
        pass
        
                                                # --- CLONING HANDLERS ---
            if state.get('awaiting_clone_master_email'):
                user_sessions[chat_id]['clone_master_email'] = text.strip()
                msg_id = state.get('msg_id')
                user_states[chat_id] = {
                    'awaiting_clone_master_pass': True,
                    'msg_id': msg_id
                }
                try:
                    bot.edit_message_text(
                        f"{E('password')} Send the <b>Master Account Password</b>:",
                        chat_id,
                        msg_id,
                        reply_markup=cancel_keyboard(),
                        parse_mode="HTML"
                    )
                except:
                    pass
                return




            if state.get('awaiting_clone_master_pass'):
                master_pass = text.strip()
                master_email = user_sessions[chat_id].get('clone_master_email', '')
                msg_id = state.get('msg_id')
                del user_states[chat_id]

                try: bot.edit_message_text(f"{E('loading')} Cloning Master Account to your profile... Please wait.", chat_id, msg_id, parse_mode="HTML")
                except: pass

                web_uid = get_web_uid(chat_id)
                res = nuker.clone_account(web_uid, master_email, master_pass)
                
                menu_text = f"{E('unlocks_login')} <b>Unlocks Configuration</b>"
                kb = create_unlocks_keyboard()

                if res.get("ok"):
                    final_msg = f"{E('success')} <b>Account Cloned Successfully!</b>\nAll cars, vinyls, money, coins & rank transferred.\n\n{menu_text}"
                else:
                    err = clean_str(res.get('message', 'Cloning failed.'))
                    final_msg = f"{E('error')} <b>Cloning Failed:</b> {html.escape(err)}\n\n{menu_text}"

                try: bot.edit_message_text(final_msg, chat_id, msg_id, reply_markup=kb, parse_mode="HTML")
                except: pass
                return
                

# ═══════════════════════════════════════════════════════════
# 🎯 CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data

    if chat_id not in user_sessions: user_sessions[chat_id] = {}
    track_user(chat_id)

    silent_nav = ["menu_main", "init_login", "init_register", "logout", "refresh_account",
                  "menu_account", "menu_economy", "menu_unlocks",
                  "acc_info", "acc_name", "acc_id", "acc_email", "acc_pass",
                  "eco_money_cust", "eco_coins_cust",
                  "admin_view_requests"]
    if data in silent_nav:
        try: bot.answer_callback_query(call.id)
        except: pass

    # ---- ACCESS REQUEST ----
    if data == "request_access":
        if add_pending_request(chat_id):
            try: bot.answer_callback_query(call.id, "✅ Request sent to admins!", show_alert=True)
            except: pass
            for aid in get_all_admins():
                try:
                    bot.send_message(aid, f"{E('request_access')} <b>NEW ACCESS REQUEST</b>\n┣━━━━━━━━━━━━━━━━━━┫\n{E('set_id')} User ID: <code>{chat_id}</code>\n\nUse /admin → View Requests to approve.", parse_mode="HTML")
                except: pass
        else:
            try: bot.answer_callback_query(call.id, "Already pending!", show_alert=True)
            except: pass
        return safe_send_dashboard(chat_id, is_callback=True, message_id=msg_id)

    # ---- ACCESS CONTROL GATE ----
    if not is_approved(chat_id):
        return safe_send_dashboard(chat_id, is_callback=True, message_id=msg_id)

    if data == "menu_main":
        if chat_id in user_states: del user_states[chat_id]
        return safe_send_dashboard(chat_id, force_refresh=False, is_callback=True, message_id=msg_id)

    if data == "init_login":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('email')} Send your email to login:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_cpm_login_email': True, 'msg_id': msg.message_id}
        return

    if data == "init_register":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('email')} Send a new email to Create Account:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_cpm_register_email': True, 'msg_id': msg.message_id}
        return

    if data == "logout":
        if chat_id in user_sessions: user_sessions[chat_id]['cpm_logged_in'] = False
        nuker.delete_token(get_web_uid(chat_id))
        return safe_send_dashboard(chat_id, force_refresh=False, is_callback=True, message_id=msg_id)

    if data == "refresh_account":
        return safe_send_dashboard(chat_id, custom_top_msg="Account Refreshed!", force_refresh=True, is_callback=True, message_id=msg_id)

    if data == "menu_account":
        try: bot.edit_message_text(f"{E('account_info')} <b>Account Management</b>", chat_id, msg_id, reply_markup=create_account_keyboard(), parse_mode="HTML")
        except: pass
        return

    if data == "menu_economy":
        try: bot.edit_message_text(f"{E('economy_profile')} <b>Economy Settings</b>", chat_id, msg_id, reply_markup=create_economy_keyboard(), parse_mode="HTML")
        except: pass
        return

    if data == "menu_unlocks":
        try: bot.edit_message_text(f"{E('unlocks_login')} <b>Unlocks Configuration</b>", chat_id, msg_id, reply_markup=create_unlocks_keyboard(), parse_mode="HTML")
        except: pass
        return

    if data == "acc_info":
        return safe_send_dashboard(chat_id, is_callback=True, message_id=msg_id)

    if data == "acc_name":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('set_name')} Enter new Name:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_change_name': True, 'msg_id': msg.message_id}
        return
    if data == "acc_id":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('set_id')} Enter new ID:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_change_id': True, 'msg_id': msg.message_id}
        return
    if data == "acc_email":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('email')} Enter new Email:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_cpm1_email': True, 'msg_id': msg.message_id}
        return
    if data == "acc_pass":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('password')} Enter new Password:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_change_pass': True, 'msg_id': msg.message_id}
        return

    # ---- ECONOMY ----
    web_uid = get_web_uid(chat_id)

    def exec_mod(call_obj, name, func, *args):
        try:
            if data.startswith("eco_"):
                menu_text = f"{E('economy_profile')} <b>Economy Settings</b>"
                kb = create_economy_keyboard()
            else:
                menu_text = f"{E('unlocks_login')} <b>Unlocks Configuration</b>"
                kb = create_unlocks_keyboard()

            try: bot.edit_message_text(f"{E('loading')} Executing...\n\n{menu_text}", chat_id, msg_id, reply_markup=kb, parse_mode="HTML")
            except: pass

            res = func(web_uid, *args) if args else func(web_uid)

            if res and isinstance(res, dict) and res.get("ok"):
                final_text = f"{E('success')} {html.escape(name)}\n\n{menu_text}"
            else:
                err = clean_str(res.get("message", "API Blocked") if isinstance(res, dict) else "Timeout")
                final_text = f"{E('error')} Failed: {html.escape(err)}\n\n{menu_text}"

            try: bot.edit_message_text(final_text, chat_id, msg_id, reply_markup=kb, parse_mode="HTML")
            except: pass
        except Exception:
            try: bot.answer_callback_query(call_obj.id, "❌ System Error.", show_alert=True)
            except: pass

    if data == "eco_money_max": return exec_mod(call, "Money -> 50,000,000", nuker.set_money, 50000000)
    if data == "eco_coins_max": return exec_mod(call, "Coins -> 500,000", nuker.set_coin, 500000)
    if data == "eco_king": return exec_mod(call, "King Rank", nuker.set_rank)
    if data == "eco_money_cust":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('money')} Enter desired money amount:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_money': True, 'msg_id': msg.message_id}
        return
    if data == "eco_coins_cust":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('coin')} Enter desired coins amount:", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_coin': True, 'msg_id': msg.message_id}
        return

    # ---- UNLOCKS ----
    if data == "unl_w16": return exec_mod(call, "W16 Engine", nuker.unlock_w16)
    if data == "unl_smoke": return exec_mod(call, "Smoke", nuker.unlock_smoke)
    if data == "unl_fuel": return exec_mod(call, "Max Fuel", nuker.unlimited_fuel)
    if data == "unl_damage": return exec_mod(call, "No Damage", nuker.disable_damage)
    if data == "unl_horns": return exec_mod(call, "Horns", nuker.unlock_horns)
    if data == "unl_anim": return exec_mod(call, "Animations", nuker.unlock_animations)
    if data == "unl_houses": return exec_mod(call, "All Houses", nuker.unlock_houses)
    if data == "unl_wheels": return exec_mod(call, "Wheels", nuker.unlock_wheels)
    if data == "unl_levels": return exec_mod(call, "Complete All Levels", nuker.complete_all_levels)
    if data == "unl_ultimate": return exec_mod(call, "Ultimate Glitch", nuker.unlock_all_features)
    if data == "unl_clone":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(
            chat_id,
            f"{E('account_info')} <b>ACCOUNT CLONING</b>\n\n"
            f"This will overwrite your target account's cars, vinyls, rank, money, coins, and equipment with data from a Master Account.\n\n"
            f"Send the <b>Master Account Email</b>:",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
        user_states[chat_id] = {'awaiting_clone_master_email': True, 'msg_id': msg.message_id}
        return
        
    # ---- ADMIN PANEL ----
    if data == "admin_panel":
        if not is_admin(chat_id): return
        try: bot.answer_callback_query(call.id)
        except: pass
        try: bot.edit_message_text(f"{E('admin_panel')} <b>OVERSEER TERMINAL</b>", chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
        except: pass
        return

    if data == "admin_add_admin":
        if not is_admin(chat_id): return
        try: bot.answer_callback_query(call.id)
        except: pass
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('add_admin')} <b>ENTER TARGET ID TO MAKE ADMIN:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_add_admin': True, 'msg_id': msg.message_id}
        return

    if data == "admin_rem_admin":
        if not is_admin(chat_id): return
        try: bot.answer_callback_query(call.id)
        except: pass
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('remove_admin')} <b>ENTER TARGET ID TO REMOVE ADMIN:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_rem_admin': True, 'msg_id': msg.message_id}
        return

    if data == "admin_view_admins":
        if not is_admin(chat_id): return
        admins = get_all_admins()
        msg_text = f"{E('users')} <b>CURRENT ADMINS</b>\n┣━━━━━━━━━━━━━━━━━━┫\n" + "".join([f"{E('set_id')} <code>{uid}</code>\n" for uid in admins])
        try: bot.edit_message_text(msg_text, chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
        except: pass
        return

    if data == "admin_view_requests":
        if not is_admin(chat_id): return
        pending = get_all_pending()
        if not pending:
            try: bot.edit_message_text(f"{E('info')} <b>No pending requests.</b>", chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
            except: pass
            return
        text = f"{E('request_access')} <b>PENDING ACCESS REQUESTS</b>\n┣━━━━━━━━━━━━━━━━━━┫\n"
        markup = types.InlineKeyboardMarkup(row_width=2)
        for uid in pending[:10]:
            text += f"{E('set_id')} <code>{uid}</code>\n"
            markup.row(
                btn(f"✅ 1D", f"req_app_1d_{uid}"),
                btn(f"✅ 1W", f"req_app_7d_{uid}"),
                btn(f"✅ 1M", f"req_app_30d_{uid}"),
                btn(f"🚫 Reject", f"req_rej_{uid}")
            )
        markup.add(btn("🔙 Back", "admin_panel"))
        try: bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="HTML")
        except: pass
        return

    if data.startswith("req_app_"):
        if not is_admin(chat_id): return
        try:
            parts = data.split("_")
            days_str = parts[2]
            target_id = int(parts[3])
            days = 1 if days_str == "1d" else (7 if days_str == "7d" else 30)
            
            approve_user(target_id, days)
            try: bot.answer_callback_query(call.id, f"✅ Approved {target_id} for {days} days", show_alert=True)
            except: pass
            try: bot.send_message(target_id, f"{E('success')} Your access request has been <b>approved</b> for <b>{days} days</b>! Send /start to begin.", parse_mode="HTML")
            except: pass
        except: pass
        pending = get_all_pending()
        if not pending:
            try: bot.edit_message_text(f"{E('info')} <b>No pending requests.</b>", chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
            except: pass
        else:
            text = f"{E('request_access')} <b>PENDING ACCESS REQUESTS</b>\n┣━━━━━━━━━━━━━━━━━━┫\n"
            markup = types.InlineKeyboardMarkup(row_width=2)
            for uid in pending[:10]:
                text += f"{E('set_id')} <code>{uid}</code>\n"
                markup.row(
                    btn(f"✅ 1D", f"req_app_1d_{uid}"),
                    btn(f"✅ 1W", f"req_app_7d_{uid}"),
                    btn(f"✅ 1M", f"req_app_30d_{uid}"),
                    btn(f"🚫 Reject", f"req_rej_{uid}")
                )
            markup.add(btn("🔙 Back", "admin_panel"))
            try: bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="HTML")
            except: pass
        return

    if data.startswith("req_rej_"):
        if not is_admin(chat_id): return
        try:
            target_id = int(data.replace("req_rej_", ""))
            reject_user(target_id)
            try: bot.answer_callback_query(call.id, f"🚫 Rejected {target_id}", show_alert=True)
            except: pass
            try: bot.send_message(target_id, f"{E('rejected')} Your access request has been rejected.", parse_mode="HTML")
            except: pass
        except: pass
        pending = get_all_pending()
        if not pending:
            try: bot.edit_message_text(f"{E('info')} <b>No pending requests.</b>", chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
            except: pass
        else:
            text = f"{E('request_access')} <b>PENDING ACCESS REQUESTS</b>\n┣━━━━━━━━━━━━━━━━━━┫\n"
            markup = types.InlineKeyboardMarkup(row_width=2)
            for uid in pending[:10]:
                text += f"{E('set_id')} <code>{uid}</code>\n"
                markup.row(
                    btn(f"✅ 1D", f"req_app_1d_{uid}"),
                    btn(f"✅ 1W", f"req_app_7d_{uid}"),
                    btn(f"✅ 1M", f"req_app_30d_{uid}"),
                    btn(f"🚫 Reject", f"req_rej_{uid}")
                )
            markup.add(btn("🔙 Back", "admin_panel"))
            try: bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="HTML")
            except: pass
        return

    if data == "admin_broadcast":
        if not is_admin(chat_id): return
        try: bot.answer_callback_query(call.id)
        except: pass
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        msg = bot.send_message(chat_id, f"{E('broadcast_announcement')} <b>ENTER BROADCAST MESSAGE:</b>", reply_markup=cancel_keyboard(), parse_mode="HTML")
        user_states[chat_id] = {'awaiting_broadcast': True, 'msg_id': msg.message_id}
        return

    if data == "admin_stats":
        if not is_admin(chat_id): return
        try: bot.answer_callback_query(call.id)
        except: pass
        t_users = get_total_users()
        pending = len(get_all_pending())
        approved = len(APPROVED_USERS)
        try: bot.edit_message_text(
            f"{E('stats_telemetry')} <b>TELEMETRY</b>\n┣━━━━━━━━━━━━━━━━━━┫\n"
            f"{E('users')} Total Users: {t_users}\n"
            f"{E('pending')} Pending Requests: {pending}\n"
            f"{E('approved')} Approved Users: {approved}\n"
            f"{E('admin_panel')} Admins: {len(get_all_admins())}",
            chat_id, msg_id, reply_markup=create_admin_keyboard(), parse_mode="HTML")
        except: pass
        return

# ═══════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("="*60)
    print("⚡ NELHUMBLE CPM STORE - ULTIMATE ENGINE ONLINE ⚡")
    print("="*60)
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)
