import pandas as pd
import datetime

df = pd.read_csv('AttemptData.csv')
dfHW = pd.read_csv('HWDates.csv')

startTime = datetime.datetime.now()
dfSize = len(df.index)

for index, row in df.iterrows():
	date = row['Date']
	dateValue =  pd.Timestamp(date).timestamp()
	set = row['Set']
	setDates = dfHW.loc[(set == dfHW.Set)].iloc[0]
	openDate = pd.Timestamp(setDates['OpenDate']).timestamp()
	closeDate = pd.Timestamp(setDates['CloseDate']).timestamp()
	norm = (dateValue-openDate)/(closeDate-openDate)
	
	df.at[index, 'NormalizedDates'] = norm
	df.at[index, 'DateOnly'] = pd.Timestamp(date).date()
	df.at[index, 'TimeOnly'] = (pd.Timestamp(date) - pd.Timestamp(str(pd.Timestamp(date).date()))).total_seconds()
	df.at[index, 'DayOfWeek'] = pd.Timestamp(date).day_name()

	if (index%100 == 0) and (index != 0):
		elapsed = datetime.datetime.now() - startTime
		remaining = elapsed / index * (dfSize - index)
		print(str(index) +" rows processed; Elapsed: " + str(elapsed) + "; Remaining: " + str(remaining), end = "\r" )

df.to_csv('AttemptData.csv', index = False)