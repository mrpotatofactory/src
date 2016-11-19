from toontown.toonbase.ToontownGlobals import *
wainscottingBase = [
    Vec4(0.80000000000000004, 0.5, 0.29999999999999999, 1.0),
    Vec4(0.69899999999999995, 0.58599999999999997, 0.47299999999999998, 1.0),
    Vec4(0.47299999999999998, 0.69899999999999995, 0.48799999999999999, 1.0)]
wallpaperBase = [
    Vec4(1.0, 1.0, 0.69999999999999996, 1.0),
    Vec4(0.78900000000000003, 1.0, 0.69899999999999995, 1.0),
    Vec4(1.0, 0.81999999999999995, 0.69899999999999995, 1.0)]
wallpaperBorderBase = [
    Vec4(1.0, 1.0, 0.69999999999999996, 1.0),
    Vec4(0.78900000000000003, 1.0, 0.69899999999999995, 1.0),
    Vec4(1.0, 0.81999999999999995, 0.69899999999999995, 1.0)]
doorBase = [
    Vec4(1.0, 1.0, 0.69999999999999996, 1.0)]
floorBase = [
    Vec4(0.746, 1.0, 0.47699999999999998, 1.0),
    Vec4(1.0, 0.68400000000000005, 0.47699999999999998, 1.0)]
baseScheme = {
    'TI_wainscotting': wainscottingBase,
    'TI_wallpaper': wallpaperBase,
    'TI_wallpaper_border': wallpaperBorderBase,
    'TI_door': doorBase,
    'TI_floor': floorBase }
colors = {
    DonaldsDock: baseScheme,
    ToontownCentral: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': wallpaperBase,
        'TI_wallpaper_border': wallpaperBorderBase,
        'TI_door': doorBase + [
            Vec4(0.80000000000000004, 0.5, 0.29999999999999999, 1.0)],
        'TI_floor': floorBase },
    TheBrrrgh: baseScheme,
    MinniesMelodyland: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': [
            Vec4(1.0, 1.0, 0.69, 1.0),
            Vec4(1.0, 0.82, 0.6, 1.0)],
        'TI_wallpaper_border': [
            Vec4(1.0, 1.0, 0.69, 1.0),
            Vec4(1.0, 0.82, 0.6, 1.0)],
        'TI_door': doorBase,
        'TI_floor': floorBase },
    DaisyGardens: baseScheme,
    DonaldsDreamland: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': wallpaperBase + [
            Vec4(0.50000000000000004, 0.5, 0.69999999999999999, 1.0)],
        'TI_wallpaper_border': wallpaperBorderBase + [
            Vec4(0.70000000000000004, 0.7, 0.99999999999999999, 1.0)],
        'TI_door': doorBase,
        'TI_floor': floorBase },
    Tutorial: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': wallpaperBase,
        'TI_wallpaper_border': wallpaperBorderBase,
        'TI_door': doorBase + [
            Vec4(0.80000000000000004, 0.5, 0.29999999999999999, 1.0)],
        'TI_floor': floorBase },
    MyEstate: baseScheme,
    FunnyFarm: baseScheme,
}
