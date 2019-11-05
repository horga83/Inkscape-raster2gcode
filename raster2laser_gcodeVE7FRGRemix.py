'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day, 
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions') 

import subprocess
import math

import inkex
import png
import array


class GcodeExport(inkex.Effect):

######## 	Invoked by _main()
	def __init__(self):
		"""init the effect library and get options from gui"""
		inkex.Effect.__init__(self)
		
		# Image export options
		self.OptionParser.add_option("-d", "--directory",action="store", type="string", dest="directory", default="/home/",help="Directory for files") ####check_dir
		self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="-1.0", help="File name")            
		self.OptionParser.add_option("","--add-numeric-suffix-to-filename", action="store", type="inkbool", dest="add_numeric_suffix_to_filename", default=True,help="Add numeric suffix to filename")            
		self.OptionParser.add_option("","--bg_color",action="store",type="string",dest="bg_color",default="",help="")
		self.OptionParser.add_option("","--resolution",action="store", type="int", dest="resolution", default="5",help="") #Usare il valore su float(xy)/resolution e un case per i DPI dell export
		
		
		# How to convert to grayscale
		self.OptionParser.add_option("","--grayscale_type",action="store", type="int", dest="grayscale_type", default="1",help="") 
		
		# Conversion Mode in Black and White 
		self.OptionParser.add_option("","--conversion_type",action="store", type="int", dest="conversion_type", default="1",help="") 
		
		# Modal Options
		self.OptionParser.add_option("","--BW_Max",action="store", type="int", dest="BW_Max", default="255",help="") 
		self.OptionParser.add_option("","--Laser_Min",action="store", type="int", dest="Laser_Min", default="40",help="") 
		self.OptionParser.add_option("","--Dim_Test_Times",action="store", type="int", dest="Dim_Test_Times", default="3",help="") 
		self.OptionParser.add_option("","--BW_threshold",action="store", type="int", dest="BW_threshold", default="128",help="") 
		self.OptionParser.add_option("","--grayscale_resolution",action="store", type="int", dest="grayscale_resolution", default="1",help="") 
		
		#Black Velocity and Moving
		self.OptionParser.add_option("","--speed_ON",action="store", type="int", dest="speed_ON", default="1200",help="") 

		# Mirror Y
		self.OptionParser.add_option("","--flip_y",action="store", type="inkbool", dest="flip_y", default=False,help="")
		
		# Homing
		self.OptionParser.add_option("","--homing",action="store", type="int", dest="homing", default="4",help="")

		# Commands
		self.OptionParser.add_option("","--laseron", action="store", type="string", dest="laseron", default="M106", help="")
		self.OptionParser.add_option("","--laseroff", action="store", type="string", dest="laseroff", default="M107", help="")
		
		
		# Preview = BN image only
		self.OptionParser.add_option("","--preview_only",action="store", type="inkbool", dest="preview_only", default=False,help="") 

		#inkex.errormsg("BLA BLA BLA Message to display") #DEBUG

		
######## 	Invoked by __init __ ()
########	Here everything is done
	def effect(self):
		

		current_file = self.args[-1]
		bg_color = self.options.bg_color
		
		
		##Implementare check_dir
		
		if (os.path.isdir(self.options.directory)) == True:					
			
			##CODE THAT IS THE DIRECTORY
			#inkex.errormsg("OK") #DEBUG

			
			#I add a suffix to the filename to not overwrite the files
			if self.options.add_numeric_suffix_to_filename :
				dir_list = os.listdir(self.options.directory) #List all the files in the work directory
				temp_name =  self.options.filename
				max_n = 0
				for s in dir_list :
					r = re.match(r"^%s_0*(\d+)%s$"%(re.escape(temp_name),'.png' ), s)
					if r :
						max_n = max(max_n,int(r.group(1)))	
				self.options.filename = temp_name + "_" + ( "0"*(4-len(str(max_n+1))) + str(max_n+1) )


			#Generate file paths to use

			
			suffix = ""
			if self.options.conversion_type == 1:
				suffix = "_BWfix_"+str(self.options.BW_threshold)+"_"
			elif self.options.conversion_type == 2:
				suffix = "_BWrnd_"
			elif self.options.conversion_type == 3:
				suffix = "_H_"
			elif self.options.conversion_type == 4:
				suffix = "_Hrow_"
			elif self.options.conversion_type == 5:
				suffix = "_Hcol_"
			else:
				if self.options.grayscale_resolution == 1:
					suffix = "_Gray_256_"
				elif self.options.grayscale_resolution == 2:
					suffix = "_Gray_128_"
				elif self.options.grayscale_resolution == 4:
					suffix = "_Gray_64_"
				elif self.options.grayscale_resolution == 8:
					suffix = "_Gray_32_"
				elif self.options.grayscale_resolution == 16:
					suffix = "_Gray_16_"
				elif self.options.grayscale_resolution == 32:
					suffix = "_Gray_8_"
				else:
					suffix = "_Gray_"
				
			
			pos_file_png_exported = os.path.join(self.options.directory,self.options.filename+".png") 
			pos_file_png_BW = os.path.join(self.options.directory,self.options.filename+suffix+"preview.png") 
			pos_file_gcode = os.path.join(self.options.directory,self.options.filename+suffix+".gcode") 
			posDimTest_file_gcode = os.path.join(self.options.directory,self.options.filename+suffix+"DimTest.gcode") 			

			#Export the image to PNG
			self.exportPage(pos_file_png_exported,current_file,bg_color)


			
			#TO DO
			#Manipulate the PNG image to generate the Gcode file
			self.PNGtoGcode(pos_file_png_exported,pos_file_png_BW,pos_file_gcode)
			
			if self.options.Dim_Test_Times >= 1:
				self.exportDimensionTest(pos_file_png_exported, pos_file_png_BW, posDimTest_file_gcode)
			
		else:
			inkex.errormsg("Directory does not exist! Please specify existing directory!")
            

            
            
########	EXPORT IMAGE IN PNG		
######## 	Invoked by effect ()
		
	def exportPage(self,pos_file_png_exported,current_file,bg_color):		
		######## CREATING THE FILE PNG ########
		#Create the image inside the folder named "pos_file_png_exported"
		#-d 127 = resolution 127DPI => 5 pixels / mm 1pixel = 0.2mm
		###command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_exported,bg_color,current_file) 

		if self.options.resolution == 1:
			DPI = 25.4
		elif self.options.resolution == 2:
			DPI = 50.8
		elif self.options.resolution == 5:
			DPI = 127
		else:
			DPI = 254

		command="inkscape -C -e \"%s\" -b\"%s\" %s -d %s" % (pos_file_png_exported,bg_color,current_file,DPI) #Command from command line to export to PNG
					
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return_code = p.wait()
		f = p.stdout
		err = p.stderr

		
########	Create a dimensional test of image
	def exportDimensionTest(self,pos_file_png_exported,pos_file_png_BW,posDimTest_file_gcode):	
		#if self.options.Dim_Test_Times > 0:
			reader = png.Reader(pos_file_png_exported)#PNG files generated
			w, h, pixels, metadata = reader.read_flat()
			file_testgcode = open(posDimTest_file_gcode, 'w')  #Create the dimenstional test file
			file_testgcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n; by 305 Engineering\n; With a remix by VE7FRG\n;\n;\n')
			file_testgcode.write('G21; Set units to millimeters\n')			
			file_testgcode.write('G90; Use absolute coordinates\n')				
			file_testgcode.write('G92; Coordinate Offset\n')

			if self.options.homing == 1:
				file_gcode.write('G28 X0 Y0; home all axes\n')
				file_gcode.write('M42 P44 S0; Turn on LEDs\n')
				file_gcode.write('M42 P64 S0; Turn on VENT Fans\n')
			elif self.options.homing == 2:
				file_gcode.write('$H; home all axes\n')
			elif self.options.homing == 4:
				file_gcode.write('G28 X0 Y0; home all axes\n')
				file_gcode.write('G92 X-57 Y-37; Coordinate Offset for CR-10 Mini\n')
				file_gcode.write('G0 Z100; Set laser head 100mm above surface\n')
			else:
				pass

			file_testgcode.write(self.options.laseron + ' S' + str(self.options.Laser_Min) + '\n')
			file_testgcode.write('; This is the number of width: '+ str(w) + '\n')
			file_testgcode.write('; This is the number of height: '+ str(h) + '\n')
			file_testgcode.write('; This is the number of tests: '+ str(self.options.Dim_Test_Times) + '\n')
			file_testgcode.write('; This is the resolution number '+ str(self.options.resolution) + '\n')
			p=1
			while p <= self.options.Dim_Test_Times:
				file_testgcode.write('G1 X' + str(w / self.options.resolution) + '\n')
				file_testgcode.write('G1 Y' + str(h /  self.options.resolution) + '\n')
				file_testgcode.write('G1 X0\n')
				file_testgcode.write('G1 Y0\n')

				p = p+1
			file_testgcode.write(self.options.laseroff + '\n')
			file_testgcode.write('M42 P44 S255; Turn on LEDs\n')
			file_testgcode.close()
		

########	CREATE IMAGE IN B / W AND THEN GENERATE GCODE
######## 	Richiamata da effect()

	def PNGtoGcode(self,pos_file_png_exported,pos_file_png_BW,pos_file_gcode):
		
		######## CREATE IMAGE IN GRAY SCALE ########
		#I scroll the image and make it a list array

		reader = png.Reader(pos_file_png_exported)#PNG files generated
		
		w, h, pixels, metadata = reader.read_flat()
		
		
		matrice = [[255 for i in range(w)]for j in range(h)]  #List al posto di un array
		

		#I write a new image in 8bit Gray scale
		#Pixel by pixel copy 
		
		if self.options.grayscale_type == 1:
			#0.21R + 0.71G + 0.07B
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position]*0.21 + pixels[(pixel_position+1)]*0.71 + pixels[(pixel_position+2)]*0.07)
		
		elif self.options.grayscale_type == 2:
			#(R+G+B)/3
			for y in range(h): #Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int((pixels[pixel_position] + pixels[(pixel_position+1)]+ pixels[(pixel_position+2)]) / 3 )		

		elif self.options.grayscale_type == 3:
			#R
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position])			

		elif self.options.grayscale_type == 4:
			#G
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+1)])	
		
		elif self.options.grayscale_type == 5:
			#B
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+2)])				
			
		elif self.options.grayscale_type == 6:
			#Max Color
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(max(list_RGB))				

		else:
			#Min Color
			for y in range(h): # Y ranges from 0 to h-1
				for x in range(w): # X varies from 0 to w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(min(list_RGB))	
		

		####Master matrix contains the grayscale image


		######## GENERATE BLACK AND BLACK IMAGE ########
		#Scorro matrice and generate matrice_BN
		B=255
		N=0 
		
		matrice_BN = [[255 for i in range(w)]for j in range(h)]
		
		
		if self.options.conversion_type == 1:
			#B/W fixed threshold
			soglia = self.options.BW_threshold
			for y in range(h): 
				for x in range(w):
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
	
			
		elif self.options.conversion_type == 2:
			#B/W random threshold
			from random import randint
			for y in range(h): 
				for x in range(w): 
					soglia = randint(20,235)
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
			
			
		elif self.options.conversion_type == 3:
			#Halftone
			Step1 = [[B,B,B,B,B],[B,B,B,B,B],[B,B,N,B,B],[B,B,B,B,B],[B,B,B,B,B]]
			Step2 = [[B,B,B,B,B],[B,B,N,B,B],[B,N,N,N,B],[B,B,N,B,B],[B,B,B,B,B]]
			Step3 = [[B,B,N,B,B],[B,N,N,N,B],[N,N,N,N,N],[B,N,N,N,B],[B,B,N,B,B]]
			Step4 = [[B,N,N,N,B],[N,N,N,N,N],[N,N,N,N,N],[N,N,N,N,N],[B,N,N,N,B]]
			
			for y in range(h/5): 
				for x in range(w/5): 
					media = 0
					for y2 in range(5):
						for x2 in range(5):
							media +=  matrice[y*5+y2][x*5+x2]
					media = media /25
					for y3 in range(5):
						for x3 in range(5):
							if media >= 250 and media <= 255:
								matrice_BN[y*5+y3][x*5+x3] = 	B	
							if media >= 190 and media < 250:
								matrice_BN[y*5+y3][x*5+x3] =	Step1[y3][x3]
							if media >= 130 and media < 190:
								matrice_BN[y*5+y3][x*5+x3] =	Step2[y3][x3]
							if media >= 70 and media < 130:
								matrice_BN[y*5+y3][x*5+x3] =	Step3[y3][x3]
							if media >= 10 and media < 70:
								matrice_BN[y*5+y3][x*5+x3] =	Step4[y3][x3]		
							if media >= 0 and media < 10:
								matrice_BN[y*5+y3][x*5+x3] = N


		elif self.options.conversion_type == 4:
			#Halftone row
			Step1r = [B,B,N,B,B]
			Step2r = [B,N,N,B,B]
			Step3r = [B,N,N,N,B]
			Step4r = [N,N,N,N,B]

			for y in range(h): 
				for x in range(w/5): 
					media = 0
					for x2 in range(5):
						media +=  matrice[y][x*5+x2]
					media = media /5
					for x3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y][x*5+x3] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y][x*5+x3] =	Step1r[x3]
						if media >= 130 and media < 190:
							matrice_BN[y][x*5+x3] =	Step2r[x3]
						if media >= 70 and media < 130:
							matrice_BN[y][x*5+x3] =	Step3r[x3]
						if media >= 10 and media < 70:
							matrice_BN[y][x*5+x3] =	Step4r[x3]		
						if media >= 0 and media < 10:
							matrice_BN[y][x*5+x3] = N			


		elif self.options.conversion_type == 5:
			#Halftone column
			Step1c = [B,B,N,B,B]
			Step2c = [B,N,N,B,B]
			Step3c = [B,N,N,N,B]
			Step4c = [N,N,N,N,B]

			for y in range(h/5):
				for x in range(w):
					media = 0
					for y2 in range(5):
						media +=  matrice[y*5+y2][x]
					media = media /5
					for y3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y*5+y3][x] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y*5+y3][x] =	Step1c[y3]
						if media >= 130 and media < 190:
							matrice_BN[y*5+y3][x] =	Step2c[y3]
						if media >= 70 and media < 130:
							matrice_BN[y*5+y3][x] =	Step3c[y3]
						if media >= 10 and media < 70:
							matrice_BN[y*5+y3][x] =	Step4c[y3]		
						if media >= 0 and media < 10:
							matrice_BN[y*5+y3][x] = N			
			
		else:
			#Grayscale
			if self.options.grayscale_resolution == 1:
				matrice_BN = matrice
			else:
				for y in range(h): 
					for x in range(w): 
						if matrice[y][x] <= 1:
							matrice_BN[y][x] == 0
							
						if matrice[y][x] >= 254:
							matrice_BN[y][x] == 255
						
						if matrice[y][x] > 1 and matrice[y][x] <254:
							matrice_BN[y][x] = ( matrice[y][x] // self.options.grayscale_resolution ) * self.options.grayscale_resolution
						
			
			
		####Ora matrice_BN contiene l'immagine in Bianco (255) e Nero (0)


		#### SAVE BLACK AND BLACK IMAGE ####
		file_img_BN = open(pos_file_png_BW, 'wb') #Create the file
		Costruttore_img = png.Writer(w, h, greyscale=True, bitdepth=8) #Setting the image file
		Costruttore_img.write(file_img_BN, matrice_BN) #Image file builder
		file_img_BN.close()	#Close the file


		#### GENERO IL FILE GCODE ####	
		if self.options.preview_only == False: #Genero Gcode solo se devo
		
			if self.options.flip_y == False: #Inverto asse Y solo se flip_y = False     
				#-> coordinate Cartesiane (False) Coordinate "informatiche" (True)
				matrice_BN.reverse()				

			
			Laser_ON = False
			F_G01 = self.options.speed_ON
			Scala = self.options.resolution
			Scaler = float(self.options.BW_Max)/255

			file_gcode = open(pos_file_gcode, 'w')  #Create the file
			
			#Configurazioni iniziali standard Gcode
			file_gcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n; by 305 Engineering\n; With a remix by VE7FRG\n;\n;\n')
			#HOMING

			file_gcode.write('G21; Set units to millimeters\n')
			file_gcode.write('G90; Use absolute coordinates\n')
			file_gcode.write('G92; Coordinate Offset\n')
			if self.options.homing == 1:
				file_gcode.write('G28 X0 Y0; home all axes\n')
				file_gcode.write('M42 P44 S0; Turn on LEDs\n')
				file_gcode.write('M42 P64 S0; Turn on VENT Fans\n')
			elif self.options.homing == 2:
				file_gcode.write('$H; home all axes\n')
			elif self.options.homing == 4:
				file_gcode.write('G28 X0 Y0; home all axes\n')
				file_gcode.write('G92 X-57 Y-37; Coordinate Offset for CR-10 Mini\n')
				file_gcode.write('G0 Z100; Set laser head 100mm above surface\n')
			else:
				pass

#			file_gcode.write('G90; Use absolute coordinates\n')
#			file_gcode.write('G92; Coordinate Offset\n')

			#Creazione del Gcode
			
			#allargo la matrice per lavorare su tutta l'immagine
			for y in range(h):
				matrice_BN[y].append(B)
			w = w+1
			
			if self.options.conversion_type != 6:
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
									file_gcode.write(self.options.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 :
										file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x+1] != N :
											file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False
					else:
						for x in reversed(range(w)):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
									file_gcode.write(self.options.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 :
										file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x-1] != N :
											file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False				

			else: ##SCALA DI GRIGI
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
									file_gcode.write(self.options.laseron + ' '+ ' S' + str(int(round(float((255 - matrice_BN[y][x])*Scaler)))) +'\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 : #controllo fine riga
										file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x+1] == B :
											file_gcode.write('G1 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False
											
										elif matrice_BN[y][x] != matrice_BN[y][x+1] :
											file_gcode.write('G1 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.options.laseron + ' '+ ' S' + str(int(round(float((255 - matrice_BN[y][x])*Scaler)))) +'\n')									

					
					else:
						for x in reversed(range(w)):
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									file_gcode.write('G00 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
									#file_gcode.write(self.options.laseron + ' '+ ' S' + str(self.options.BW_Max - matrice_BN[y][x]) +'\n')
									file_gcode.write(self.options.laseron + ' '+ ' S' + str(int(round(float((255 - matrice_BN[y][x])*Scaler)))) +'\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 : #controllo fine riga ritorno
										file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.options.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x-1] == B :
											file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.options.laseroff + '\n')
											Laser_ON = False
											
										elif  matrice_BN[y][x] != matrice_BN[y][x-1] :
											file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											#file_gcode.write(self.options.laseron + ' '+ ' S' + str(self.options.BW_Max - matrice_BN[y][x-1]) +'\n')
											file_gcode.write(self.options.laseron + ' '+ ' S' + str(int(round(float((255 - matrice_BN[y][x])*Scaler)))) +'\n')

			
			
			#Configurazioni finali standard Gcode
			file_gcode.write('G00 X0 Y0; home\n')
			#HOMING
			if self.options.homing == 1:
				file_gcode.write('G28 X0 Y0; home all axes\n')
				file_gcode.write('M42 P44 S255; Turn on LEDs\n')
				file_gcode.write('M42 P64 S255; Turn on VENT Fans\n')
			elif self.options.homing == 2:
				file_gcode.write('$H; home all axes\n')
			else:
				pass
			
			file_gcode.close() #Chiudo il file




######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	


def _main():
	e=GcodeExport()
	e.affect()
	
	exit()

if __name__=="__main__":
	_main()







