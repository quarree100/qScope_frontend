# pygame notes

2022-05-29

- pygame tutorials: https://www.pygame.org/docs/#tutorials

## alpha on viewport surface?
https://stackoverflow.com/questions/62505797/setting-an-alpha-on-a-pygame-surface

> There are three different kinds of transparency supported in pygame: colorkeys, surface alphas, and pixel alphas; and you can't easily mix surface alphas and pixel alphas
> If you want to use set_alpha to set the transparency of the entire Surface, you use surface alpha (that means setting, well, the alpha value of the entire surface).
> But the image you want to use is a PNG which uses pixel alpha (that means each pixel has its own alpha value); so you should call convert_alpha on the Surface after loading so the image.

### option 1: use a color key (for entire surface?)

### option 2: use a temporary surface and BLEND_RGBA_MULT to apply transparency (for entire surface?)

---

## setting image pixel transparency

- define which pixels should be transparent (a.k.a "not be blitted"): `self.image.set_colorkey((0, 0, 0))`
- works with .tif files; .png show alpha channel as white pixels

### [Pygame Transparency](https://riptutorial.com/pygame/example/23788/transparency)

---

### using sprites

pygame documentation: [Sprite Module Introduction](https://www.pygame.org/docs/tut/SpriteIntro.html)

- Sprite Class
- Group Class

