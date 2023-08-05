import datetime

from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich import box, print as rich_print

COLOR_GREEN = "light_green"
COLOR_GRAY = "gray70"
NEWLINE = "\n"

def format_day(date): 
    _, _, day = date.split('-')
    return day

def format_to_date(date_str):
    datum, hours = date_str.split('T')
    year, month, day = datum.split('-')
    hours_template, _ = hours.split('-')
    hour, minute, second = hours_template.split('.')[0].split(':')
    date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return date

def format_to_hours(date_str):
    _, hours = date_str.split('T')
    hours_template, _ = hours.split('-')
    hour, minute, seconds = hours_template.split('.')[0].split(':')
    return f"{hour}:{minute}:{seconds}"

def trunc_numbers(number): 
    return "R$ " + str("{:.2f}".format(number))

def match_project(project_id, projects): 
    return next((project for project in projects if str(project["id"]) == str(project_id)), None)

def printTasks(tasks_tuple, projects): 
    table = Table(
        title="Month Tasks",
        box=box.DOUBLE_EDGE,
        title_style="white bold",
        caption_style=COLOR_GRAY,
        border_style=COLOR_GRAY,
    )

    table.add_column("Day", style=COLOR_GREEN)
    table.add_column("Project", style=COLOR_GREEN)
    table.add_column("Description", style=COLOR_GRAY)
    table.add_column("Start", style=COLOR_GRAY)
    table.add_column("End", style=COLOR_GRAY)
    table.add_column("Duration")
    table.add_column("Cost (R$)")
    
    wage = 0

    for date, tasks in tasks_tuple:
        for task in tasks["tasks"]: 
            start = task['start']
            end = task['end']
            duration = format_to_date(end) - format_to_date(start)
            project = match_project(task['project_id'], projects)
            table.add_row(
                format_day(date),
                f"[{project['tag_color']}]{project['name']}",
                task['description'],
                format_to_hours(task['start']),
                format_to_hours(task['end']),
                str(duration),
                f"[light_green]{trunc_numbers(task['cost'])}"
            )
            wage = wage + task['cost']
    table.add_row(
        "",
        "",
        "",
        "",
        "",
        "[green]Total:",
        f"[green]{trunc_numbers(wage)}"
    )
    return table

def convert_seconds_to_hours(seconds): 
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02i:%02i:%02i" % (h, m, s)

def has_sent_nfe(invoice): 
    if invoice['id'] == None:
        return "[red]:heavy_check_mark:"
    return f"[{COLOR_GREEN}]:heavy_check_mark:"

def print_reports(reports): 
    table = Table(
        title="Reports",
        box=box.DOUBLE_EDGE,
        title_style="white bold",
        caption_style=COLOR_GRAY,
        border_style=COLOR_GRAY,
    )

    table.add_column("Month", style=COLOR_GREEN)
    table.add_column("Total Hours", style=COLOR_GRAY)
    table.add_column("Hour Value", style=COLOR_GRAY)
    table.add_column("Sub Total", style=COLOR_GRAY)
    table.add_column("Discount", style=COLOR_GRAY)
    table.add_column("Final Value", style=COLOR_GRAY)
    table.add_column("NF-e")

    current_month = len(reports)
    for report in reports:
        sub_total = report['duration'] / 1000 / 60 / 60 * report['hour_value']
        table.add_row(
            f"{current_month}",
            convert_seconds_to_hours(report['duration'] / 1000),
            trunc_numbers(report['hour_value']),
            trunc_numbers(sub_total),
            trunc_numbers(report['current_discount']),
            trunc_numbers(sub_total - report['current_discount']),
            has_sent_nfe(report['invoice'])

        )
        current_month = current_month - 1

    return table