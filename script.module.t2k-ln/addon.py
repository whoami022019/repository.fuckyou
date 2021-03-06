# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 RACC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from xbmcgui import ListItem
from routing import Plugin

import requests
import time
import json
import io
import os
import sys
import datetime
from base64 import b64decode, urlsafe_b64encode
from itertools import chain

try:
    from urllib.parse import quote as orig_quote
except ImportError:
    from urllib import quote as orig_quote

from resources.lib.lntv_config import lntvConfig
from resources.lib.lntv_channels import lntvChannels

addon = xbmcaddon.Addon()
plugin = Plugin()
plugin.name = addon.getAddonInfo("name")
s = requests.Session()

# plugin conf
USER_DATA_DIR = xbmc.translatePath(addon.getAddonInfo("profile")).decode("utf-8")
ADDON_DATA_DIR = xbmc.translatePath(addon.getAddonInfo("path")).decode("utf-8")
RESOURCES_DIR = os.path.join(ADDON_DATA_DIR, "resources")
channel_list_file = os.path.join(USER_DATA_DIR, "channels.json")
app_config_file = os.path.join(USER_DATA_DIR, "config.json")
implemented = ["0", "23", "29", "32", "33", "38", "44", "48", "54", "45"]

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1; AFTT Build/LMY47O)"

_reset = addon.getSetting("reset") or "0"
if int(_reset) < int(33):
    addon.setSetting("user_id", "")
    addon.setSetting("data_time", "")
    addon.setSetting("reset", "33")

data_time = int(addon.getSetting("data_time") or "0")
cache_time = int(addon.getSetting("cache_time") or "0")
user_id = addon.getSetting("user_id")


def quote(s, safe=""):
    return orig_quote(s.encode("utf-8"), safe.encode("utf-8"))


current_time = int(time.time())
if current_time - data_time > cache_time * 60 * 60:
    try:
        new_config = lntvConfig()
        app_config = new_config.get_data()
        with io.open(app_config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(app_config, indent=2, sort_keys=True, ensure_ascii=False))
    except:
        with io.open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.loads(f.read())
    try:
        with io.open(channel_list_file, "r", encoding="utf-8") as f:
            old_channels = json.loads(f.read())
    except:
        old_channels = ""
    try:
        new_channels = lntvChannels(app_config, user_id)
        channel_list = new_channels.get_channel_list()
        if len(channel_list) < (len(old_channels) / 2):
            addon.setSetting("user_id", "")
            channel_list = old_channels
        else:
            addon.setSetting("user_id", new_channels.user)
        with io.open(channel_list_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(channel_list, indent=2, sort_keys=True, ensure_ascii=False))
    except:
        channel_list = old_channels
    addon.setSetting("data_time", str(int(time.time())))
else:
    try:
        with io.open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.loads(f.read())
    except IOError:
        app_config = ""
    try:
        with io.open(channel_list_file, "r", encoding="utf-8") as f:
            channel_list = json.loads(f.read())
    except IOError:
        channel_list = ""


def fix_auth_date(auth):
    now = datetime.datetime.utcnow()
    _in = list(auth)
    _in.pop(len(_in) + 2 - 3 - int(str(now.year)[:2]))
    _in.pop(len(_in) + 3 - 4 - int(str(now.year)[2:]))
    # java January = 0
    _in.pop(len(_in) + 4 - 5 - (now.month - 1 + 1 + 10))
    _in.pop(len(_in) + 5 - 6 - now.day)
    return "".join(_in)


# star sports
def get_auth_token_33(referer):
    if referer == None:
        referer = ""
    wms_url = b64decode(app_config.get("ZmFtYW50YXJhbmFfdGF0aTAw")[1:])
    auth = b64decode(app_config.get("dGVydHRleWFj")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))
    fix_auth = lambda auth: "".join([auth[:-56], auth[-55:-50], auth[-49:-42], auth[-41:-34], auth[-33:]])
    req = requests.Request(
        "GET",
        wms_url,
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Referer": referer, "Modified": modified(mod_value), "Authorization": auth},
    )
    prq = req.prepare()
    r = s.send(prq)
    return fix_auth(r.text)


# eurosport
def get_auth_token_38(referer):
    if referer == None:
        referer = ""
    wms_url = b64decode(app_config.get("YmVsZ2lfMzgw")[1:])
    auth = b64decode(app_config.get("Z2Vsb29mc2JyaWVm")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))
    fix_auth = lambda auth: "".join([auth[:-66], auth[-65:-56], auth[-55:-46], auth[-45:-36], auth[-35:]])
    req = requests.Request(
        "GET",
        wms_url,
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Referer": referer, "Modified": modified(mod_value), "Authorization": auth},
    )
    prq = req.prepare()
    r = s.send(prq)
    return fix_auth(r.text)


# ane
def get_auth_token_44():
    wms_url = b64decode(app_config.get("YmVsa2lpdW1uXzk2")[1:])
    auth = b64decode(app_config.get("dGVydHRleWFj")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))
    req = requests.Request(
        "GET", wms_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Modified": modified(mod_value), "Authorization": auth}
    )
    prq = req.prepare()
    r = s.send(prq)
    return fix_auth_date(r.text)


# canada
def get_auth_token_23():
    wms_url = b64decode(app_config.get("dGhlX3RlYXMw")[1:])
    auth = b64decode(app_config.get("TWVuX2Nob2Jpc18w")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))
    req = requests.Request(
        "GET", wms_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Modified": modified(mod_value), "Authorization": auth}
    )
    prq = req.prepare()
    r = s.send(prq)
    return r.text


# bt sports 1
def get_auth_token_48(referer):
    if referer == None:
        referer = ""
    wms_url = b64decode(app_config.get("Ym9ya3lsd3VyXzQ4")[1:])
    auth = b64decode(app_config.get("dGVydHRleWFj")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))
    req = requests.Request(
        "GET",
        wms_url,
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Referer": referer, "Modified": modified(mod_value), "Authorization": auth},
    )
    prq = req.prepare()
    r = s.send(prq)
    return fix_auth_date(r.text)


# bein 1
def get_stream_32(stream):
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
    api_url = b64decode(app_config.get("dWt1c3VzYV91a3ViaGFsYV9iYXRlczAw")[1:])
    auth = b64decode(app_config.get("amFnX3Ryb3JfYXR0X2Vu")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))

    response_body_api_url = b64decode(app_config.get("bWFya2llcmlzX2J0aXMw")[1:])
    response_body_auth = b64decode(app_config.get("bXdlbnRlcnR5")[1:])
    req = requests.Request("GET", response_body_api_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Authorization": response_body_auth})
    prq = req.prepare()
    r = s.send(prq)
    response_body = r.text

    data = {"data": json.dumps({"token": 32, "response_body": response_body, "stream_url": stream})}
    req = requests.Request(
        "POST", api_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Modified": modified(mod_value), "Authorization": auth}, data=data
    )
    prq = req.prepare()
    r = s.send(prq)
    return r.json().get("stream_url")


# bt sports 1
def get_stream_29(stream):
    api_url = b64decode(app_config.get("Y2hlaWxlYWRoIF9DZWFuZ2FsX29udGlz")[1:])
    auth = b64decode(app_config.get("amFnX3Ryb3JfYXR0X2Vu")[1:])
    mod_value = int(b64decode(app_config.get("TW9vbl9oaWsx")[1:]))
    modified = lambda value: "".join(chain(*zip(str(int(time.time()) ^ value), "0123456789")))

    data = {"data": json.dumps({"token": 29, "response_body": "f", "stream_url": stream})}
    req = requests.Request(
        "POST", api_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Modified": modified(mod_value), "Authorization": auth}, data=data
    )
    prq = req.prepare()
    r = s.send(prq)
    return r.json().get("stream_url")


# sky
def get_stream_45(stream):
    import re,urlparse
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
    api_url = b64decode(stream[1:]).split("|")[0]
    req = requests.Request("GET", api_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Referer": "https://hdcast.me"})
    prq = req.prepare()
    r = s.send(prq)
    _pattern = re.compile(r"""source:\s*'([^']+playlist.m3u8[^']+)'""")
    _source = re.search(_pattern, r.text).group(1)
    return urlparse.urljoin(api_url,_source)


def get_stream_54(stream):
    import re
    from urlparse import urlparse
    api_url = b64decode(app_config.get("Ym9rYXJpc2hvbDc3")[1:])
    req = requests.Request(
        "POST", api_url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip", "Content-Type": "application/x-www-form-urlencoded", "Content-Length": "0"}
    )
    prq = req.prepare()
    r = s.send(prq)

    _pattern = re.compile("<script>([^<]+)</script>", re.M)
    _split = re.search(_pattern, r.text).group(1).strip().split("\n")
    _upperCase = urlparse(api_url).path.split("/")[1].upper()
    _c = ord(_upperCase[0]) - ord("@")
    _s2 = _split[ord(_upperCase[(len(_upperCase) - 1)]) - ord("@") - 1].split("?")[1]
    _n = len(_s2) - 1
    _in = list(_s2)
    _in.pop(2 + _n - (_c + 3))
    _in.pop(3 + _n - (_c + 11))
    _in.pop(4 + _n - (_c + 19))
    _in.pop(5 + _n - (_c + 27))
    return stream.replace("$", b64decode(r.headers["session"]))+"?"+"".join(_in)


@plugin.route("/")
def root():
    categories = channel_list.get("categories_list")
    list_items = []
    for c in categories:
        li = ListItem(c.get("cat_name"))
        url = plugin.url_for(list_channels, cat=c.get("cat_id"))
        list_items.append((url, li, True))

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_FULLPATH)
    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_channels/<cat>")
def list_channels(cat=None):
    list_items = []
    for channel in channel_list.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("cat_id") == "8":
            channel["cat_id"] = "1"

        if channel.get("cat_id") == cat:
            if len([stream for stream in channel.get("Qc3RyZWFtX2xpc3Q=") if b64decode(stream.get("AdG9rZW4=")[:-1]) in implemented]) == 0:
                continue

            title = b64decode(channel.get("ZY19uYW1l")[:-1])
            icon = b64decode(channel.get("abG9nb191cmw=")[1:])
            image = "{0}|User-Agent={1}".format(icon, quote(user_agent))
            c_id = channel.get("rY19pZA==")

            li = ListItem(title)
            li.setProperty("IsPlayable", "true")
            li.setInfo(type="Video", infoLabels={"Title": title, "mediatype": "video"})
            li.setArt({"thumb": image, "icon": image})
            try:
                li.setContentLookup(False)
            except AttributeError:
                pass
            url = plugin.url_for(play, c_id=c_id)
            list_items.append((url, li, False))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/play/<c_id>/play.pvr")
def play(c_id):
    for channel in channel_list.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("rY19pZA==") == c_id:
            selected_channel = channel
            break

    # stream_list = selected_channel.get("Qc3RyZWFtX2xpc3Q=")
    stream_list = [stream for stream in selected_channel.get("Qc3RyZWFtX2xpc3Q=") if b64decode(stream.get("AdG9rZW4=")[:-1]) in implemented]
    if len(stream_list) > 1:
        select_list = []
        for stream in stream_list:
            select_list.append(b64decode(stream.get("Bc3RyZWFtX3VybA==")[1:]))

        dialog = xbmcgui.Dialog()
        ret = dialog.select("Choose Stream", select_list)
        selected_stream = stream_list[ret]
    else:
        selected_stream = stream_list[0]

    if "AdG9rZW4=" in selected_stream:
        if b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "33":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + get_auth_token_33(selected_stream.get("referer"))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "38":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + get_auth_token_38(selected_stream.get("referer"))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "44":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + get_auth_token_44()
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "54":
            media_url = get_stream_54(b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "45":
            media_url = get_stream_45(b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "23":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + get_auth_token_23()
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "48":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + get_auth_token_48(selected_stream.get("referer"))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "32":
            media_url = get_stream_32(b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "29":
            media_url = get_stream_29(b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]))
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == "0":
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:])
        else:
            media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]) + b64decode(selected_stream.get("AdG9rZW4=")[:-1])
    else:
        media_url = b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:])

    if selected_stream.get("player_user_agent", user_agent) == None or selected_stream.get("player_user_agent", user_agent) == "null" or selected_stream.get("player_user_agent", user_agent) == "":
        selected_stream["player_user_agent"] = user_agent

    media_url = "{0}|User-Agent={1}".format(media_url, quote(selected_stream.get("player_user_agent", user_agent)))

    title = b64decode(selected_channel.get("ZY19uYW1l")[:-1])
    icon = b64decode(selected_channel.get("abG9nb191cmw=")[1:])
    image = "{0}|User-Agent={1}".format(icon, quote(user_agent))

    if "playlist.m3u8" in media_url:
        if addon.getSetting("inputstream") == "true":
            li = ListItem(title, path=media_url)
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setProperty("inputstreamaddon", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "hls")
            li.setProperty("inputstream.adaptive.stream_headers", media_url.split("|")[-1])
        elif addon.getSetting("livestreamer") == "true":
            serverPath = os.path.join(xbmc.translatePath(addon.getAddonInfo("path")), "livestreamerXBMCLocalProxy.py")
            runs = 0
            while not runs > 10:
                try:
                    requests.get("http://127.0.0.1:19001/version")
                    break
                except Exception:
                    xbmc.executebuiltin("RunScript(" + serverPath + ")")
                    runs += 1
                    xbmc.sleep(600)
            livestreamer_url = "http://127.0.0.1:19001/livestreamer/" + urlsafe_b64encode("hlsvariant://" + media_url)
            li = ListItem(title, path=livestreamer_url)
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("video/x-mpegts")
        else:
            li = ListItem(title, path=media_url)
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
    else:
        li = ListItem(title, path=media_url)
        li.setArt({"thumb": image, "icon": image})
    try:
        li.setContentLookup(False)
    except AttributeError:
        pass

    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == "__main__":
    plugin.run(sys.argv)
