from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.telemetry import Telemetry

async def getTelemetryJson(db: AsyncSession, user_id: str):
    jsonDic = {}

    # Query to fetch all telemetry data for the given user ID
    result = await db.execute(
        select(Telemetry).where(Telemetry.id == user_id)
    )
    # get all rows from that query
    # You can get the results in database by grabbing the indexes of rows
    # Example:
    # rows[0].battery_level
    # rows[0].cpu_temp
    rows = result.scalars().all()

    # TODO: implement logic to process rows and populate jsonDic
    jsonDic["cpuTemp"] = getCpuTemp(rows)

    # Return the dictionary
    return jsonDic

def getCpuTemp(rows: list):
    # return the cpuTempDic such that it stores current temp, past hour temps, and past 24 hours temps.
    cpuTempDic = {}
    # Get the current CPU temp
    curCpuTemp = rows[0].cpu_temp
    avgHourTemps = []
    avgHourTemps2 = []
    pastHourCpuTemps = []
    pastDayCpuTemps = []

    # Make sure to do rows[i-1] when getting row data
    for i in range(1, len(rows)+1):
        # If i is greater than 60 than we are past an hour of information
        if i > 60:
            continue
        # Get the past hour temps
        else:
            # average between last 5 minutes and append to pastHourCpuTemps
            if i % 5 == 0:
                avgHourTemps.append(rows[i-1].cpu_temp)
                avg = sum(avgHourTemps) / len(avgHourTemps)
                pastHourCpuTemps.append(avg)
                avgHourTemps.clear()
            else:
                avgHourTemps.append(rows[i-1].cpu_temp) 
        # If i is greater than 1440, than we've gone past 24 hours of data
        if i > 1440:
            break
        else:
            avgHourTemps2.append(rows[i-1].cpu_temp)
            if i % 60 == 0:
                avg = sum(avgHourTemps2) / len(avgHourTemps2)
                pastDayCpuTemps.append(avg)
                avgHourTemps2.clear()
    
    # append the data to the dictionary
    cpuTempDic["current"] = curCpuTemp
    cpuTempDic["pastHour"] = pastHourCpuTemps
    cpuTempDic["pastDay"] = pastDayCpuTemps

    # return the dictionary
    return cpuTempDic





