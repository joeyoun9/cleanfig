import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as tk
import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot
from matplotlib import rc,rcParams
#from pylab import *
import math
from datetime import tzinfo,timedelta,date,datetime
from . import timezones as tz

def epoch2mplDate(ep):
	return md.epoch2num(ep)

def figure():
	rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
	rc('text',usetex=True)
	return plt.figure()

def init_axis(rows,cols,i,twin=False):
	# this creates axes with the axes artist loaded
	ax = host_subplot(rows,cols,i)#,axes_class=AA.Axes)
	if twin:
		# the twin axis will create a second X and Y axis on the top and the left!
		return ax,ax.twin()
	else:
		return ax
def init_axis_gs (plt,gs,twin=False,sharex=False):
	if not sharex:
		ax = host_subplot(gs,axes_class=AA.Axes)
	else:
		ax = host_subplot(gs,axes_class=AA.Axes,sharex=sharex)
	if twin:
		return ax,ax.twin()
	else:
		return ax
# a new way to deal with times, simply use epoch times, and figure it out from there
major_scale = {
	0      : .5,
        6      : 1,
	12     : 3,
	48     : 12,
	300	: 24,
	525     : 48
	}
# FIXME - at greater than 525 hours, there is no guarantee of encountering 12/0UTC
minor_scale = {
	0     : (1./60.),
	3     : .5,
	12     : 1,
	72     : 3
	}
sub_major_scale = {
	0.     : 0,
	0.5    : 0,
	1.0     : (1./3.),
	2.0     :  1,
	6.0     :  3,
        11.0    :  6,
        24.0    :  6,
	48	:  12,
	118	:  24
   
}
""" the tt functions allow you to call a tiemzone specific function, without having to import tzinfo"""
def ttUTC(ax,xy,begin,end,ms=major_scale,mns=minor_scale):
	timeticks(ax,xy,tz.utcTZ(),begin,end,days=True,major_scale=ms,minor_scale=mns)

def ttMST(ax,xy,begin,end,ms=major_scale,mns=minor_scale):
	timeticks(ax,xy,tz.mstTZ(),begin,end,major_scale=ms,minor_scale=mns)


def timeticks(ax,xy,tzone,begin,end,days=False,major_scale=major_scale,minor_scale=minor_scale):
	"""
		
	"""
	# determine the epoch values of time ticks in UTC, and then their lables
	# remember to label the date if a new day! #FIXME - only accepts hours
	epochs = []
	labels = []
	minis = []
	# start by calculating the ticks, ie, how far apart each one is!
	duration = (end - begin) / 3600. # duration in hours
	scale = major_scale
	# now find the value that is greater than duration, but less than the next one
	major_ticks = False
	minor_ticks = False
	smj_ticks = False
	for key in scale.keys():
		if key < duration:
			major_ticks = scale[key]
	# find sub-major ticks wich are major ticks, but without any labels.
	global sub_major_scale
	keys = sub_major_scale.keys()
	keys.sort()
	for key in keys:
		if key < major_ticks:
			smj_ticks = sub_major_scale[key]
	# now do the same for minor ticks
	for key in minor_scale.keys():
		if key < duration:
			minor_ticks = minor_scale[key]

	# begin is epoch time value, find the next occuring 0, 3, 6, 9, 12, 15, 18 or 21 hour
	time = begin
	if major_ticks >= 0.5:
		bhr = datetime.fromtimestamp(begin,tz=tzone).hour
		while bhr % major_ticks != 0:
			bhr += 1.
			time += 3600.

	# repeat for minor axis ticks
	time_minor = begin
	if minor_ticks > 0.5:
		bhr = datetime.fromtimestamp(begin,tz=tzone).hour
		while bhr % minor_ticks != 0:
			bhr += 1.
			time_minor += 3600.

	# now time is the epoch time of the starting hour, 
	# use the duration to determine how far between major/minor ticks should be
	# define the epochs and labels lists using the major_ticks as the spacing
	while time <= end:  ## Put ticks everywhere, including at the ends if they are good.
		#WRONG - if beginning plot!!# time should start at the first 0/3/6/9/etc - however, skip the first one if it is also the beginning
		#if time == begin:
		#	time += major_ticks * 3600
		#	continue
		# cool, now create ticks
		epochs.append(time)
		dt = datetime.fromtimestamp(time,tz=tzone)
		if (dt.hour == 0 or dt.hour == 12) and days and time != begin and time != end:
			# don't plot the date at the beginning or end, it looks tacky...
			# DETERMINE IF LaTeX is active/available, if not, then do a longer string
			if rcParams['text.usetex']:
				label = dt.strftime(r'%H:%M%\\%d %b %Y')
			elif major_ticks >=24:
				label = dt.strftime(r'%d %b')
			else:
				label= dt.strftime(r'%H:%M') # for now...
		else:
			if major_ticks >= 24:
				label = dt.strftime(r'%d %b')
			else:
				label = dt.strftime(r'%H:%M')
		labels.append(label)
		# now to add the sub-major ticks! These for now are automatic based on the current major ticks
		if smj_ticks > 0.:
			smjkey = time+smj_ticks*3600.
			while smjkey < time + major_ticks*3600.:
				epochs.append(smjkey)
				labels.append('') # append a blank label
				smjkey += smj_ticks*3600.

		time += major_ticks * 3600.
	#now for minor ticks!
	while time_minor <= end:
		minis.append(time_minor)
		time_minor += minor_ticks * 3600.
	customTick(ax,xy,epochs,labels,minis)

# now to define ticks!!!
def tick(axis,interval,minor=False):
	fmt = tk.FormatStrFormatter('%i')
	loc = tk.MultipleLocator(base=interval)
	# now set!
	axis.set_major_formatter(fmt)
	axis.set_major_locator(loc)
	if minor:
		minor = tk.MultipleLocator(base=minor)
		axis.set_minor_locator(minor)



def customTick(ax,xy, vals, labels, minor=False):
	if xy == 'x':
		ax.set_xticks(vals)
		ax.set_xticklabels(labels)
		if minor:
			ax.set_xticks(minor,minor=True)
	else:
		ax.set_yticks(vals)
		ax.set_yticklabels(labels)
		if minor:
			ax.set_yticks(minor,minor=True)

def label_x(ax,label):
	ax.set_xlabel(label)

def label_y(ax,label):
	ax.set_ylabel(label)


# colorbar!!!
def colbar_ceilometer(fig,data):
	fig.colorbar(data,**{
		'orientation':'horizontal',
		'fraction':0.04,
		'pad':0.1,
		'format':tk.FormatStrFormatter(r"%1.1f\linebreak$\displaystyle m^{-1}sr^{-1}$"),
		'aspect':40,
		'drawedges':False
	})

def fig_size(fig,x,y):
	fig.set_size_inches(x,y)

def ep2num(num):
	return num

