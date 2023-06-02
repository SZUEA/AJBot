"""连接SD-WEBUI-API"""
import random

from PIL import Image, PngImagePlugin
from translate import Translator
import os, json, io, base64, requests
from EAbotoy.contrib import get_cache_dir, plugin_receiver
from plugins.bot_dev.bot_api import is_api_master
from EAbotoy.model import WeChatMsg
from EAbotoy.sugar import Picture, Text


def get_image_from_url(prompt, hrop, seeds=-1, now=0, multi=1024):
    NUM = 2
    RM = random.randint(1, NUM)
    if now != 0: RM = now
    if RM == 1:
        url = "http://127.0.0.1:7861"
    elif RM == 2:
        url = "http://local-lab.hz2016.cn:7861"

    payload = {
        "prompt": prompt,
        "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers,extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry , disfigured, lowres, bad anatomy, bad hands, text, error, more fingers, extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, watermark,  blurry, bad feet, bad eye",
        "steps": 10,
        "width": 512,
        "height": 512,
        "enable_hr": hrop,
        "hr_resize_x": 1024,
        "hr_resize_y": 1024,
        "denoising_strength": 0,
        "firstphase_width": 0,
        "firstphase_height": 0,
        "hr_scale": 2,
        "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
        "hr_second_pass_steps": 0,
        "seed": seeds,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "batch_size": 1,
        "n_iter": 1,
        "cfg_scale": 7,
        "tiling": False,
        "restore_faces": False,
        "sampler_name": "DPM++ 2S a Karras",
        "send_images": True,
        "alwayson_scripts": {}
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    if response.status_code != 200:
        if now == 1: return None
        if now == 0: now = NUM + 1
        return get_image_from_url(prompt, hrop,seeds=seeds, now=now - 1, multi=multi)
    r = response.json()
    seeds = json.loads(r['info'])['seed']
    if multi>1024:
        payload={
            "resize_mode": 0,
            "show_extras_results": True,
            "gfpgan_visibility": 0,
            "codeformer_visibility": 0,
            "codeformer_weight": 0,
            "upscaling_resize": 2,
            "upscaling_resize_w": multi,
            "upscaling_resize_h": multi,
            "upscaling_crop": True,
            "upscaler_1": "R-ESRGAN 4x+ Anime6B",
            "upscaler_2": "None",
            "extras_upscaler_2_visibility": 0,
            "upscale_first": False,
            "image": r['images'][0]
        }
        response = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=payload)
        if response.status_code != 200:
            if now == 1: return None
            if now == 0: now = NUM + 1
            return get_image_from_url(prompt, hrop,seeds=seeds, now=now - 1, multi=multi)
        r = response.json()
        return r['image'], seeds
    else:
        return r['images'][0], seeds


@plugin_receiver.wx
def receive_wx_msg(ctx: WeChatMsg):
    isAdmin = is_api_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master
    # if not isAdmin:
    #    return
    if ctx.Content.startswith("AIGC "):
        args = ctx.Content[5:]
        result, seeds = get_image_from_url(args, False)
        Text(f"message: %s\nseeds: %d\nAIGCX %d %s" % (args, seeds, seeds, args))
        Picture(pic_base64=result)
    elif ctx.Content.startswith("AIGCC "):
        args = ctx.Content[6:]
        os.environ["http_proxy"] = "http://localhost:7890"
        os.environ["https_proxy"] = "http://localhost:7890"
        translator = Translator(from_lang="zh", to_lang="en")
        translation = translator.translate(args)
        result, seeds = get_image_from_url(translation, False)
        Text(f"message: %s\nseeds: %d\nAIGCX %d %s" % (translation, seeds, seeds, translation))
        Picture(pic_base64=result)
    elif ctx.Content.startswith("AIGCX "):
        args = ctx.Content[6:]
        len = args.find(' ')
        if len != -1:
            setseeds = args[0:len]
            args = args[len + 1:]
            result, seeds = get_image_from_url(args, True, seeds=setseeds)
            Text(f"message: %s\nseeds: %d\nAIGCF %d %d %s" % (args, seeds, seeds, 2048, args))
            Picture(pic_base64=result)
    elif ctx.Content.startswith("AIGCF "):
        if not isAdmin:
            Text(f"AIGCF ONLY ADMIN")
            return
        args = ctx.Content[6:]
        len = args.find(' ')
        if len != -1:
            setseeds = int(args[0:len])
            args = args[len + 1:]
            len = args.find(' ')
            if len != -1:
                multi = int(args[0:len])
                args = args[len + 1:]
                result, seeds = get_image_from_url(args, True, seeds=setseeds ,multi=multi)
                Text(f"message: %s\nseeds: %d\nAIGCF %d %d %s" % (args, seeds, seeds, multi*2 ,args))
                Picture(pic_base64=result)
