import json
import time
from typing import Union, Dict
import pyautogui

from loguru import logger
from datetime import datetime

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


class Project:
    def __init__(self, name: str, ):
        self._name = name
        self._start_datetime = None
        self._end_datetime = None

    def __repr__(self):
        return f"<VsCodeReport project: {self.name}>"

    @property
    def start_datetime(self):
        return self._start_datetime

    @property
    def end_datetime(self):
        return self._end_datetime

    @property
    def name(self):
        return self._name

    def start_tracking(self):
        self._start_datetime = datetime.now()

    def stop_tracking(self):
        self._end_datetime = datetime.now()

    def generate_json_report(self):
        return {
            self.name: {
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            },
        }


def create_or_update_report_in_history_file(project: Project):

    with open(get_or_create_history_file(), "r") as file:
        json_history = json.load(file)

    report = project.generate_json_report()

    if json_history.get(project.name):
        json_history[project.name] = {**report[project.name]}
    else:
        json_history.update(**report)

    with open(get_or_create_history_file(), "w") as file:
        file.write(json.dumps(json_history, indent=4, default=str))


def get_active_window() -> Union[str, None]:
    all_windows = pyautogui.getAllWindows()
    for window in all_windows:
        if window.isActive:
            return window

def stop_tracking_and_report(project: Project):
    project.stop_tracking()
    create_or_update_report_in_history_file(project)
    logger.info(f"Stop Tracking {project}")

def main():
    last_project_worked = None
    try:
        while True:
            time.sleep(1)
            active_window = get_active_window()

            if active_window and "Visual Studio Code" in active_window.title:
                current_project = active_window.title.split(" - ")[1]

                if last_project_worked == None or current_project != last_project_worked.name:
                    logger.info(f"Stop Tracking {last_project_worked}")
                    if last_project_worked != None:
                        stop_tracking_and_report(last_project_worked)

                    new_project = Project(current_project)
                    new_project.start_tracking()
                    last_project_worked = new_project
                    logger.info(f"Start Tracking {new_project}")
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
