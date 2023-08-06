import random

def wallpaper():
    images = [
        "https://ibb.co/mR307kP",
        "https://ibb.co/mXRJrsM",
        "https://ibb.co/g32XxfX",
        "https://ibb.co/h93fP65",
        "https://ibb.co/VNLVmSf",
        "https://ibb.co/GnMzgr0",
        "https://ibb.co/k3qskcW",
        "https://ibb.co/6v5dwrS",
        "https://ibb.co/rmkxPfy",
        "https://ibb.co/thNhnVF",
        "https://ibb.co/BcZCzfp",
        "https://ibb.co/sbnzs0c",
        "https://ibb.co/njyRGYr",
        "https://ibb.co/XWMQfBd",
        "https://ibb.co/RHC83qQ",
        "https://ibb.co/NWwvCdQ",
        "https://ibb.co/pdBYdpW",
        "https://ibb.co/cFTfSLv",
        "https://ibb.co/1svzj88",
        "https://ibb.co/x27cdbp",
        "https://ibb.co/Gc0ptr9",
        "https://ibb.co/c1bbdNF",
        "https://ibb.co/yp1tNVV",
        "https://ibb.co/KKFpyjh",
        "https://ibb.co/zPgvQ5x",
        "https://ibb.co/mBZxfQw",
        "https://ibb.co/Gp2t0nM",
        "https://ibb.co/kG2LsnK",
        "https://ibb.co/KNkk39V",
        "https://ibb.co/Ct2Ny1R",
        "https://ibb.co/pZcNKb8",
        "https://ibb.co/T2mcxWP",
        "https://ibb.co/J33nDJv",
        "https://ibb.co/KbDjCqQ",
        "https://ibb.co/nRTdGWM",
        "https://ibb.co/9wzmg9k"
    ]
    
    image = random.choice(images)
    return image

print(wallpaper())