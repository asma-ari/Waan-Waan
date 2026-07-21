from datetime import date, timedelta
from typing import List

THAI_WEEKDAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]

def thai_weekday(d: date) -> str:
    return THAI_WEEKDAYS[d.weekday()]

def is_due(start_date: date, interval_days: int, target_date: date, weekdays_str: str = "") -> bool:
    if target_date < start_date:
        return False
    
    # หากมีการระบุวันในสัปดาห์ (เช่น "2,4" สำหรับ พุธ, ศุกร์)
    if weekdays_str and weekdays_str.strip():
        days_list = [int(w.strip()) for w in weekdays_str.split(",") if w.strip().isdigit()]
        return target_date.weekday() in days_list

    # หากเป็นการระบุแบบ ทุกๆ N วัน
    delta_days = (target_date - start_date).days
    return delta_days % interval_days == 0

def upcoming_due_dates(start_date: date, interval_days: int, from_date: date, count: int = 30, weekdays_str: str = "") -> List[date]:
    results = []
    curr = max(start_date, from_date)
    end_limit = curr + timedelta(days=365) # ค้นหาล่วงหน้าไม่เกิน 1 ปี
    
    while curr <= end_limit and len(results) < count:
        if is_due(start_date, interval_days, curr, weekdays_str):
            results.append(curr)
        curr += timedelta(days=1)
        
    return results
