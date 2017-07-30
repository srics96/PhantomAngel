from django.conf.urls import include
from django.conf.urls import url

from PGE.views import add_employee, add_tasks, get_channels, get_employees, get_project_employees, handle_message, list_links, submit_link_data

urlpatterns = [
	url(r'^submitTasks', add_tasks, name = "add_tasks"),
	url(r'^submitMessage', handle_message, name="handle_message"),
	url(r'^submitLinkData', submit_link_data, name="submit_link_data"),
	url(r'^addEmployee', add_employee, name="add_employee"),
	url(r'^getEmployees/(?P<role>[A-Z]+)', get_employees, name="get_employees"),
	url(r'^getChannels/(?P<email>[^@]+@[^@]+\.[^@]+)', get_channels, name="get_channels"),
	url(r'^getProjectEmployees/(?P<channel_name>[A-Za-z]+)', get_project_employees, name="get_project_employees"),
	url(r'^listLinks/(?P<channel_name>[A-Za-z]+)', list_links, name="list_links"),
] 