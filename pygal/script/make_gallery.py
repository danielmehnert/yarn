import os
from PIL import Image

imagetypes = ["PNG", "JPEG", "JPG", "GIF"]

def thumb_from_image(img):
    size = 128, 128
    filename, ext = os.path.splitext(img)
    im = Image.open(img)
    im.thumbnail(size)
    if "JPG" in ext.upper() or "JPEG" in ext.upper():
        im.save(filename + "_thumb"+ext, "JPEG")
    if "PNG" in ext.upper():
        im.save(filename + "_thumb"+ext, "PNG")
    if "GIF" in ext.upper():
        im.save(filename + "_thumb"+ext, "GIF")

def make_thumbs(imagedir):
    for img in os.listdir(imagedir):
        if "thumb" not in img:
            if os.path.splitext(img)[1][1:].upper() in imagetypes:
                thumb_from_image(os.path.join(imagedir, img))
    return 0

def build_website(header, footer, imagepath, outpath = "../"):
    content = []
    with open(header) as i:
        content.append(i.read())
    images = ""
    namecount = 0
    make_thumbs(imagepath)
    for img in sorted(os.listdir(imagepath)):
        if img.split(".")[-1].upper() in imagetypes and "thumb" not in img:
            
            images += '<a href="./img/{}" class="thumb_link"><span class="selected"></span><img src="./img/{}" title="{}" alt="{}" class="thumb" /></a>'.format(img, "_thumb".join(os.path.splitext(img)), namecount, namecount) + "\n"
            namecount += 1
    content.append(images)
    with open(footer) as i:
        content.append(i.read())
    with open(os.path.join(outpath, "gallery.html"), "w") as o:
        o.write("\n".join(content))
    return 0
    
    
def build_website_2(header, footer, imagepath, outpath="../"):
    content = []
    with open(header) as i:
        content.append(i.read())
    images = ""
    namecount = 0
    make_thumbs(imagepath)
    for imgc, img in enumerate(sorted(os.listdir(imagepath))):
        if img.split(".")[-1].upper() in imagetypes and "thumb" not in img:
            if imgc == 0:
                preview = "./img/"+img
                content = [preview.join(content[0].split("{{PREVIEW}}"))]
            
            images += '<div class="content">\n<div><a href="./img/{}"><img src="./img/{}" title="{}" alt="{}" class="thumb" /></a></div>\n</div>'.format(img, "_thumb".join(os.path.splitext(img)), namecount, namecount) + "\n"
            namecount += 1
    content.append(images)
    with open(footer) as i:
        content.append(i.read())
    with open(os.path.join(outpath, "simplegallery.html"), "w") as o:
        o.write("\n".join(content))
    return 0
    
    
    
if __name__ == "__main__":
    build_website_2("header2.txt", "footer2.txt", r"/home/pi/dev/images/img")
        
