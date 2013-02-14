import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as tk
import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot
from matplotlib import rc, rcParams
import math
from datetime import tzinfo, timedelta, date, datetime
from . import timezones as tz

def epoch2mplDate(ep):
	return md.epoch2num(ep)

def figure():
	rc('font', **{'family':'sans-serif', 'sans-serif':['Helvetica']})
	rc('text', usetex=True)
	return plt.figure()

def init_axis(rows, cols, i, twin=False):
	# this creates axes with the axes artist loaded
	ax = host_subplot(rows, cols, i)  # ,axes_class=AA.Axes)
	if twin:
		# the twin axis will create a second X and Y axis on the top and the left!
		return ax, ax.twin()
	else:
		return ax
def init_axis_gs (plt, gs, twin=False, sharex=False):
	if not sharex:
		ax = host_subplot(gs, axes_class=AA.Axes)
	else:
		ax = host_subplot(gs, axes_class=AA.Axes, sharex=sharex)
	if twin:
		return ax, ax.twin()
	else:
		return ax

""" the tt functions allow you to call a tiemzone specific function, without having to import tzinfo"""
def ttUTC(begin, end=False, **kwargs):
	tt(begin, end, tz.utcTZ(), **kwargs)

def ttMST(begin, end=False, **kwargs):
	tt(begin, end, tz.mstTZ(), **kwargs)

def tt(begin, end=False, userTZ=tz.utcTZ(), ax=plt.gca(), xy='x', major_count=5., minor_count=6., nodates=False, plt=False, **kwargs):
	'''
	create time ticks
	'''
	if not end:
		'we can accept simply a list of times, and take the first and last values'
		end = begin[-1]
		begin = begin[0]
	'determine the gaps'
	duration = float(end - begin)
	dt = duration / (major_count - 1.)
	'So, figure out where this is closest to'

	def alg(dt):
		'a simple algorithm to determine how much to add'
		if dt < 3 * 3600:
			'1,2,3'
			return 3600
		elif dt < 18 * 3600:
			'6,9,12,15,18'
			return 3 * 3600
		elif dt < 36 * 3600:
			'24,30,36'
			return 6 * 3600
		else:
			return 12 * 3600
			'48,60,72,84,96,...'

	if dt < 3600:
		'''
		if to make major_count-1 segments is less than an hour, then simply
		make major_count segments.
		'''
		dt = duration / major_count
	else:
		count = 100.
		dt = 3600
		while count > major_count:
			dt += alg(dt)
			count = duration / dt
	'Not perfect, but it will do for now...'
	minor_dt = dt / minor_count
	'''
	I could add more logic to this computation, but I cannot figure out a good
	way to actually make anything better.
	'''

	'now find the ticks'
	'determine if the date should be shown or not'
	st = datetime.fromtimestamp(begin, tz=userTZ)
	en = datetime.fromtimestamp(end, tz=userTZ)
	incl_dates = False
	if duration > 86400 or not  st.day == en.day: incl_dates = True

	'''
	Determine tick beginning time. The logic here will be that
	if there is a whole hour within 1/3 of a dt range, then start there
	'''
	start = begin
	shift_st = datetime.fromtimestamp(begin + dt / 3, tz=userTZ)
	if not shift_st.hour == st.hour:
		'We have determined that within the first third of a bin, there is an hour change'
		'shift this thing to the next full hour'
		if st.minute > 0:
			start += (59 - st.minute) * 60 + 60 - st.second
		'THEN! if dt is > 9 hours, then find the nearest multiple of 3'
		if dt > 9 * 3600:
			shift_st = datetime.fromtimestamp(start, tz=userTZ)
			while not shift_st.hour % 3 == 0:
				start += 3600
				shift_st = datetime.fromtimestamp(start, tz=userTZ)


	t = start
	times = []
	texts = []

	'make major ticks'
	while t <= end + dt:
		times.append(t)
		'''
		logic for dates
		if there is more than one day in the period, then include the date
		'''
		dtobj = datetime.fromtimestamp(t, tz=userTZ)
		t += dt
		if incl_dates and not nodates:
			texts.append(dtobj.strftime('%H:%M\n%d %b %Y'))
		else:
			texts.append(dtobj.strftime('%H:%M'))
	print 'This many time ticks were made: ', len(times)
	'make minor ticks'
	t = start - dt
	minor_times = []
	while t < end + dt:
		minor_times.append(t)
		t += minor_dt
	'and draw the actual ticks'
	if plt:
		'if a plt key is passed, then that supercedes the ax key passed.'
		ax = plt.gca()
	customTick(ax, xy, times, texts, minor=minor_times)
	if xy == 'x':
		ax.set_xlim((begin, end))
		ax.set_xlabel('Time (' + userTZ.tzname(False) + ')')


def tick(axis, interval, minor=False):
	fmt = tk.FormatStrFormatter('%i')
	loc = tk.MultipleLocator(base=interval)
	# now set!
	axis.set_major_formatter(fmt)
	axis.set_major_locator(loc)
	if minor:
		minor = tk.MultipleLocator(base=minor)
		axis.set_minor_locator(minor)

def no_ticks(plt, xy='x'):
	if xy == 'x':
		plt.gca().get_xaxis().set_ticks([])
	else:
		plt.gca().get_yaxis().set_ticks([])
	'NOTE, this may not remove labels...'

def customTick(ax, xy, vals, labels, minor=False):
	if xy == 'x':
		ax.set_xticks(vals)
		ax.set_xticklabels(labels)
		if minor:
			ax.set_xticks(minor, minor=True)
	else:
		ax.set_yticks(vals)
		ax.set_yticklabels(labels)
		if minor:
			ax.set_yticks(minor, minor=True)

def label_x(ax, label):
	ax.set_xlabel(label)

def label_y(ax, label):
	ax.set_ylabel(label)


# colorbar!!!
def colbar_ceilometer(fig, data):
	fig.colorbar(data, **{
		'orientation':'horizontal',
		'fraction':0.04,
		'pad':0.1,
		'format':tk.FormatStrFormatter(r"%1.1f\linebreak$\displaystyle m^{-1}sr^{-1}$"),
		'aspect':40,
		'drawedges':False
	})

def fig_size(fig, x, y):
	fig.set_size_inches(x, y)

def ep2num(num):
	return num

