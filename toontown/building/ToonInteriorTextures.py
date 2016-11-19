from toontown.toonbase.ToontownGlobals import *
wainscottingBase = [
    "phase_3.5/maps/wall_paper_b2.jpg",
    "phase_3.5/maps/wall_paper_b3.jpg",
    "phase_3.5/maps/wall_paper_b4.jpg"]
wallpaperBase = [
    "phase_3.5/maps/stripeB5.jpg",
    "phase_5.5/maps/big_stripes2.jpg",
    "phase_5.5/maps/squiggle1.jpg",
    "phase_5.5/maps/diamonds2_cherries.jpg",
    "phase_5.5/maps/stripes_green.jpg",
    "phase_5.5/maps/two_stripes1.jpg",
    "phase_3.5/maps/wall_paper_a5.jpg"]
wallpaperBorderBase = [
    "phase_5.5/maps/diamonds_border2.jpg",
    "phase_5.5/maps/bd_grey_border1.jpg",
    "phase_3.5/maps/wall_paper_b3.jpg"]
moldingBase = [
    "phase_3.5/maps/molding_wood1.jpg",
    "phase_3.5/maps/molding_wood2.jpg"]
couchBase = [
    "phase_3.5/maps/couch.jpg",
    "phase_3.5/maps/couch2.jpg",
    "phase_3.5/maps/couch3.jpg"]
floorBase = [
    "phase_3.5/maps/floor_wood.jpg",
    "phase_3.5/maps/carpet.jpg"]
baseScheme = {
    'TI_wainscotting': wainscottingBase,
    'TI_wallpaper': wallpaperBase,
    'TI_wallpaper_border': wallpaperBorderBase,
    'TI_molding': moldingBase,
    'TI_couch': couchBase,
    'TI_floor': floorBase  }
textures = {
    DonaldsDock: baseScheme,
    ToontownCentral: baseScheme,
    TheBrrrgh: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': [
            "phase_5.5/maps/big_stripes3.jpg",
            "phase_5.5/maps/diamonds3_cherries.jpg",
            "phase_5.5/maps/squiggle2.jpg",
            "phase_5.5/maps/squiggle5.jpg",
            "phase_5.5/maps/stripes_cyan.jpg",
            "phase_5.5/maps/stripeB1.jpg"],
        'TI_wallpaper_border': [
            "phase_5.5/maps/diamonds_border3ch.jpg",
            "phase_5.5/maps/bd_grey_border1.jpg"],
        'TI_molding': moldingBase,
        'TI_couch': couchBase,
        'TI_floor': floorBase  },
    MinniesMelodyland: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': [
            "phase_5.5/maps/big_stripes5.jpg",
            "phase_5.5/maps/diamonds2_cherries.jpg",
            "phase_5.5/maps/squiggle1.jpg",
            "phase_5.5/maps/squiggle6.jpg",
            "phase_5.5/maps/stripes_magenta.jpg",
            "phase_5.5/maps/stripeB6.jpg",
            "phase_3.5/maps/wall_paper_a5.jpg"],
        'TI_wallpaper_border': [
            "phase_5.5/maps/diamonds_border2.jpg",
            "phase_5.5/maps/bd_grey_border1.jpg"],
        'TI_molding': moldingBase,
        'TI_couch': couchBase,
        'TI_floor': floorBase  },
    DaisyGardens: baseScheme,
    DonaldsDreamland: {
        'TI_wainscotting': wainscottingBase,
        'TI_wallpaper': [
            "phase_5.5/maps/big_stripes3.jpg",
            "phase_5.5/maps/diamonds6_cherry.jpg",
            "phase_5.5/maps/diamonds5_cherries.jpg",
            "phase_5.5/maps/squiggle4.jpg",
            "phase_5.5/maps/stripeB7.jpg",
            "phase_3.5/maps/wall_paper_a5.jpg"],
        'TI_wallpaper_border': [
            "phase_5.5/maps/diamonds_border3ch.jpg",
            "phase_5.5/maps/bd_grey_border1.jpg"],
        'TI_molding': moldingBase,
        'TI_couch': couchBase,
        'TI_floor': floorBase  },
    Tutorial: baseScheme,
    MyEstate: baseScheme,
    FunnyFarm: baseScheme,
}