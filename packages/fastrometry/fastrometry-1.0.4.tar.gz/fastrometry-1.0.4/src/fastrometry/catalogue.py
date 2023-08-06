from pathlib import Path
import csv
import numpy as np
from math import sin, cos, pi
from AstraCarta import astracarta
import sys, os

def getIntermediateCoords(ra, dec, scale, img_xmax, img_ymax, shape, filter, catalogue, pmepoch, nrefinepts, allintrmpoints, catalog_points, mean_catcoords, user_dir, debug_report, verbosity, debug):

    if not Path('{}\\gaiaqueries'.format(user_dir)).is_dir():
        if verbosity >= 1:
            print("| Creating {}\\gaiaqueries".format(user_dir))
        Path('{}\\gaiaqueries'.format(user_dir)).mkdir(parents=True)

    if verbosity == 0:
        silent = True
    else:
        silent = False

    resultsfilename = astracarta(ra=ra, dec=dec, scale=scale, maglimit=30, pixwidth=img_xmax, pixheight=img_ymax, shape=shape, filter=filter, catalogue=catalogue, pmepoch=pmepoch, nquery=nrefinepts, outdir=user_dir+'\\gaiaqueries\\', silent=silent)

    if resultsfilename == '':
        sys.exit("ERROR: Catalogue query failed to complete.")

    num_catsources = 0
    with open(resultsfilename, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for row in reader:
            catalog_points[num_catsources,0] = float(row['ra'])*pi/180
            catalog_points[num_catsources,1] = float(row['dec'])*pi/180
            num_catsources += 1

    if verbosity >= 1:
        print("| done")

    if verbosity == 2:
        print("| Got {} valid sky coordinates.".format(num_catsources))

    if verbosity >= 1:
        print("| Gnomonically projecting sky coordinates...")

    a0 = np.sum(catalog_points[:,0])/num_catsources
    a0deg = a0*pi/180

    d0 = np.sum(catalog_points[:,1])/num_catsources
    d0deg = d0*pi/180

    mean_catcoords[0] = a0
    mean_catcoords[1] = d0

    # Gnomonic projection. See e.g. https://apps.dtic.mil/sti/pdfs/ADA037381.pdf, beginning of chapter 6 for a derivation of the equations. The context
    # in the paper is creating a map projection of the earth's surface. Note that the derived equations on page 208 have the scale incorporated into them.
    # The scale factor "S" is the dimensionless ratio of map distance/earth distance, and "a" is the radius of the earth. Thus the x and y end up in map 
    # distance. In this program, the scale factor has units of radians/pixel (originally it is supplied by the user in arcseconds/pixel, but this is converted).
    # However, the scale factor is not included in the intermediate coordinate equations, so the intermediate coordinates are left dimensionless, or in radians.
    # The conversion to "map distance", or pixels in this case, comes later in the main part of the WCS solver, which uses the scale factor in the transformations.
    # In the forward transformations from pixels to intermediate coordinates, for example, a dimensional analysis would read: pixels X radians/pixel = radians,
    # which are the correct units of the intermediate coordinates.

    for k in range(num_catsources):
        a = catalog_points[k,0]
        d = catalog_points[k,1]
        X = (cos(d)*sin(a-a0) / (cos(d0)*cos(d)*cos(a-a0)+sin(d0)*sin(d)))
        Y = (cos(d0)*sin(d) - cos(d)*sin(d0)*cos(a-a0)) / (cos(d0)*cos(d)*cos(a-a0) + sin(d0)*sin(d))
        allintrmpoints[k,0] = X
        allintrmpoints[k,1] = Y
    
    if debug:
        np.savetxt(user_dir+"\\debug\\"+debug_report+"\\allintrmpoints.csv",allintrmpoints,delimiter=",")

    if debug:
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(13,7))

        axes_query = fig.add_subplot(121)
        axes_query.invert_xaxis()
        axes_query.axis('equal')
        axes_query.set_title('Sky coordinates')
        axes_query.set_xlabel('Right ascension (degrees)')
        axes_query.set_ylabel('Declination (degrees)')
        axes_query.scatter(catalog_points[:,0]*180/pi,catalog_points[:,1]*180/pi,marker=".",color='red')
        axes_query.scatter([a0deg],[d0deg],marker="x",color='black')

        axes_proj = fig.add_subplot(122)
        axes_proj.invert_xaxis()
        axes_proj.axis('equal')
        axes_proj.set_title('Intermediate coordinates')
        axes_proj.set_xlabel('X (radians)')
        axes_proj.set_ylabel('Y (radians)')
        axes_proj.scatter(allintrmpoints[:,0],allintrmpoints[:,1],marker=".",color='red')
        axes_proj.scatter([0],[0],marker="x",color='black')
        
        dscrp_query = "Sky coordinates obtained from the catalogue. When the RA and Dec axes are \nscaled equally, the resulting shape will be wider than it is tall, especially \nas declination approaches +- 90."
        dscrp_proj = "Intermediate coordinates, formed from taking the Gnomonic projection of the \ncatalog coordinates, using the mean of the coordinates as the projection \ncenter (invariant point)."
        plt.figtext(0.3, 0.08, dscrp_query, ha="center", fontsize=9)
        plt.figtext(0.72, 0.08, dscrp_proj, ha="center", fontsize=9)
        plt.subplots_adjust(wspace=0.2,left=0.08,right=0.92,bottom=0.25,top=0.9)
        plt.savefig(user_dir+"\\debug\\"+debug_report+"\\projection.png")
        plt.show()
    
    if verbosity >= 1:
        print("| done")

    return num_catsources