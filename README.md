# Various Inkscape extensions

 - Raster 2 Laser GCode generator
 - Some changes I made:
 -   Included additions from Chandler Customs such as turning on fan, adjusting laser power and dimensioning
 -   Added additional home for CR-10 Mini with a 2.5W laser
 -     Homes the head
 -     Changes the 0,0 offset to X-57 and Y-37 so the 0,0 head position is correct
 -     Changes the Z height to 100mm which is what my laser requires.


#Descriptions
- Raster 2 Laser GCode generator is an extension to generate Gcode for a laser cutter/engraver (or pen plotter), it can generate various type of outputs from a simple B&W (on/off) to a more detailed Grayscale (pwm)


#Installing:

Simply copy all the files in the folder "Extensions" of Inkscape

>Windows ) "C:\<...>\Inkscape\share\extensions"

>Linux ) "/usr/share/inkscape/extensions"

>Mac ) "/Applications/Inkscape.app/Contents/Resources/extensions"


for unix (& mac maybe) change the permission on the file:

>>chmod 755 for all the *.py files

>>chmod 644 for all the *.inx files



#Usage of "Raster 2 Laser GCode generator":

[Required file: png.py / raster2laser_gcode.inx / raster2laser_gcode.py]

- Step 1) Resize the inkscape document to match the dimension of your working area on the laser cutter/engraver (Shift+Ctrl+D)

- Step 2) Draw or import the image

- Step 3) To run the extension go to: Extension > 305 Engineering + VE7FRG > Raster 2 Laser GCode generator

- Step 4) Play!




#Note
I have created all the file except for png.py , see that file for details on the license
