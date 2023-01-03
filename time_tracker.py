import json
import time
import pyautogui
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import List, Union

PROJECT_NAME = "auto_time_tracker"

def log_format(record):
    # Remove initial part of the file path to spare space.
    # (only the last 2 names will be)
    # Ex.: module.file.klass_name.func -> klass_name.func
    record["name"] = ".".join(record["name"].split(".")[-2:])

    suffix = ""
    if record.get("extra", False):
        suffix = "{extra}"

    return (
        datetime.now().strftime("%d-%m-%Y %H:%M")
        + " | <level>{level}</level>"
        + " | <level>{message}</level>"
        + suffix
        + " | <green>{name}.{module}:{function}:{line}</green>"
        + "\n{exception}"
    )

# Reset logger (remove all added handlers).
logger.remove()
# Add handler with custom format and output
logger.add(f"{PROJECT_NAME}__debug.log", level="DEBUG", format=log_format)
logger.add(f"{PROJECT_NAME}__general.log", level="INFO", format=log_format)

class TimeEntry:
    def __init__(
        self,
        identifier: int,
        start_datetime: Union[datetime, None] = None,
        end_datetime: Union[datetime, None] = None,
        time_in_seconds: int = 0,
        time_in_minutes: int = 0,
        time_in_hours: int = 0,
    ) -> None:
        self.__identifier = identifier
        self.__start_datetime = start_datetime
        self.__end_datetime = end_datetime
        self.__time_in_seconds = time_in_seconds
        self.__time_in_minutes = time_in_minutes
        self.__time_in_hours = time_in_hours

    def __repr__(self) -> str:
        return f"<TimeEntry: {self.__identifier}>"

    @property
    def identifier(self) -> int:
        return self.__identifier

    @property
    def start_datetime(self) -> Union[datetime, None]:
        return self.__start_datetime

    @start_datetime.setter
    def start_datetime(self, start_datetime: datetime) -> datetime:
        self.__start_datetime = start_datetime
        return self.__start_datetime

    @property
    def end_datetime(self) -> Union[datetime, None]:
        return self.__end_datetime

    @end_datetime.setter
    def end_datetime(self, end_datetime: datetime) -> datetime:
        self.__end_datetime = end_datetime
        return self.__end_datetime

    @property
    def time_in_seconds(self) -> int:
        return self.__time_in_seconds

    @time_in_seconds.setter
    def time_in_seconds(self, time_in_seconds: int) -> int:
        self.__time_in_seconds = time_in_seconds
        return self.__time_in_seconds

    @property
    def time_in_minutes(self) -> int:
        return self.__time_in_minutes

    @time_in_minutes.setter
    def time_in_minutes(self, time_in_minutes: int) -> int:
        self.__time_in_minutes = time_in_minutes
        return self.__time_in_minutes

    @property
    def time_in_hours(self) -> int:
        return self.__time_in_hours

    @time_in_hours.setter
    def time_in_hours(self, time_in_hours: int) -> int:
        self.__time_in_hours = time_in_hours
        return self.__time_in_hours

    def serialize(self) -> dict:
        return {
            "identifier": self.identifier,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "time_in_seconds": self.time_in_seconds,
            "time_in_minutes": self.time_in_minutes,
            "time_in_hours": self.time_in_hours,
        }

class Project:
    def __init__(
        self,
        name: str,
        total_time_in_seconds: int = 0,
        total_time_in_minutes: int = 0,
        total_time_in_hours: int = 0,
        total_time_in_days: int = 0,
        time_entries: List[dict] = []
    ) -> None:
        self.name = name
        self.__total_time_in_seconds = total_time_in_seconds
        self.__total_time_in_minutes = total_time_in_minutes
        self.__total_time_in_hours = total_time_in_hours
        self.__total_time_in_days = total_time_in_days
        self.__time_entries = self.parse_historical_time_entries(time_entries)

    def __repr__(self) -> str:
        return f"<Project: {self.name}>"

    def parse_historical_time_entries(self, time_entries: List) -> List[TimeEntry]:
        time_entries_list = []
        for time_entry in time_entries:
            time_entries_list.append(TimeEntry(**time_entry))
        return time_entries_list

    @property
    def total_time_in_seconds(self) -> int:
        return self.__total_time_in_seconds

    @total_time_in_seconds.setter
    def total_time_in_seconds(self, total_time_in_seconds: int) -> int:
        self.__total_time_in_seconds = total_time_in_seconds
        return self.__total_time_in_seconds

    @property
    def total_time_in_minutes(self) -> int:
        return self.__total_time_in_minutes

    @total_time_in_minutes.setter
    def total_time_in_minutes(self, total_time_in_minutes: int) -> int:
        self.__total_time_in_minutes = total_time_in_minutes
        return self.__total_time_in_minutes

    @property
    def total_time_in_hours(self) -> int:
        return self.__total_time_in_hours

    @total_time_in_hours.setter
    def total_time_in_hours(self, total_time_in_hours: int) -> int:
        self.__total_time_in_hours = total_time_in_hours
        return self.__total_time_in_hours

    @property
    def total_time_in_days(self) -> int:
        return self.__total_time_in_days

    @property
    def time_entries(self) -> List[TimeEntry]:
        return self.__time_entries

    def get_serialized_time_entries(self) -> List[dict]:
        return [time_entry.serialize() for time_entry in self.__time_entries]

    def start_tracking(self) -> None:
        if self.time_entries:
            identifier = self.time_entries[len(self.time_entries) - 1].identifier + 1
        else:
            identifier = 0
        self.__current_time_entry = TimeEntry(identifier=identifier)
        self.__current_time_entry.start_datetime = datetime.now()

    def stop_tracking(self) -> None:
        self.__current_time_entry.end_datetime = datetime.now()
        self.__time_entries.append(self.__current_time_entry)

    def generate_json_report(self) -> dict:
        return {
            "total_time_in_seconds": self.total_time_in_seconds,
            "total_time_in_minutes": self.total_time_in_minutes,
            "total_time_in_hours": self.total_time_in_hours,
            "total_time_in_days": self.total_time_in_days,
            "time_entries": self.get_serialized_time_entries(),
        }

def get_or_create_history_file() -> Path:
    file = (Path.cwd() / f"./{PROJECT_NAME}_history.json")
    if file.exists():
        return file
    else:
        with open(file, 'w') as f:
            f.write('{}')
        return file

def get_history() -> dict:
    with open(get_or_create_history_file(), "r") as file:
        history = json.load(file)
    return history

def get_project_in_history(project_name: str) -> dict:
    history = get_history()
    for key, value in history.items():
        if key == project_name:
            return value
    return {}

def update_report_in_history_file(project: Project) -> None:
    history = get_history()
    report = project.generate_json_report()
    history.update({project.name: report})

    with open(get_or_create_history_file(), "w") as file:
        file.write(json.dumps(history, indent=4, default=str))

def get_active_window():
    all_windows = pyautogui.getAllWindows()
    for window in all_windows:
        if window.isActive:
            return window

def stop_tracking_and_report(project: Project) -> None:
    project.stop_tracking()
    update_report_in_history_file(project)
    logger.info(f"Stop Tracking {project}")

def start_tracking_project(project_name: str) -> Project:
    project_history = get_project_in_history(project_name)

    project = Project(name=project_name, **project_history)
    logger.info(f"Start Tracking {project}")

    project.start_tracking()
    return project

def main():
    last_project_worked: Union[Project, None] = None
    try:
        while True:
            time.sleep(1)
            active_window = get_active_window()

            if active_window and "Visual Studio Code" in active_window.title:
                splited_window_title = active_window.title.split(" - ")
                if len(splited_window_title) <= 1:
                    logger.debug(f"Couldn't find the project name (splited window title: {splited_window_title})")
                    continue
                current_project_name = splited_window_title[1]
                if last_project_worked == None or current_project_name != last_project_worked.name:
                    if last_project_worked != None:
                        stop_tracking_and_report(last_project_worked)

                    project = start_tracking_project(current_project_name)
                    last_project_worked = project
                else:
                    logger.debug(f"Still workin on {last_project_worked}")
    except KeyboardInterrupt:
        if last_project_worked != None:
            stop_tracking_and_report(last_project_worked)

        logger.info(f"Tracking Finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.opt(exception=exc).critical("Fail at execution")
