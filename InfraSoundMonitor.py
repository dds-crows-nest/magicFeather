#---------------------------ooo0ooo---------------------------
#       Seismic Monitoring Software
#       Ian Robinson
#       starfishprime.co.uk
#
#---------------------------Notes---------------------------
#
#		last update 22/8/21
#
#---------------------------ooo0ooo---------------------------

import gc
import os
import time
import smbus



from threading import Thread
import numpy as np
from obspy import UTCDateTime, read, Trace, Stream
from obspy.signal.filter import bandpass, lowpass, highpass
from shutil import copyfile
import copy

import matplotlib
matplotlib.use('Agg') #prevent use of Xwindows
from matplotlib import pyplot as plt



#---------------------------ooo0ooo---------------------------
def read_pressure_from_sensor():
	#this function specifically reads data over i2c from a 
	#DLVRF50D1NDCNI3F Amphenol mems differential pressure sensor 
	
	# this routine will need to be changed for a diffent input device
	#such as a voltage via an a/d convertor
	# note: the return value 'pressure' is a floting point number
	
    raw_data = bytearray
    z=bytearray
    raw_pressure= int
    raw_data=[]

    z = [0,0,0,0]
    z = sensor.read_i2c_block_data(addr, 0, 4) #offset 0, 4 bytes

    d_masked = (z[0] & 0x3F)
    raw_data = (d_masked<<8) +  z[1]    

    raw_pressure= int(raw_data)
    pressure = (((raw_pressure-8192.0)/16384.0)*250.0 *1.25)
    
    return pressure

#---------------------------ooo0ooo---------------------------
def save_hourly_data_as_mseed(st):
	
	start_date_time=st[0].stats.starttime

	year = str(start_date_time.year)
	month = str(start_date_time.month)
	day = str(start_date_time.day)
	hour = str(start_date_time.hour)
	
	save_dir=  'Data' + '/' + year + '/' + month+ '/' + day
	filename = hour + '.mseed'
  
#----------create data Directory Structure if not already present  
	here = os.path.dirname(os.path.realpath(__file__))
	

	try:
		os.makedirs('Data/'+year+'/')
	except OSError:
		if not os.path.isdir('Data/'+year+'/'):
			raise
 
	try:
		os.makedirs('Data/'+year+'/'+month+'/')
	except OSError:
		if not os.path.isdir('Data/'+year+'/'+month+'/'):
			raise

	try:
		os.makedirs('Data/'+year+'/'+month+'/'+day+'/')
	except OSError:
		if not os.path.isdir('Data/'+year+'/'+month+'/'+day+'/'):
			raise


	filepath = os.path.join(here, save_dir, filename)
  
	dataFile = open(filepath, 'wb')
	st.write(dataFile,format='MSEED', encoding=4, reclen=4096)
	dataFile.close()
	print ('Data write of last hours active data completed')

	return None
#---------------------------ooo0ooo---------------------------
def save_weekly_pwr_as_mseed(st):
	weekly_start_time= st[0].stats.starttime
	year = str(weekly_start_time.year)
	month = str(weekly_start_time.month)
	day = str(weekly_start_time.day)
	hour = str(weekly_start_time.hour)
	
	save_dir=  'Data' + '/' + year + '/' + month+ '/'
	filename = day + '_' + month +'_' + year + '_weekly_acoustic_pwr' + '.mseed'
  
#----------create data Directory Structure if not already present  
	here = os.path.dirname(os.path.realpath(__file__))
	

	try:
		os.makedirs('Data/'+year+'/')
	except OSError:
		if not os.path.isdir('Data/'+year+'/'):
			raise
 
	try:
		os.makedirs('Data/'+year+'/'+month+'/')
	except OSError:
		if not os.path.isdir('Data/'+year+'/'+month+'/'):
			raise



	filepath = os.path.join(here, save_dir, filename)
  
	dataFile = open(filepath, 'wb')
	st.write(dataFile,format='MSEED', encoding=4, reclen=4096)
	dataFile.close()
	print ('Data write of weely pwr data completed')
	
	return None
	
###---------------------------ooo0ooo---------------------------
def plot_daily_raw_pressures(st, frq_low_cut, frq_high_cut):
	#produces a 24hour obspy 'dayplot' saved in svg format.
	#two copies are produced Today.svg and 'date'.svg

	if (st[0].stats.npts > 1000):
		try:
			
			here = os.path.dirname(os.path.realpath(__file__))
			start_time = st[0].stats.starttime
			year = str(start_time.year)
			month = str(start_time.month)
			day = str(start_time.day)
			year_dir =  'Data' + '/' + year
			station_info= str(st[0].stats.station)+'-'+str(st[0].stats.channel)+'-'+str(st[0].stats.location)

			save_dir=  'Plots/' 
			date_string = str(year) + '_' + str(month) + '_' + str(day)
			plot_title= 'Raw Pressure ' +':::'+station_info+':::'+' '+date_string+'  '+str(frq_low_cut) + '-' + str(frq_high_cut) + ' Hz'
			filename1 = ('Plots/today_raw_pressure.svg')
			filename2 = 'Plots/' + date_string+'__'+station_info+'__Raw_Pressure.svg'
			
			st.plot(type="dayplot",outfile=filename1, title=plot_title, data_unit='$\Delta$Pa', interval=60, right_vertical_labels=False, one_tick_per_line=False, color=['k', 'r', 'b', 'g'], show_y_UTC_label=False)
			copyfile(filename1, filename2)
			plt.close('all')
			print ('Plotting of daily raw pressure completed')
		except (ValueError,IndexError):
			print('an  error on plotting dayly raw pressures!')
	
	return None

###---------------------------ooo0ooo---------------------------
def create_mseed(readings, start_time, end_time, n_samples, station_id, station_channel, location):

    true_sample_frequency = float(n_samples) / (end_time - start_time)

    # Fill header attributes
    stats = {'network': 'IR', 'station': station_id, 'location': location,
         'channel': station_channel, 'npts': n_samples, 'sampling_rate': true_sample_frequency,
         'mseed': {'dataquality': 'D'}}
    # set current time
    stats['starttime'] = start_time
    st = Stream([Trace(data=readings[0:n_samples], header=stats)])
    return st

###---------------------------ooo0ooo---------------------------
def plot_daily_pwr(st, frq_low_cut, frq_high_cut, dt):
	
	# this is specific to acoustic meaurements producing a plot of acoustic pwr
	# routine can be ignore more non-acoustic readings
	#produces a 24hour obspy 'dayplot' saved in svg format.
	#two copies are produced 

	
	if (st[0].stats.npts > 3000):
		try:
			here = os.path.dirname(os.path.realpath(__file__))
		
			start_time = st[0].stats.starttime
			year = str(start_time.year)
			month = str(start_time.month)
			day = str(start_time.day)
			year_dir =  'Data' + '/' + year
			
			station_info= str(st[0].stats.station)+'-'+str(st[0].stats.channel)+'-'+str(st[0].stats.location)
			tr = calc_running_mean_pwr(st, dt, frq_low_cut, frq_high_cut)
			save_dir=  'Plots/' 
			date_string = str(year) + '_' + str(month) + '_' + str(day)
			plot_title= 'acoustic_pwr ' +':::'+station_info+':::'+' '+date_string+'  '+str(frq_low_cut) + '-' + str(frq_high_cut) + ' Hz'
			filename1 = ('Plots/today_acoustic_pwr.svg')
			filename2 = 'Plots/' + date_string+'__'+station_info+'__acoustic_pwr.svg'
			tr.plot(type="dayplot",outfile=filename1, title=plot_title, data_unit='$Wm^{-2}$', interval=60, right_vertical_labels=False, 
			color=['k', 'r', 'b', 'g'], show_y_UTC_label=False)
			copyfile(filename1, filename2)
			plt.close('all')
			print ('Plotting of daily acoustic power completed')
		except (ValueError,IndexError):
			print('an error on plotting acoustic pwr!')
	return None
	

###---------------------------ooo0ooo---------------------------
def plot_weekly_accoustic_power(st):
	
	try:
		start_date_time=st[0].stats.starttime
		n_samples=st[0].stats.npts
		frq_sampling=st[0].stats.sampling_rate
	
		start_year = start_date_time.year
		start_month= start_date_time.month
		# start_day as day of month i.e  1, 2 ... 31 
		start_day= start_date_time.day
		# start day as numerical day of week i.e.  1 (Mon) to 7 (Sun)
		iso_start_day=start_date_time.isoweekday() 
		start_hour=start_date_time.hour
		start_minute=start_date_time.minute
	
		station_info= str(st[0].stats.station)+'-'+str(st[0].stats.channel)+'-'+str(st[0].stats.location)
		
		date_string = str(start_year) + '-' + str(start_month) + '-' + str(start_day)
		filename1 = ('Plots/weekly_acoustic_pwr.svg')
		filename2 = ('Plots/' + date_string + '_weekly_acoustic_pwr.svg')
	
	
	
		time_sampled = n_samples/frq_sampling  #length of data in seconds
		graph_start = float(iso_start_day-1) + (float(start_hour)/24) + float(start_minute/1440)
		graph_end = graph_start + (time_sampled/86400.0)
	
		z = UTCDateTime()
		updated= z.strftime("%A, %d. %B %Y %I:%M%p")
		date_string = str(start_year) + '-' + str(start_month) + '-' + str(start_day)
	
		weekly_acoustic_pwr=st[0].data
		y_values=weekly_acoustic_pwr[0:(n_samples-1)]
	
		x_values= np.linspace(graph_start, graph_end, len(y_values))
				
		fig = plt.figure(figsize=(12,4))
	
		xAxisText=("Time  updated - "+ updated +" UTC")
		plt.title('Acoustic Pwr - w/c - '+ date_string  +':::'+' '+station_info)
		plt.xlabel(xAxisText)
	
		plt.ylabel('$Wm^{-2}$')
	
		plt.plot(x_values, y_values,  marker='None',    color = 'darkolivegreen')  
		plt.xlim(0.0, 7.01)
	
		ticks=np.arange(0, 7, 1.0)
		labels = "Mon Tues Weds Thurs Fri Sat Sun".split()
		plt.xticks(ticks, labels)
		plt.grid(True)
		
		plt.savefig(filename1)
		copyfile(filename1, filename2)  
		plt.close('all')
		print ('Plotting of weekly acoustic power completed')
	
	except (ValueError,IndexError):
		print('an error on plotting weekly acoustic pwr!')

	return None



###---------------------------ooo0ooo---------------------------
def calc_running_mean_pwr(st, dt, frq_low_cut, frq_high_cut):
	#routine used to help plot acoustic pwr - can be ignored for non-acoustic
	#applications

    N=len(st[0].data)
    dt = st[0].stats.delta
    new_stream=st[0].copy()

    new_stream.filter('bandpass', freqmin=frq_low_cut, freqmax=frq_high_cut, corners=4, zerophase=True)
    x=new_stream.data
   
    x=x**2
    
    n_sample_points=int(dt/dt)
    running_mean=np.zeros((N-n_sample_points), np.float32)

    #determine first tranche
    temp_sum = 0.0
    
    for i in range(0,(n_sample_points-1)):
        temp_sum = temp_sum + x[i]

        running_mean[i]=temp_sum/n_sample_points

    #calc rest of the sums by subracting first value and adding new one from far end  
    for i in range(1,(N-(n_sample_points+1))):
            temp_sum = temp_sum - x[i-1] + x[i + n_sample_points]
            running_mean[i]=temp_sum/n_sample_points
    # calc averaged acoustic intensity as P^2/(density*c)
    running_mean=running_mean/(1.2*330)


    new_stream.data=running_mean
    new_stream.stats.npts=len(running_mean)

    return new_stream

###---------------------------ooo0ooo---------------------------
def calc_acoustic_pwr(tranche, dt, n_sample_points):
	
	tranche=tranche**2
	temp_sum = 0.0
	
	for i in range(0,(n_sample_points-1)):
		temp_sum=temp_sum+tranche[i]
	
	mean=temp_sum/n_sample_points
# calc averaged acoustic intensity as P^2/(density*c)
	acoustic_pwr=mean/(1.2*330)

	return acoustic_pwr


	
###---------------------------ooo0ooo---------------------------
def save_and_plot_all(daily_readings, hourly_readings, day_start_time, hourly_start_time, \
	n_daily_samples,n_hourly_samples, weekly_acoustic_pwr, n_weekly_samples, \
	week_start_date_time,station_id, station_channel,location, sample_end_time, dt):	
	


	#PlotAndSaveweekly_acoustic_pwr
	st=create_mseed(weekly_acoustic_pwr, week_start_date_time, sample_end_time, n_weekly_samples, station_id, station_channel, location)
	save_weekly_pwr_as_mseed(st)
	plot_weekly_accoustic_power(st)

	st = create_mseed(hourly_readings, hourly_start_time, sample_end_time, n_hourly_samples, station_id, station_channel, location)
	save_hourly_data_as_mseed(st)
	
	#create daily stream and plot
	st = create_mseed(daily_readings, day_start_time, sample_end_time, n_daily_samples, station_id, station_channel, location)
	st.filter('bandpass', freqmin=frq_low_cut, freqmax=frq_high_cut, corners=4, zerophase=True)
	plot_daily_raw_pressures(st, frq_low_cut, frq_high_cut)	
	plot_daily_pwr(st, frq_low_cut, frq_high_cut, dt)
	return None



###--------------------------Main Body--------------------------
###-                                                           -
###-                                                           -
###--------------------------+++++++++--------------------------

sensor = smbus.SMBus(1)    #used to communicate with i2c sensor
addr = 0x28				   # address of i2c sensor
#os.chdir('/home/pi/InfraSound')  #replace with home directory of application


# below are station parameters for your station. see SEED manual for
# more details http://www.fdsn.org/pdf/SEEDManual_V2.4.pdf

#-- station parameters
station_id= 'STARF'
# channel B=broadband 10-80Hz sampling, D=pressure sensor, F=infrasound
station_channel = 'BDF'  #see SEED format documentation
location = '01'  # 2 digit code to identify specific sensor rig
station_network='IR'

frq_sampling=40.00
n_seconds_in_sampling_period = 1.00/frq_sampling
seconds_in_day=3600*24

dt = 5.0  # time interval seconds to calculate running mean for acoustic pwr
frq_low_cut=0.01         # low cut-off frequency
frq_high_cut=10.0        # high cut-off frequency


#-----create top level Data and plots directories if not already present
here = os.path.dirname(os.path.realpath(__file__))

try:
	os.makedirs('Plots/')
except OSError:
	if not os.path.isdir('Plots/'):
		raise

try:
	os.makedirs('Data/')
except OSError:
	if not os.path.isdir('Data/'):
		raise


###---------------------------ooo0ooo---------------------------
# -- create numpy arrays to store pressure and time data
n_target_hourly_samples=int(frq_sampling*3600*1.1)
n_target_daily_samples=int(n_target_hourly_samples*24)

daily_readings=np.zeros(n_target_daily_samples, np.float32) 
hourly_readings=np.zeros(n_target_hourly_samples, np.float32)
n_daily_samples = 0
n_hourly_samples = 0


# -- create Numpy array to store week's acoustic pwr 
n_target_weekly_acoustic_pwr = int((608400*1.05)/dt)
weekly_acoustic_pwr=np.zeros([n_target_weekly_acoustic_pwr], dtype=np.float32)
n_weekly_samples=0


# -- create Numpy array to store temp data for most recent acoustic pwr 
n_target_recent_pwr_readings=int(dt*frq_sampling)
N=int(n_target_recent_pwr_readings*1.1)
acoustic_pwr_tranche=np.zeros(N, dtype=np.float32)
acoustic_pwr_head_pointer=0



week_start_date_time=UTCDateTime()
day_start_time=week_start_date_time #initialise variable
hourly_start_time=week_start_date_time
sample_end_time=week_start_date_time #initialise variable
last_save_time=week_start_date_time #initialise variable
last_acoustic_pwr_calc_time=week_start_date_time



while 1:
	
	time.sleep(n_seconds_in_sampling_period)
	
	try:
		temp_pressure=read_pressure_from_sensor()
		daily_readings[n_daily_samples] = temp_pressure
		hourly_readings[n_hourly_samples] = temp_pressure
		acoustic_pwr_tranche[acoustic_pwr_head_pointer]=temp_pressure
		n_daily_samples = n_daily_samples + 1
		n_hourly_samples = n_hourly_samples +1
		acoustic_pwr_head_pointer=acoustic_pwr_head_pointer+1
		
	except (IOError, IndexError):
		print('read error')
		daily_readings[n_daily_samples] = 0.00
		hourly_readings[n_hourly_samples] = 0.00
		n_daily_samples = n_daily_samples + 1
		n_hourly_samples = n_hourly_samples +1
        
	if((UTCDateTime() - last_acoustic_pwr_calc_time) > dt):
		#calculate acoustic pwr of last tranche
		acoustic_pwr=calc_acoustic_pwr(acoustic_pwr_tranche, dt, acoustic_pwr_head_pointer)
		weekly_acoustic_pwr[n_weekly_samples]=acoustic_pwr
		acoustic_pwr_tranche=np.zeros(N, dtype=np.float32)
		acoustic_pwr_head_pointer=0
		n_weekly_samples=n_weekly_samples+1
		last_acoustic_pwr_calc_time= UTCDateTime()
	
	if (UTCDateTime().hour != hourly_start_time.hour):
		sample_end_time=UTCDateTime()
		
		thread_plot_and_save = Thread(target=save_and_plot_all, args=(daily_readings, \
		hourly_readings, day_start_time, hourly_start_time, n_daily_samples,\
		n_hourly_samples, weekly_acoustic_pwr, \
		n_weekly_samples,week_start_date_time,station_id, \
		station_channel,location, sample_end_time, dt))


		thread_plot_and_save.start()

		hourly_start_time = UTCDateTime()
		hourly_readings=np.zeros(n_target_hourly_samples, np.float32) #reset data array to zero for new hour
		n_hourly_samples = 0
		
	if (day_start_time.day != UTCDateTime().day):
		sample_end_time=UTCDateTime()
		daily_readings=np.zeros(n_target_daily_samples, np.float32)  #reset data array to zero for new day
		day_start_time=UTCDateTime()
		n_daily_samples = 0

		if sample_end_time.isoweekday()==1: #Monday-- new week starts
			#clear theweekly data array
			weekly_acoustic_pwr=np.zeros([n_target_weekly_acoustic_pwr], dtype=np.float32)
			week_start_date_time=UTCDateTime()
			n_weekly_samples=0
