import serial
import threading
import time
import math
from sys import stdin
import socket
class QuadController():



	"""docstring for QuadController: set quad focus co-ordinates using setCenter and
	 use the target function to make the quad fly and focus on new co-ordinates"""

	def __init__(self,SerialPort,SerialSpeed):


		
		self.debugging=False

		self.autopilot=False

		self.kill_deamons=0

		self.SerialPort = SerialPort

		self.SerialSpeed = SerialSpeed

		self.tmax = 0x7F # 127

		self.tmin = 0x0A # 10

		self.emax = 300

		self.emin = 20

		self.oldXerror = 0

		self.oldYerror = 0

		self.ySummation=0

		self.xSummation=0

		self.kd = 5

		self.ki = 1000.0

		self.bound =False

		self.ser=0

		self.x = 0

		self.y = 0

		self.prev_command_val={'p':0,'r':0,'y':0,'t':0x7a};

		self.commander = {\
				'b':[self.bind,False],\
				's':self.kickstart,\
				'q':[self.up,80],\
				'e':[self.down,122],\
				'5':[self.up,60],\
				'0':[self.down,30],\
				'w':[self.up,0],\
				'8':[self.forward,120],\
				'i':[self.forward,75],\
				'2':[self.back,120],\
				'k':[self.back,75],\
				'p':[self.forward,0],\
				'4':[self.left,120],\
				'j':[self.left,75],\
				'6':[self.right,120],\
				'l':[self.right,75],\
				'o':[self.right,0],\
				'a':[self.yaw,50],\
				'd':[self.yaw,-50],\
				'f':[self.yaw,0],\
				'y':[self.set_autopilot,False],\
				't':[self.set_autopilot,True],\
				'+':[self.set_debugging,True],\
				'!':[self.set_debugging,False],\
				'`':self.quit,\
				'|':self.keepalive,\
				}

		self.serialController = threading.Thread(target=self.serialDeamon)
		self.serialController.deamon = True
		self.serialController.start()

		self.udp_client_lost=5
		self.udpController = threading.Thread(target=self.UdpDeamon)
		self.udpController.deamon=True
		self.udpController.start()

		self.updatedThrotle = ''
		self.newThrotleAvailable=threading.Event()
		self.throtlesController = threading.Thread(target=self.throtlesDeamon)
		self.throtlesController.deamon=True
		#self.throtlesController.start()

		self.started_at=time.time()

		self.r = open("yperror.dat",'a+')
		self.r2 = open("yerror.dat",'a+')


	def serialDeamon(self):

		try:

			self.ser =  serial.Serial(self.SerialPort, self.SerialSpeed, timeout=2)

		except serial.SerialException as e:

			self.kill_deamons=1
			print("[-] Serial port unreachable")
			return 0

		print "[-] Started Serial listener at port ",self.SerialPort,":",self.SerialSpeed

		while not self.kill_deamons:

			try:
				line=self.ser.readline();


				if line:
					print("[+] "+line);
					reply = 'me-?-?-'
					try:
						self.sock.sendto(reply+line,self.addr)
					except:
						pass
				if self.autopilot==True and self.bound==True:
					if(time.time()-self.last_point>2):
						self.log("Autopilot is not getting co-ordinates,quiting..")
						self.log("Last Autopilot command received at:"+str(time.time()-self.last_point)+" seconds ago")
						print 'Autopilot is not getting co-ordinates,quiting..'
						self.quit();
			except:

				self.kill_deamons=1
		else:
			self.ser.close()



		print ("[-] Serial Deamon got killed !!!")
		self.log("Serial deamon killed")


	def right(self,value):

		value = 0 if value < 1 else value+127

		self.write_command('r',value)

	def yaw(self,value):

		value=value if abs(value) < 128 else -127 if value < -127 else 127

		value = abs(value) if value < 0 else value+128 if value >0 else 0

		self.write_command('y',value)

	def left(self,value):

		value=127 if value>127 else value

		self.write_command('r',value)

	def forward(self,value):# value = 0 - 127

		value=127 if value>127 else value

		self.write_command('p',value)

	def back(self,value):

		value = 0 if value < 1 else value+127

		self.write_command('p',value)

	def up(self,value):#0-133

		value= 0 if value < 0 else value+122

		self.write_command('t',value)

	def down(self,value):#0-122

		value=122 if value>122 else 0 if value < 1 else value
		if value==122:
			
			self.set_autopilot(False)

		value = 122-value
		
		self.write_command('t',value)

	def write_command(self,command,value):

		value = 0 if value < 1 else value

		value=int(math.ceil(value))

		value=255 if value>255 else value

		if command in self.prev_command_val: #['p','r','y','t']:

			if self.prev_command_val[command] is value:

				return

			self.prev_command_val[command] = value

			#self.updatedThrotle=command

			#self.newThrotleAvailable.set()

			#return

			if self.debugging==False:
					try:
						self.sock.sendto("me-?-?-P:%3s R:%3s Y:%3s T:%3s"%(self.prev_command_val['p'],self.prev_command_val['r'],self.prev_command_val['y'],self.prev_command_val['t']),self.addr)
					except:
						pass

		try:
			self.ser.write(bytearray([command,value]))
		except:
			print'[-] Unable to send command(',command,':',value,')via serial'

	def setCenter(self,x,y):

		self.x=x
		self.y=y

	def target(self,tx,ty):

		if self.bound and self.autopilot==True:

			xperror = tx-self.x # x error in pixels
			yperror = self.y-ty # y error in pixels

			xerror = self.pdx(xperror) # apply pd controller to roll

			xerror = self.maper(xerror) # map x error from pixels to quad distance error

			xerror = self.pidx(xerror)

			if xerror>0: # positive error along +ve x-axis

				self.right(xerror)

			else:

				self.left(abs(xerror))

			yerror = self.pdy(yperror) # apply pd controller to pitch

			yerror = self.maper(yerror) # map y error from pixels to quad distance error

			yerror = self.pidy(yerror)

			if yerror>0: # positive error along +ve y-axis

				self.forward(yerror)

			else:

				self.back(abs(yerror))

			self.last_point = time.time()


			self.r.write(str(yperror)+',')

			self.r2.write(str(yerror)+',')

	def maper(self,value):

		if value < 0:
			sign=-1
		else:
			sign=1

		value = abs(value)

		value = self.emin if value<self.emin else self.emax if value>self.emax else value

		ret= (value - self.emin) * (self.tmax - self.tmin+0.0) / (self.emax - self.emin) + self.tmin

		return ret*sign

	def setThrust(self,max,min):

		self.tmax = max # 127
		self.tmin = min # 0

	def setRange(self,max,min):

		self.emax = max # 300
		self.emin = min # 30

	def pidx(self,xerror):

		self.xSummation +=(xerror+0.0)/self.ki

		return xerror+self.xSummation

	def pidy(self,yerror):

		self.ySummation +=(yerror+0.0)/self.ki

		return yerror+self.ySummation

	def pdx(self,xerror):

		ret =  xerror + self.kd*(xerror-self.oldXerror)

		self.oldXerror = xerror

		return ret

	def pdy(self,yerror):

		ret =  yerror + self.kd*(yerror-self.oldYerror)

		self.oldYerror = yerror

		return ret

	def bind(self,ask=True):

		if not self.bound:

			print "[-] Binding started..."
			self.write_command('b',1)
			self.bound=True
		else:

			if ask:
				print "[-] Already bound! (y to rebind) :"

				if stdin.read(1)=='y':
					self.bound=0
					self.bind()
				else:
					print "[-] Okay, not binding."
			else:
				self.bound=0
				self.bind()

	def kickstart(self):
		self.write_command('s',1)
	def quit(self):
		self.kill_deamons=True
		self.autopilot=False
		self.clearAll()
		self.down(122)
	def keepalive(self):
		10
	def clearAll(self):
		self.write_command('r',0)
		self.write_command('p',0)
		self.write_command('y',0)
		self.pdx(0)
		self.pdy(0)
		self.ySummation=0
		self.xSummation=0

	def set_autopilot(self,val):
		self.last_point = time.time()
		self.autopilot=val
		print "[-] Autopilot is",val
		if not val:
			self.clearAll()

		elif not self.bound:
			print "[-] Drone not bound yet"

	def set_debugging(self,val):
		if val==True:
			self.write_command('d',1)
			self.debugging=True
		elif val==False:
			self.debugging=False
			self.write_command('d',0)

	def log(self,a):
		try:

			self.logger = open("log","a+")
			self.logger.write(str(int(time.time()-self.started_at)))
			self.logger.write(" : "+str(a))
			self.logger.write('\n')
			self.logger.close()
		except:
			pass


	def UdpDeamon(self):#server

		UDP_IP = "0.0.0.0"
		UDP_PORT = 1337

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

		self.sock.bind((UDP_IP, UDP_PORT))
		print'[-] Udp Deamon started...'
		self.sock.settimeout(3)
		conected=False
		while not conected and not self.kill_deamons:
			try:
				#self.log("UDP Deamon Running.. waiting")
				data, self.addr = self.sock.recvfrom(1024)
				loc='Conected from %s:%s'%(self.addr[0],self.addr[1])
				print'[-]',loc
				self.sock.sendto('me-?-?-'+loc,self.addr)
				conected=True
			except:
				pass
		prev_command=0
		last_keep_alive_pkt=time.time()
		while not self.kill_deamons: 
			try:
				data, self.addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
				try:

					if data.split("-")[0]=='me':

						command = data.split("-")[1]

						if command!=prev_command:
							cmd=self.commander[command]
							if type(cmd).__name__ == 'instancemethod':
								cmd()
							else:
								cmd[0](cmd[1])
							prev_command=command

						self.sock.sendto(data,self.addr)

					else:
						loc='New connection from %s:%s'%(self.addr[0],self.addr[1])
						print loc
						self.sock.sendto('me-?-?-'+loc,self.addr)
					last_keep_alive_pkt=time.time()
				except:
					print '[-] Error while sending Ack to udp client at',self.addr 
			except socket.timeout as tm:
				if (time.time()-last_keep_alive_pkt)>self.udp_client_lost:
					self.quit()
					print '[-] Udp client lost...quiting'
					self.log("Udp client lost...quiting")
					self.log("Last udp keepalive received at:"+str(time.time()-last_keep_alive_pkt)+" seconds ago")
				pass
		print ("[-] UDP Deamon got killed !!!")
		self.log("UDP deamon killed")
		self.r.close()
		self.r2.close()

	def throtlesDeamon(self):

		while not self.kill_deamons:

			self.newThrotleAvailable.wait()

			self.newThrotleAvailable.clear()

			command = self.updatedThrotle

			if self.debugging==False:
					try:
						self.sock.sendto("me-?-?-P:%3s R:%3s Y:%3s T:%3s"%(self.prev_command_val['p'],self.prev_command_val['r'],self.prev_command_val['y'],self.prev_command_val['t']),self.addr)
					except:
						pass
			value = self.prev_command_val[command]
			try:
				self.ser.write(bytearray([command,value]))
			except:
				print'[-] Unable to send command(',command,':',value,')via serial'
		else:
			"[-] Killed throtlesDeamon"
			self.log("Killed throtlesDeamon")

