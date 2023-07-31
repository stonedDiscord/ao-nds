import os
import subprocess
import math

from PIL import Image

import images

print("AO NDS converter tool")
print("This tool will convert your AO 'base' folder to formats that will work with the Nintendo DS.\n")

print("Drag the AO base folder to this console window then press ENTER:")
folder = input("> ")

try:
    os.makedirs("converted/data/ao-nds")
    os.makedirs("converted/data/ao-nds/background")
    os.makedirs("converted/data/ao-nds/characters")
    os.makedirs("converted/data/ao-nds/evidence")
    os.makedirs("converted/data/ao-nds/sounds/general")
    os.makedirs("converted/data/ao-nds/sounds/music")
    os.makedirs("converted/data/ao-nds/sounds/blips")
except:
    pass

# start
print("Converting backgrounds...")
for bg in os.listdir(folder+"/background"):
    if not os.path.isdir(folder+"/background/"+bg):
        continue

    print(bg)
    try: os.mkdir("converted/data/ao-nds/background/"+bg)
    except: pass

    if os.path.exists("converted/data/ao-nds/background/"+bg+"/desk_tiles.cfg"):
        os.remove("converted/data/ao-nds/background/"+bg+"/desk_tiles.cfg")

    # convert background first
    for imgfile in ["defenseempty.png", "prosecutorempty.png", "witnessempty.png", "helperstand.png", "prohelperstand.png", "judgestand.png"]:
        full_filename = folder+"/background/"+bg+"/"+imgfile
        if not os.path.exists(full_filename):
            continue

        new_file = os.path.splitext(imgfile)[0]+".img.bin"

        img = Image.open(full_filename).convert("RGBA")
        if img.size[0] != 256 or img.size[1] != 192:
            img = img.resize((256, 192), Image.BICUBIC)
        img.save("temp.png")
        img.close()

        # 16-bit bitmap, disable alpha and set opaque bit for all pixels, LZ77 compression, export to .img.bin, don't generate .h file
        subprocess.Popen("./grit temp.png -gB16 -gb -gT! -gzl -ftb -fh!").wait()
        
        if os.path.exists("converted/data/ao-nds/background/"+bg+"/"+new_file):
            os.remove("converted/data/ao-nds/background/"+bg+"/"+new_file)
        os.rename("temp.img.bin", "converted/data/ao-nds/background/"+bg+"/"+new_file)

    # then convert desks. we won't bother with helper desks since these are mostly only used for special effects (source: GS4Night background)
    for imgfile, imgindex in [["defensedesk.png", 0], ["prosecutiondesk.png", 1], ["stand.png", 2], ["judgedesk.png", 3]]:
        full_filename = folder+"/background/"+bg+"/"+imgfile
        if not os.path.exists(full_filename):
            continue

        no_ext_file = os.path.splitext(imgfile)[0]

        img = Image.open(full_filename).convert("RGBA")
        if img.size[0] != 256 or img.size[1] != 192:
            img = img.resize((256, 192), Image.BICUBIC)

        # first, clear all semi-transparent pixels (must be either 0 or 255)
        pix = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pix[x, y][3] != 0 and pix[x, y][3] != 255:
                    pix[x, y] = (pix[x, y][0], pix[x, y][1], pix[x, y][2], 0 if pix[x, y][3] < 200 else 255)

        # find top image corner from top to bottom til we hit a visible pixel
        found = False
        top = 0
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pix[x, y][3] != 0:
                    top = y
                    found = True
                    break
            if found: break

        # crop corners
        img = img.crop((0, top, img.size[0], img.size[1]))

        # in the AA games on DS, desks are loaded as sprites.
        # the image width will be set to a size divisible by 64,
        # and the height will be set to a size divisible by 32
        # so that it can be loaded as 64x32 tiles
        horizontalTiles = int(math.ceil(img.size[0]/64.))
        verticalTiles = int(math.ceil(img.size[1]/32.))
        img = img.crop((0, img.size[1]-(verticalTiles*32), horizontalTiles*64, img.size[1]))

        img.save("temp.png")
        img.close()
        
        with open("converted/data/ao-nds/background/"+bg+"/desk_tiles.cfg", "a") as f:
            f.write("%s: %d,%d\n" % (no_ext_file, horizontalTiles, verticalTiles))

        # 16-bit, export to .img.bin, don't generate .h file, exclude map data, metatile height and width
        subprocess.Popen("./grit temp.png -gB8 -gt -ftb -fh! -m! -Mh4 -Mw8").wait()
        
        if os.path.exists("converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".img.bin"):
            os.remove("converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".img.bin")
        if os.path.exists("converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".pal.bin"):
            os.remove("converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".pal.bin")
        os.rename("temp.img.bin", "converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".img.bin")
        os.rename("temp.pal.bin", "converted/data/ao-nds/background/"+bg+"/"+no_ext_file+".pal.bin")


print("Backgrounds done.\n\nConverting characters...")
"""
a = images.load_apng(folder+"/characters/kristoph/(a)confident.apng")
pix = a[0][0].load()
middleWidth = 0
top = 0

found = False
for x in range(a[0][0].size[0]):
    for y in range(a[0][0].size[1]):
        if pix[x, y][3] != 0:
            middleWidth = x
            found = True
            break
    if found: break

found = False
for x in range(a[0][0].size[0]-1, -1, -1):
    for y in range(a[0][0].size[1]-1, -1, -1):
        if pix[x, y][3] != 0 and a[0][0].size[0]-1-x < middleWidth:
            middleWidth = a[0][0].size[0]-1-x
            found = True
            break
    if found: break

found = False
for y in range(a[0][0].size[1]):
    for x in range(a[0][0].size[0]):
        if pix[x, y][3] != 0:
            top = y
            found = True
            break
    if found: break

copy = None
copy = a[0][0].crop((middleWidth, top, a[0][0].size[0]-middleWidth, a[0][0].size[1]))
copy = copy.crop((0, 0, math.ceil(copy.size[0]/32.)*32, math.ceil(copy.size[1]/32.)*32))
#copy.show()
"""
# TO-DO


print("Converting evidence images...")
# TO-DO


print("Converting sounds...")
# TO-DO


print("Converting music...")
# TO-DO (use ffmpeg)


print("Cleaning up temporary files...")
os.remove("temp.png") # lmao

print("Done!")
print("Inside the folder named 'converted', you will see a folder named 'data'.")
print("Copy this 'data' folder to the root of your SD card.")
