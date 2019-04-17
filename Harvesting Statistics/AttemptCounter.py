import pandas as pd
import datetime

df = pd.read_csv('AttemptData.csv')
dfProblemAttributes = pd.read_csv('ProblemAttributes.csv')
attemptsColumns = ['Student', 'Set', 'FileName','ProblemNumber', 'NumOfAttempts','MaxScore','HasGivenUp'];
dfAttempts = pd.DataFrame(columns = attemptsColumns)

startTime = datetime.datetime.now()
dfSize = len(df.index)

for index, row in df.iterrows():
	set = row['Set']
	student = row['Student']
	num = row['ProblemNumber']
	problem = row['FileName']

	dfTemp = df.loc[(df.Student == student) & (df.Set == set) & (df.ProblemNumber == num)]

	numAttempts = len(dfTemp.index)

	if numAttempts > 0:
		df = df.drop(list(dfTemp.index.values))
		maxScore = dfTemp.loc[dfTemp['Score'].idxmax()]['Score']

		gaveUp = 1 if maxScore < 1 else 0

		dfAttemptsRow = pd.DataFrame([[student, set, problem, num, numAttempts,maxScore, gaveUp]], columns = attemptsColumns)
		dfAttempts = dfAttempts.append(dfAttemptsRow, ignore_index=True)

	if (index%10 == 0) and (index != 0):
		elapsed = datetime.datetime.now() - startTime
		remaining = elapsed / index * (dfSize - index)
		print(str(index) +" rows processed; Elapsed: " + str(elapsed) + "; Remaining: " + str(remaining), end = "\r" )

dfAttempts.to_csv('AttemptCount.csv', index = False)
