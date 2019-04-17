import pandas as pd
import datetime

df = pd.read_csv('WWLogRaw.csv')
dfProblemAttributes = pd.read_csv('ProblemAttributes.csv')
dfHW = pd.read_csv('HWDates.csv')

startTime = datetime.datetime.now()
dfSize = len(df.index)

for index, row in df.iterrows():
	date = row['Date']
	set = row['Set']
	num = row['ProblemNumber']
	student = row['Student']
	dfTemp = dfHW.loc[(set == dfHW.Set)]
	if len(dfTemp.index) == 0:
		df = df.drop(index)
	else:
		setDates = dfTemp.iloc[0]
		if date > setDates['CloseDate']:
			try:
				df = df.drop(index)
			except:
				pass
		else: 
			dfProblem = dfProblemAttributes.loc[(dfProblemAttributes.ProblemNumber == num) & (dfProblemAttributes.Set == set)]
			if len(dfProblem.index) == 0:
				df = df.drop(index)
				continue
			else:
				fileName = dfProblem.FileName.iloc[0]
				df.at[index, 'FileName'] = fileName

			if row['Score'] >= 1:
				toDelete = df.loc[(df.Student == student) & (df.Set == set) & (df.ProblemNumber == num) & (df.Date > date)]
				if len(toDelete.index) != 0: 
					df = df.drop(list(toDelete.index.values))
			

	if (index%10 == 0) and (index != 0):
		elapsed = datetime.datetime.now() - startTime
		remaining = elapsed / index * (dfSize - index)
		print(str(index) +" rows processed; Elapsed: " + str(elapsed) + "; Remaining: " + str(remaining), end = "\r" )

df = df.dropna()

df.to_csv('AttemptData.csv', index = False)

