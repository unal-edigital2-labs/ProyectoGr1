#!/usr/bin/env python3

from migen import *
from migen.genlib.io import CRG
from migen.genlib.cdc import MultiReg

## debe dejar solo una tarjeta
#import tarjetas.digilent_nexys4 as tarjeta # si usa tarjeta nexy 4 
import tarjetas.nexys4ddr as tarjeta # si usa tarjeta nexy 4 4DRR
# import tarjetas.digilent_zybo_z7 as tarjeta # si usa tarjeta zybo z7
# import tarjetas.c4e6e10 as tarjeta

#from module import servo


from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.cores import pwm
from litex.soc.cores import gpio
from module import rgbled
from module import vgacontroller
from module	import	camera
from module.display import SevenSegmentDisplay

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
	def __init__(self):
		sys_clk_freq = int(100e6)
		platform = tarjeta.Platform()

		#platform.add_source("module/verilog/servomotor.v")
		# SoC with CPU
		SoCCore.__init__(self, platform,
# 			cpu_type="picorv32",
			cpu_type="vexriscv",
			clk_freq=100e6,
			integrated_rom_size=0x8000,
			integrated_sram_size=0x1000,
			integrated_main_ram_size=200*1024)

		# Clock Reset Generation
		self.submodules.crg = CRG(platform.request("clk"), ~platform.request("cpu_reset"))

		# Leds
		SoCCore.add_csr(self,"leds")
		user_leds = Cat(*[platform.request("led", i) for i in range(8)])
		self.submodules.leds = gpio.GPIOOut(user_leds)
		
		# Switchs
		SoCCore.add_csr(self,"switchs")
		user_switchs = Cat(*[platform.request("sw", i) for i in range(4)])
		self.submodules.switchs = gpio.GPIOIn(user_switchs)
		
		# Buttons
		SoCCore.add_csr(self,"buttons")
		user_buttons = Cat(*[platform.request("btn%c" %c) for c in ['c','d','u']])
		self.submodules.buttons = gpio.GPIOIn(user_buttons)
		

		# RGB leds
		SoCCore.add_csr(self,"ledRGB_1")
		self.submodules.ledRGB_1 = rgbled.RGBLed(platform.request("ledRGB",1))
		
		SoCCore.add_csr(self,"ledRGB_2")
		self.submodules.ledRGB_2 = rgbled.RGBLed(platform.request("ledRGB",2))
		
		# 7segments Display para zybo z7 comentar 
  
		self.submodules.display = SevenSegmentDisplay(sys_clk_freq)
		self.add_csr("display")
		self.comb += [
          platform.request("display_cs_n").eq(~self.display.cs),
           platform.request("display_abcdefg").eq(~self.display.abcdefg)
   	]		

		
		# Servomotor
		#SoCCore.add_csr(self,"servomotor_cntrl")
		#self.submodules.servomotor_cntrl = servo.servomotor(platform.request("servo"))
		#PWM
		SoCCore.add_csr(self,"PWM")
		self.submodules.PWM = pwm.PWM(platform.request("pwm__",1))
		# VGA para zybo z7 comentar 
#		SoCCore.add_csr(self,"vga_cntrl")
#		vga_red = Cat(*[platform.request("vga_red", i) for i in range(4)])
#		vga_green = Cat(*[platform.request("vga_green", i) for i in range(4)])
#		vga_blue = Cat(*[platform.request("vga_blue", i) for i in range(4)])
#		self.submodules.vga_cntrl = vgacontroller.VGAcontroller(platform.request("hsync"),platform.request("vsync"), vga_red, vga_green, vga_blue)

# Build --------------------------------------------------------------------------------------------
if __name__ == "__main__":
	builder = Builder(BaseSoC(),output_dir="build", csr_csv="csr.csv")
	builder.build(build_name="top")

